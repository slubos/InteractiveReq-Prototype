import logging
from llama_index.core import PromptTemplate
from llama_index.core.workflow import Workflow, Context, step, StartEvent, StopEvent
from app.events.ProjectContextEvents import SummarizeProjectContextEvent
from app.models.ProjectDescription import ProjectDescription
from app.models.Requirements import ExtendedEpic
from app.prompts.ProjectContextPrompts import PROJECT_CONTEXT_SUMMARIZATION


class ProjectContextWorkflow(Workflow):
    def __init__(self, llm, index, max_steps: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm = llm
        self.index = index
        self.max_steps = max_steps
        self.retrieval_top_k = 5

    @step
    async def retrieve_feature_context(self, ctx: Context, ev: StartEvent) -> SummarizeProjectContextEvent:
        self.logger.debug(
            f"Retrieve the relevant epics and user stories from the provided feature descriptions: '{ev.feature_descriptions}'")
        await ctx.set("feature_descriptions", ev.feature_descriptions)

        # Retrieval from index
        retriever = self.index.as_retriever(similarity_top_k=self.retrieval_top_k)
        query = "\n".join(ev.feature_descriptions) if len(ev.feature_descriptions) > 0 else ""
        retrieved_epics = await retriever.aretrieve(query)

        self.logger.debug(f"Retrieved {len(retrieved_epics)} epics from the index.")
        epics = [ExtendedEpic(**epic_node.metadata) for epic_node in retrieved_epics]

        return SummarizeProjectContextEvent(epics=epics)

    @step
    async def summarize_project_context(self, ctx: Context, ev: SummarizeProjectContextEvent) -> StopEvent:
        self.logger.debug(
            f"Summarizing the project context based on most relevant epics and user stories for feature description.")

        epics_and_user_stories_description = ""
        for epic in ev.epics:
            epics_and_user_stories_description += f"Epic title: {epic.title}\nEpic description: {epic.description}\n"
            epics_and_user_stories_description += f"Related User Stories:\n"
            for user_story in epic.user_stories:
                epics_and_user_stories_description += f"Title: {user_story.title}\nStory: {user_story.story}\n"

        summarized_project_context = self.llm.structured_predict(
            ProjectDescription,
            PromptTemplate(PROJECT_CONTEXT_SUMMARIZATION),
            epics_and_user_stories=epics_and_user_stories_description
        )

        return StopEvent(result=summarized_project_context)
