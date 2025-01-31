from llama_index.core.workflow import Event
from app.models.Epic import Epic
from app.models.QualityCriterionEvaluation import EnrichedQualityCriterionEvaluation
from app.models.UserStory import UserStory, UserStories

class UserStoryGenerationEvent(Event):
    epic: Epic
    critique: str | None


class UserStoryQualityAssuranceEvent(Event):
    generated_user_stories: UserStories


class UserStoryQualityCriterionEvaluationEvent(Event):
    user_story_id: int
    generated_user_story: UserStory
    quality_criterion: str
    quality_criterion_definition: str


class UserStoryQualityImprovementEvent(Event):
    user_story_id: int
    generated_user_story: UserStory
    evaluation_result: EnrichedQualityCriterionEvaluation


class UserStoryCritiquingEvent(Event):
    generated_user_stories: UserStories