import os
import json
from llama_index.core import VectorStoreIndex
from app.models.Requirements import Requirements
from app.services.RequirementsDataReader import RequirementsDataReader
from llama_index.core import Settings

Settings.chunk_size = 2048

class RequirementsIndexGenerator:
    def __init__(self, embed_model):
        self.embed_model = embed_model

    def load_index(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        with open(file_path, encoding="utf-8") as f:
            try:
                data = json.load(f)
                requirements = Requirements(**data)
            except Exception as e:
                raise BaseException(f"Requirements file could not be loaded: {e}")

        documents = RequirementsDataReader().load_data(requirements)
        index = VectorStoreIndex.from_documents(
            documents=documents,
            embed_model=self.embed_model,
        )
        return index

    def load_index_from_file(self, file):
        try:
            requirements = Requirements(**file)
        except Exception as e:
            raise BaseException(f"Requirements file could not be loaded: {e}")

        documents = RequirementsDataReader().load_data(requirements)
        index = VectorStoreIndex.from_documents(
            documents=documents,
            embed_model=self.embed_model,
        )
        return index