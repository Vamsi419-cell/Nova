from langchain_core.documents import Document 
from langchain_text_splitters import RecursiveCharacterTextSplitter
document = Document(
    page_content="""
    Python is a programming language.

    It supports object-oriented programming.

    Python is widely used in machine learning.

    It has libraries like PyTorch and TensorFlow.
    """,
    metadata={"source": "python_notes.txt"}
)
splitter = RecursiveCharacterTextSplitter(
    chunk_size = 250,
    chunk_overlap = 20 
)
chunks = splitter.split_documents([document])
for index , chunk in enumerate(chunks):
    print(f" \n Chunk {index+1}")
    print(chunk.page_content)
    print("Metadata", chunk.metadata)
    print("Length:", len(chunk.page_content))