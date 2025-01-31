from pydantic import BaseModel, Field

class FeatureDescription(BaseModel):
    """Data model for the textual description of the new feature to be implemented."""
    feature_description: str = Field(
        description="Textual description of the new feature to be implemented provided by the user."
    )