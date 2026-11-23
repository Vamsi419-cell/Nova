
import json
import os

from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader


class NotebookLoader(BaseLoader):

    def __init__(self, file_path: str):
        self.file_path = file_path

    def lazy_load(self):
        # Read the notebook JSON file
        with open(self.file_path, "r", encoding="utf-8") as file:
            notebook = json.load(file)

        notebook_name = os.path.basename(self.file_path)
        total_cells = len(notebook["cells"])

        # Process each cell
        for index, cell in enumerate(notebook["cells"]):

            cell_type = cell["cell_type"]
            source = cell["source"]

            # Normalize source into a string
            if isinstance(source, list):
                source = "".join(source)

            # Ignore empty cells
            if not source.strip():
                continue

            # Convert the cell into a LangChain Document
            yield Document(
                page_content=source,
                metadata={
                    "source": self.file_path,
                    "notebook_name": notebook_name,
                    "cell_type": cell_type,
                    "cell_index": index,
                    "total_cells": total_cells,
                }
            )


if __name__ == "__main__":

    loader = NotebookLoader("sample.json")

    documents = loader.load()

    for doc in documents:
        print("Content:", doc.page_content)
        print("Metadata:", doc.metadata)
        print("-" * 50)
