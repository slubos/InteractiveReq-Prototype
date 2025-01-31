from pydantic import BaseModel, Field

class Epic(BaseModel):
    """Data model for generated Epics."""
    title: str = Field(
        description="Title of the epic describing its content. The title should have a maximum of 10 words."
    )
    description: str = Field(
        description="Description of the user needs to be solved with this epic. The description should not be longer than three sentences."
    )