from typing import List
from pydantic import BaseModel, Field

class SuggestedCritiques(BaseModel):
    """Data model for suggested critiques, i.e., direct feedback to adapt generated output."""
    critiques: List[str] = Field(
        description="Suggested critiques to improve or adapt the generated output. Usually 5 critiques."
    )