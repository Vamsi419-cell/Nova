
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    Language
)

python_code = """
import numpy as np

def calculate_mean(values):
    return np.mean(values)

def calculate_variance(values):
    return np.var(values)

class Statistics:
    def summarize(self, values):
        return {
            "mean": calculate_mean(values),
            "variance": calculate_variance(values)
        }
"""

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=150,
    chunk_overlap=20
)

chunks = splitter.create_documents([python_code])

for i, chunk in enumerate(chunks):
    print(f"\\nChunk {i + 1}")
    print(chunk.page_content)
    print("-" * 50)
