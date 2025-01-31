import json
import os
import logging
from llama_index.core import PromptTemplate
from llama_index.core.workflow import Workflow, Context, step, StartEvent, StopEvent
from llama_index.core.workflow.retry_policy import ConstantDelayRetryPolicy
from app.events.UserStoryGenerationEvents import UserStoryGenerationEvent, UserStoryCritiquingEvent, UserStoryQualityImprovementEvent, UserStoryQualityCriterionEvaluationEvent, UserStoryQualityAssuranceEvent
from app.models.Requirements import ExtendedEpic, Requirements
from app.models.QualityCriterionEvaluation import EnrichedQualityCriterionEvaluation, QualityCriterionEvaluation
from app.models.SuggestedCritiques import SuggestedCritiques
from app.models.UserStory import UserStory, UserStories
from app.prompts.QualityCriteria import INVEST_QUALITY_CRITERIA
from app.prompts.UserStoryPrompts import USER_STORY_CRITIQUE_SUGGESTION_TEMPLATE, USER_STORY_QUALITY_IMPROVEMENT_TEMPLATE, USER_STORY_QUALITY_EVALUATION_TEMPLATE, USER_STORY_REFINEMENT_TEMPLATE, USER_STORY_GENERATION_TEMPLATE

class UserStoryGenerationWorkflow(Workflow):
    def __init__(self, llm, max_steps: int = 10, quality_assurance_enabled: bool = True, result_directory: str = ".", **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm = llm
        self.max_steps = max_steps
        self.quality_assurance_enabled = quality_assurance_enabled
        self.result_directory = result_directory

    @step(retry_policy=ConstantDelayRetryPolicy(delay=1, maximum_attempts=5))
    async def generate_user_stories(self, ctx: Context, ev: StartEvent | UserStoryGenerationEvent) -> UserStoryQualityAssuranceEvent | UserStoryCritiquingEvent:
        if type(ev) is StartEvent:
            await ctx.set("epic", ev.epic)
            await ctx.set("project_description", ev.project_description)
            project_description = ev.project_description
            # Generate initial user stories
            self.logger.debug(f"Try to generate the user story for the epic: '{ev.epic}'")
            generated_user_stories = self.llm.structured_predict(
                UserStories,
                PromptTemplate(USER_STORY_GENERATION_TEMPLATE),
                project_description=project_description,
                epic=ev.epic
            )
        else:
            # Improve the suggested user stories
            user_story_critiques = await ctx.get("user_story_critiques", [])
            user_story_critiques.append(ev.critique)
            await ctx.set("user_story_critiques", user_story_critiques)
            user_stories = await ctx.get("user_stories")
            project_description = await ctx.get("project_description")
            self.logger.debug(f"Try to improve the user stories using the critique: '{ev.critique}'")
            generated_user_stories = self.llm.structured_predict(
                UserStories,
                PromptTemplate(USER_STORY_REFINEMENT_TEMPLATE),
                project_description=project_description,
                epic=ev.epic,
                user_stories=user_stories,
                critique=ev.critique
            )

        self.logger.debug(f"Generated User Stories: '{generated_user_stories}'")
        if self.quality_assurance_enabled:
            self.logger.debug(f"User story quality assurance is enabled. Continuing with quality assurance event.")
            return UserStoryQualityAssuranceEvent(generated_user_stories=generated_user_stories)
        else:
            self.logger.debug(f"User story quality assurance is disabled. Continuing with critiquing event.")
            return UserStoryCritiquingEvent(generated_user_stories=generated_user_stories)

    @step(retry_policy=ConstantDelayRetryPolicy(delay=1, maximum_attempts=5))
    async def user_story_quality_assurance(self, ctx: Context, ev: UserStoryQualityAssuranceEvent) -> UserStoryQualityCriterionEvaluationEvent:
        self.logger.debug(f"Evaluate the quality criteria for the generated user stories: '{ev.generated_user_stories}'")
        await ctx.set("generated_user_stories", ev.generated_user_stories)
        await ctx.set("quality_criteria_cnt", len(INVEST_QUALITY_CRITERIA.keys()))
        await ctx.set("user_story_cnt", len(ev.generated_user_stories.user_stories))

        for i in range(len(ev.generated_user_stories.user_stories)):
            for criterion, definition in INVEST_QUALITY_CRITERIA.items():
                ctx.send_event(UserStoryQualityCriterionEvaluationEvent(
                    user_story_id=i,
                    generated_user_story=ev.generated_user_stories.user_stories[i],
                    quality_criterion=criterion,
                    quality_criterion_definition=definition))
        return None

    @step(num_workers=len(INVEST_QUALITY_CRITERIA.keys()))
    async def user_story_quality_criterion_evaluation(self, ctx: Context, ev: UserStoryQualityCriterionEvaluationEvent) -> UserStoryQualityImprovementEvent:
        self.logger.debug(f"Evaluate the quality criterion '{ev.quality_criterion}' for the generated user story {ev.user_story_id}: '{ev.generated_user_story}'")
        evaluation_result = EnrichedQualityCriterionEvaluation(fulfilled=True, explanation="",
                                                               quality_criterion=ev.quality_criterion,
                                                               quality_criterion_definition=ev.quality_criterion_definition)
        project_description = await ctx.get("project_description")
        epic = await ctx.get("epic")

        try:
            user_story_evaluation = self.llm.structured_predict(
                QualityCriterionEvaluation,
                PromptTemplate(USER_STORY_QUALITY_EVALUATION_TEMPLATE),
                epic=epic,
                project_description=project_description,
                user_story=ev.generated_user_story,
                quality_criterion=ev.quality_criterion,
                quality_criterion_definition=ev.quality_criterion_definition
            )
            self.logger.debug(f"Evaluation result for '{ev.quality_criterion}': '{user_story_evaluation}'")
            evaluation_result.fulfilled = user_story_evaluation.fulfilled
            evaluation_result.explanation = user_story_evaluation.explanation
        except Exception as e:
            self.logger.debug(f"Could not evaluate the quality criterion '{ev.quality_criterion}'. Error: {e}")
            evaluation_result.explanation = "Error during evaluation. Skipped it!"
        return UserStoryQualityImprovementEvent(user_story_id=ev.user_story_id,
                                                generated_user_story=ev.generated_user_story,
                                                evaluation_result=evaluation_result)

    @step(retry_policy=ConstantDelayRetryPolicy(delay=1, maximum_attempts=5))
    async def user_story_quality_improvement(self, ctx: Context, ev: UserStoryQualityImprovementEvent) -> UserStoryCritiquingEvent:
        quality_criteria_cnt = await ctx.get("quality_criteria_cnt")
        user_story_cnt = await ctx.get("user_story_cnt")
        results = ctx.collect_events(ev, [UserStoryQualityImprovementEvent] * (quality_criteria_cnt * user_story_cnt))
        if results is None:
            return None

        await ctx.set("quality_evaluation_results", results)

        improved_user_stories = []
        for i in range(user_story_cnt):
            user_story_evaluation_results = [r.evaluation_result for r in results if r.user_story_id == i]
            user_story = [r.generated_user_story for r in results if r.user_story_id == i][0]
            unfulfilled_criteria = [
                f"- The user story is not '{evaluation.quality_criterion}'. Explanation: {evaluation.explanation}" for
                evaluation in user_story_evaluation_results if evaluation.fulfilled == False]

            if len(unfulfilled_criteria) > 0:
                # Improve epic
                project_description = await ctx.get("project_description")
                epic = await ctx.get("epic")
                self.logger.debug(f"Trying to improve the user story {i} based on the evaluation feedback.")
                improved_user_story = self.llm.structured_predict(
                    UserStory,
                    PromptTemplate(USER_STORY_QUALITY_IMPROVEMENT_TEMPLATE),
                    epic=epic,
                    project_description=project_description,
                    user_story=user_story,
                    evaluation_feedback="\n".join(unfulfilled_criteria),
                )
                improved_user_stories.append(improved_user_story)
            else:
                self.logger.debug(f"No need to improve the user story {i} based on the evaluation feedback.")
                improved_user_stories.append(user_story)

        return UserStoryCritiquingEvent(generated_user_stories=UserStories(user_stories=improved_user_stories))

    @step(retry_policy=ConstantDelayRetryPolicy(delay=1, maximum_attempts=5))
    async def critique_user_stories(self, ctx: Context, ev: UserStoryCritiquingEvent) -> UserStoryGenerationEvent | StopEvent:
        await ctx.set("user_stories", ev.generated_user_stories.user_stories)
        project_description = await ctx.get("project_description")
        epic = await ctx.get("epic")

        # Suggest critiques
        suggested_user_story_critiques = self.llm.structured_predict(
            SuggestedCritiques,
            PromptTemplate(USER_STORY_CRITIQUE_SUGGESTION_TEMPLATE),
            epic=epic,
            project_description=project_description,
            user_stories=ev.generated_user_stories.user_stories
        )

        # Ask human for critique
        gen_description = '.\n'.join(epic.description.split('.'))
        human_prompt = f"Based on the generated epic:\n----------\n"
        human_prompt += f"Title: {epic.title}\n"
        human_prompt += f"Description:\n{gen_description}\n"
        human_prompt += f"The following User Stories have been generated:\n\n"
        for user_story in ev.generated_user_stories.user_stories:
            human_prompt += f"Title: {user_story.title}\n"
            human_prompt += f"Story: {user_story.story}\n"
            gen_acceptance_criteria = '\n'.join([f"- {ac}" for ac in user_story.acceptance_criteria])
            human_prompt += f"Acceptance Criteria:\n{gen_acceptance_criteria}\n\n"
        human_prompt += f"Please review the user stories and specify critiques what needs to be improved. If you are satisfied, press enter.\n"
        human_prompt += f"The following critiques have been suggested:\n"
        for critique in suggested_user_story_critiques.critiques:
            human_prompt += f"- {critique}\n"

        suggested_critiques = await ctx.get("suggested_critiques", [])
        suggested_critiques.append(suggested_user_story_critiques.critiques)
        await ctx.set("suggested_critiques", suggested_critiques)

        user_critique = input(human_prompt)
        if user_critique and len(user_critique) > 0:
            # Refined the epic with the provided critique
            self.logger.debug(f"Refine the user stories based on the provided critique: '{user_critique}'")
            return UserStoryGenerationEvent(generated_epic=epic, critique=user_critique)
        else:
            # No critiques, return result
            # Export the generated critiques to JSON
            if os.path.exists(self.result_directory):
                suggested_critiques_file = os.path.join(self.result_directory, "suggested_user_story_critiques.json")
                with open(suggested_critiques_file, "w") as json_file:
                    suggested_user_story_critiques = {
                        "suggested_critiques": suggested_critiques
                    }
                    json.dump(suggested_user_story_critiques, json_file)
            else:
                self.logger.debug(f"Given result directory: '{self.result_directory}' does not exist. Skip storing the suggested critiques.")

            generated_requirement = ExtendedEpic(title=epic.title, description=epic.description, user_stories=ev.generated_user_stories.user_stories)
            result = Requirements(epics=[generated_requirement])
            return StopEvent(result=result)