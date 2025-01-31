from pydantic import BaseModel, Field


class QualityCriterionEvaluation(BaseModel):
    """Data model for quality criteria evaluation"""
    fulfilled: bool = Field(
        description="Evaluation decision whether the quality criterion is fulfilled."
    )
    explanation: str = Field(
        description="Explanation to emphasize the reason for the evaluation decision giving hints for improvement. The explanation should not be longer than one sentence."
    )


class EnrichedQualityCriterionEvaluation(QualityCriterionEvaluation):
    """Data model for quality criteria evaluation including definition of the quality criterion"""
    quality_criterion: str = Field(
        description="Label of the quality criterion."
    )
    quality_criterion_definition: str = Field(
        description="Definition of the quality criterion."
    )