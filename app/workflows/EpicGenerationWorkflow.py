import json
import os
import logging
from llama_index.core import PromptTemplate
from llama_index.core.workflow import Workflow, Context, step, StartEvent, StopEvent
from llama_index.core.workflow.retry_policy import ConstantDelayRetryPolicy
from app.events.EpicGenerationEvents import EpicGenerationEvent, EpicQualityAssuranceEvent, EpicQualityCriterionEvaluationEvent, EpicQualityImprovementEvent, EpicCritiquingEvent
from app.models.Epic import Epic
from app.models.QualityCriterionEvaluation import EnrichedQualityCriterionEvaluation, QualityCriterionEvaluation
from app.models.SuggestedCritiques import SuggestedCritiques
from app.prompts.EpicPrompts import EPIC_GENERATION_TEMPLATE, EPIC_REFINEMENT_TEMPLATE, EPIC_QUALITY_EVALUATION_TEMPLATE, EPIC_QUALITY_IMPROVEMENT_TEMPLATE, EPIC_CRITIQUE_SUGGESTION_TEMPLATE
from app.prompts.QualityCriteria import QUALITY_CRITERIA

class EpicGenerationWorkflow(Workflow):
    def __init__(self, llm, max_steps: int = 10, quality_assurance_enabled: bool = False, result_directory: str = ".", **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm = llm
        self.max_steps = max_steps
        self.quality_assurance_enabled = quality_assurance_enabled
        self.result_directory = result_directory

    @step(retry_policy=ConstantDelayRetryPolicy(delay=1, maximum_attempts=5))
    async def generate_epic(self, ctx: Context, ev: StartEvent | EpicGenerationEvent) -> EpicQualityAssuranceEvent | EpicCritiquingEvent:
        if type(ev) is StartEvent:
            await ctx.set("feature_description", ev.feature_description)
            await ctx.set("project_description", ev.project_description)
            project_description = ev.project_description
            # Generate the initial epic version
            self.logger.debug(f"Try to generate the epic for the feature description: '{ev.feature_description}'")
            generated_epic = self.llm.structured_predict(
                Epic,
                PromptTemplate(EPIC_GENERATION_TEMPLATE),
                project_description=project_description,
                feature_description=ev.feature_description
            )
        else:
            # Improve the suggested epic
            epic_critiques = await ctx.get("epic_critiques", [])
            epic_critiques.append(ev.critique)
            await ctx.set("epic_critiques", epic_critiques)
            project_description = await ctx.get("project_description")
            self.logger.debug(f"Try to improve the epic using the critique: '{ev.critique}'")
            generated_epic = self.llm.structured_predict(
                Epic,
                PromptTemplate(EPIC_REFINEMENT_TEMPLATE),
                project_description=project_description,
                feature_description=ev.feature_description,
                epic=await ctx.get("epic"),
                critique=ev.critique,
            )

        self.logger.debug(f"Generated epic: '{generated_epic}'")
        if self.quality_assurance_enabled:
            self.logger.debug(f"Epic quality assurance is enabled. Continuing with quality assurance event.")
            return EpicQualityAssuranceEvent(generated_epic=generated_epic)
        else:
            self.logger.debug(f"Epic quality assurance is disabled. Continuing with critiquing event.")
            return EpicCritiquingEvent(generated_epic=generated_epic)

    @step(retry_policy=ConstantDelayRetryPolicy(delay=1, maximum_attempts=5))
    async def epic_quality_assurance(self, ctx: Context, ev: EpicQualityAssuranceEvent) -> EpicQualityCriterionEvaluationEvent:
        self.logger.debug(f"Evaluate the quality criteria for the generated epic: '{ev.generated_epic}'")
        await ctx.set("generated_epic", ev.generated_epic)
        await ctx.set("quality_criteria_cnt", len(QUALITY_CRITERIA.keys()))
        project_description = await ctx.get("project_description")
        feature_description = await ctx.get("feature_description")

        for criterion, definition in QUALITY_CRITERIA.items():
            ctx.send_event(EpicQualityCriterionEvaluationEvent(
                project_description=project_description,
                feature_description=feature_description,
                generated_epic=ev.generated_epic,
                quality_criterion=criterion,
                quality_criterion_definition=definition))
        return None

    @step(num_workers=len(QUALITY_CRITERIA.keys()))
    async def epic_quality_criterion_evaluation(self, ctx: Context, ev: EpicQualityCriterionEvaluationEvent) -> EpicQualityImprovementEvent:
        self.logger.debug(f"Evaluate the quality criterion '{ev.quality_criterion}' for the generated epic: '{ev.generated_epic}'")
        evaluation_result = EnrichedQualityCriterionEvaluation(fulfilled=True, explanation="",
                                                               quality_criterion=ev.quality_criterion,
                                                               quality_criterion_definition=ev.quality_criterion_definition)
        project_description = await ctx.get("project_description")
        feature_description = await ctx.get("feature_description")

        try:
            epic_evaluation = await self.llm.astructured_predict(
                QualityCriterionEvaluation,
                PromptTemplate(EPIC_QUALITY_EVALUATION_TEMPLATE),
                project_description=project_description,
                feature_description=feature_description,
                epic=ev.generated_epic,
                quality_criterion=ev.quality_criterion,
                quality_criterion_definition=ev.quality_criterion_definition
            )
            self.logger.debug(f"Evaluation result for '{ev.quality_criterion}': '{epic_evaluation}'")
            evaluation_result.fulfilled = epic_evaluation.fulfilled
            evaluation_result.explanation = epic_evaluation.explanation
        except Exception as e:
            self.logger.debug(f"Could not evaluate the quality criterion '{ev.quality_criterion}'. Error: {e}")
            evaluation_result.explanation = "Error during evaluation. Skipped it!"
        return EpicQualityImprovementEvent(generated_epic=ev.generated_epic, evaluation_result=evaluation_result)

    @step(retry_policy=ConstantDelayRetryPolicy(delay=1, maximum_attempts=5))
    async def epic_quality_improvement(self, ctx: Context, ev: EpicQualityImprovementEvent) -> EpicCritiquingEvent:
        quality_criteria_cnt = await ctx.get("quality_criteria_cnt")
        results = ctx.collect_events(ev, [EpicQualityImprovementEvent] * quality_criteria_cnt)
        if results is None:
            return None

        evaluation_results = [result.evaluation_result for result in results]
        await ctx.set("quality_evaluation_results", evaluation_results)

        unfulfilled_criteria = [
            f"- The epic is not '{evaluation.quality_criterion}'. Explanation: {evaluation.explanation}" for evaluation
            in evaluation_results if evaluation.fulfilled == False]

        if len(unfulfilled_criteria) > 0:
            # Improve epic
            self.logger.debug(f"Trying to improve regarding '{unfulfilled_criteria}' the epic based on the evaluation feedback.")
            project_description = await ctx.get("project_description")
            feature_description = await ctx.get("feature_description")
            improved_epic = self.llm.structured_predict(
                Epic,
                PromptTemplate(EPIC_QUALITY_IMPROVEMENT_TEMPLATE),
                project_description=project_description,
                feature_description=feature_description,
                epic=ev.generated_epic,
                evaluation_feedback="\n".join(unfulfilled_criteria),
            )
            return EpicCritiquingEvent(generated_epic=improved_epic)
        else:
            return EpicCritiquingEvent(generated_epic=ev.generated_epic)

    @step(retry_policy=ConstantDelayRetryPolicy(delay=1, maximum_attempts=5))
    async def critique_epic(self, ctx: Context, ev: EpicCritiquingEvent) -> EpicGenerationEvent | StopEvent:
        await ctx.set("epic", ev.generated_epic)
        project_description = await ctx.get("project_description")
        feature_description = await ctx.get("feature_description")

        # Suggest critiques
        suggested_epic_critiques = self.llm.structured_predict(
            SuggestedCritiques,
            PromptTemplate(EPIC_CRITIQUE_SUGGESTION_TEMPLATE),
            project_description=project_description,
            feature_description=feature_description,
            epic=ev.generated_epic
        )

        # Ask human for critique
        gen_description = '.\n'.join(ev.generated_epic.description.split('.'))
        human_prompt = f"The following epic was generated based on the feature description: '{feature_description}'\n\n"
        human_prompt += "Generated Epic:\n----------\n"
        human_prompt += f"Title: {ev.generated_epic.title}\n"
        human_prompt += f"Description:\n{gen_description}\n"
        human_prompt += f"Please review the epic and specify critiques what needs to be improved. If you are satisfied, press enter.\n"
        human_prompt += f"The following critiques have been suggested:\n"
        for critique in suggested_epic_critiques.critiques:
            human_prompt += f"- {critique}\n"

        suggested_critiques = await ctx.get("suggested_critiques", [])
        suggested_critiques.append(suggested_epic_critiques.critiques)
        await ctx.set("suggested_critiques", suggested_critiques)

        user_critique = input(human_prompt)
        if user_critique and len(user_critique) > 0:
            # Refined the epic with the provided critique
            self.logger.debug(f"Refine the epic based on the provided critique: '{user_critique}'")
            return EpicGenerationEvent(feature_description=feature_description, critique=user_critique)
        else:
            # No critiques, return result
            # Export the generated critiques to JSON
            if os.path.exists(self.result_directory):
                suggested_critiques_file = os.path.join(self.result_directory, "suggested_epic_critiques.json")
                with open(suggested_critiques_file, "w") as json_file:
                    suggested_epic_critiques = {
                        "suggested_critiques": suggested_critiques
                    }
                    json.dump(suggested_epic_critiques, json_file)
            else:
                self.logger.debug(f"Given result directory: '{self.result_directory}' does not exist. Skip storing the suggested critiques.")
            return StopEvent(result=ev.generated_epic)