from llama_index.core.workflow import Event
from app.models.Epic import Epic
from app.models.QualityCriterionEvaluation import EnrichedQualityCriterionEvaluation

class EpicGenerationEvent(Event):
    feature_description: str
    critique: str | None


class EpicQualityAssuranceEvent(Event):
    generated_epic: Epic


class EpicQualityCriterionEvaluationEvent(Event):
    generated_epic: Epic
    quality_criterion: str
    quality_criterion_definition: str


class EpicQualityImprovementEvent(Event):
    generated_epic: Epic
    evaluation_result: EnrichedQualityCriterionEvaluation


class EpicCritiquingEvent(Event):
    generated_epic: Epic