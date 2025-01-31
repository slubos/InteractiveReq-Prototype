from typing import List
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from app.models.Requirements import Requirements


class RequirementsDataReader(BaseReader):
    def __init__(self):
        super().__init__()

    def load_data(self, requirements: Requirements) -> List[Document]:
        documents = []
        for epic in requirements.epics:
            # Create a document for each epic
            epic_document = Document(text=epic.to_text(), metadata=
                {"title": epic.title, "description": epic.description, "user_stories": epic.user_stories}
            )
            documents.append(epic_document)

        return documents