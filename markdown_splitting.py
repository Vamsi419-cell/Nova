from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter


markdown_text = """
# Machine Learning

Machine learning allows computers to learn from data.

## Supervised Learning

Supervised learning uses labelled data.

### Regression

Regression predicts continuous values.

### Classification

Classification predicts categories.

## Unsupervised Learning

Unsupervised learning works with unlabelled data.
"""

headers = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers
)

documents = splitter.split_text(markdown_text)
from langchain_text_splitters import RecursiveCharacterTextSplitter

recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)

final_chunks = recursive_splitter.split_documents(documents)

for i, chunk in enumerate(final_chunks):
    print(f"\nChunk {i + 1}")
    print(chunk.page_content)
    print(chunk.metadata)
