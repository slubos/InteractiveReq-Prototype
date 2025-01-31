from typing import List
from llama_index.core.workflow import Event
from app.models.Requirements import ExtendedEpic

class SummarizeProjectContextEvent(Event):
    epics: List[ExtendedEpic]
