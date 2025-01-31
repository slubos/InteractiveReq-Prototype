from pydantic import BaseModel, Field
from typing import List

class UserStory(BaseModel):
    """Data model for generated User Stories."""
    title: str = Field(
        description="Title of the user story describing its content. The title should have a maximum of 10 words."
    )
    story: str = Field(
        description="Informal, general explanation of a software feature written from the perspective of the end user, articulating how it will provide value. User stories need to follow the pattern: As [persona], I want to [do something], so that [need is fulfilled]."
    )
    acceptance_criteria: List[str] = Field(
        description="Conditions that must be satisfied such that the user story is completed. Usually 3-8 criteria."
    )

class UserStories(BaseModel):
    """Data model for generated related User Stories."""
    user_stories: List[UserStory] = Field(
        description="A collection of related user stories."
    )
