from typing import List
from pydantic import BaseModel, Field

class FeatureDescriptionEvaluation(BaseModel):
    """Data model for the evaluation result of textual description of the new feature to be implemented."""
    sufficient: bool = Field(
        description="Evaluation decision whether the feature description is sufficient."
    )
    explanation: str = Field(
        description="Explanation to emphasize the reason for the evaluation decision. The explanation should not be longer than one sentences."
    )
    required_input: List[str] = Field(
        description="List of additional information that is required to consider the description as sufficient. The list is empty if the description is already sufficient."
    )