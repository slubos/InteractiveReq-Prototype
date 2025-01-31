from pydantic import BaseModel, Field

class ProjectDescription(BaseModel):
    """Data model for the textual description of the already implemented project."""
    project_description: str = Field(
        description="Textual description of the the already implemented project."
    )
    