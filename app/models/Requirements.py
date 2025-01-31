from pydantic import BaseModel, Field
from typing import List
from app.models.Epic import Epic
from app.models.UserStory import UserStory

class ExtendedEpic(Epic):
    """Data model for epics with related user stories."""
    user_stories: List[UserStory] = Field(
        description="User stories assigned to the epic."
    )
    
    def to_text(self):
        text = f"{self.title}\n{self.description}\n"
        for user_story in self.user_stories:
            text += f"{user_story.title}\n{user_story.story}\n"
        return text

class Requirements(BaseModel):
    """Data model for a set of requirements in the form of epics and related user stories."""
    epics: List[ExtendedEpic] = Field(
        description="List of epics including related user stories"
    )