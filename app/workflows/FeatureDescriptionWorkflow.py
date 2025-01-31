import logging
from llama_index.core import PromptTemplate
from llama_index.core.workflow import Workflow, Context, step, StartEvent, StopEvent
from app.events.FeatureDescriptionEvents import EvaluateFeatureDescriptionEvent, AggregateFeatureDescriptionEvent, FeatureDescriptionRefinementEvent
from app.models.FeatureDescription import FeatureDescription
from app.models.FeatureDescriptionEvaluation import FeatureDescriptionEvaluation
from app.prompts.FeatureDescriptionPrompts import FEATURE_DESCRIPTION_AGGREGATION_AND_IMPROVEMENT, FEATURE_DESCRIPTION_EVALUATION_TEMPLATE

class FeatureDescriptionWorkflow(Workflow):
    def __init__(self, llm, max_steps: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm = llm
        self.max_steps = max_steps
        self.max_user_preference_evaluation_cnt = 2

    @step
    async def aggregate_feature_descriptions(self, ctx: Context, ev: StartEvent | AggregateFeatureDescriptionEvent) -> EvaluateFeatureDescriptionEvent:
        if type(ev) is StartEvent:
            await ctx.set("project_description", ev.project_description)
            project_description = ev.project_description
        else:
            project_description = await ctx.get("project_description")

        self.logger.debug(f"Aggregate and improve the provided feature descriptions: '{ev.feature_descriptions}'")
        await ctx.set("feature_descriptions", ev.feature_descriptions)

        # Aggregate and improve feature_descriptions
        aggregated_feature_description = self.llm.structured_predict(
            FeatureDescription,
            PromptTemplate(FEATURE_DESCRIPTION_AGGREGATION_AND_IMPROVEMENT),
            project_description=project_description,
            feature_descriptions=";".join(ev.feature_descriptions)
        )
        self.logger.debug(f"Aggregated feature description: '{aggregated_feature_description.feature_description}'")
        return EvaluateFeatureDescriptionEvent(feature_description=aggregated_feature_description.feature_description)

    @step
    async def evaluate_feature_description(self, ctx: Context, ev: EvaluateFeatureDescriptionEvent) -> FeatureDescriptionRefinementEvent | StopEvent:
        self.logger.debug(f"Evaluate whether the provided feature description is sufficient: '{ev.feature_description}'")
        await ctx.set("feature_description", ev.feature_description)
        feature_description_evaluation_cnt = await ctx.get("feature_description_evaluation_cnt", 0)
        feature_description_evaluation_cnt += 1
        await ctx.set("feature_description_evaluation_cnt", feature_description_evaluation_cnt)

        # Skip evaluation if max count is reached
        if feature_description_evaluation_cnt <= self.max_user_preference_evaluation_cnt:
            # Evaluate provided feature description
            project_description = await ctx.get("project_description")
            feature_description_evaluation = self.llm.structured_predict(
                FeatureDescriptionEvaluation,
                PromptTemplate(FEATURE_DESCRIPTION_EVALUATION_TEMPLATE),
                project_description=project_description,
                feature_description=ev.feature_description
            )
            if not feature_description_evaluation.sufficient:
                # Feature description is not sufficient and need refinement (human-in-the-loop)
                self.logger.debug(f"Feature description is not sufficient. LLM explanation: '{feature_description_evaluation.explanation}'")
                return FeatureDescriptionRefinementEvent(feature_description=ev.feature_description, feature_description_evaluation=feature_description_evaluation)
            else:
                self.logger.debug(f"Feature description is sufficient. LLM explanation: '{feature_description_evaluation.explanation}'")

        # Feature description is sufficient
        return StopEvent(result=ev.feature_description)

    @step
    async def refine_feature_description(self, ctx: Context, ev: FeatureDescriptionRefinementEvent) -> AggregateFeatureDescriptionEvent:
        self.logger.debug(f"Request human feedback to better understand the feature description. Current input: '{ev.feature_description}'\nRequested information: '{ev.feature_description_evaluation.required_input}'")

        # Ask human to extend the feature description
        human_prompt = f"The current feature description: '{ev.feature_description}' is not sufficient to generate an epic.\n\n"
        human_prompt += "Please add further information considering the following aspects:\n"
        for required_input in ev.feature_description_evaluation.required_input:
            human_prompt += f"- {required_input}\n"
        additional_feature_description = input(human_prompt)

        # Retrieve complete user input
        provided_feature_descriptions = await ctx.get("feature_descriptions", [])
        provided_feature_descriptions.append(additional_feature_description)

        return AggregateFeatureDescriptionEvent(feature_descriptions=provided_feature_descriptions)
