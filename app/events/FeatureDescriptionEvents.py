from typing import List
from llama_index.core.workflow import Event
from app.models.FeatureDescriptionEvaluation import FeatureDescriptionEvaluation

class AggregateFeatureDescriptionEvent(Event):
    feature_descriptions: List[str]


class FeatureDescriptionRefinementEvent(Event):
    feature_description: str
    feature_description_evaluation: FeatureDescriptionEvaluation


class EvaluateFeatureDescriptionEvent(Event):
    feature_description: str