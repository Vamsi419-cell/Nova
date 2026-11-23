
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
    Language,
)

from notebook_documents import NotebookLoader


class NotebookAwareTextSplitter:

    def __init__(self, chunk_size=300, chunk_overlap=50):

        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "h1"),
                ("##", "h2"),
                ("###", "h3"),
            ]
        )

        self.code_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def split_documents(self, documents):

        final_chunks = []

        for document in documents:

            cell_type = document.metadata.get("cell_type")

            # Markdown cells
            if cell_type == "markdown":

                markdown_chunks = self.markdown_splitter.split_text(
                    document.page_content
                )

                enriched_chunks = []

                for chunk in markdown_chunks:
                    metadata = {
                        **document.metadata,
                        **chunk.metadata,
                    }

                    enriched_chunks.append(
                        Document(
                            page_content=chunk.page_content,
                            metadata=metadata,
                        )
                    )

                # Further split oversized Markdown sections
                chunks = self.recursive_splitter.split_documents(
                    enriched_chunks
                )

            # Python code cells
            elif cell_type == "code":

                chunks = self.code_splitter.create_documents(
                    [document.page_content],
                    metadatas=[document.metadata],
                )

            # Raw or other cell types
            else:

                chunks = self.recursive_splitter.split_documents(
                    [document]
                )

            final_chunks.extend(chunks)

        return final_chunks


if __name__ == "__main__":

    loader = NotebookLoader("sample.json")
    documents = loader.load()

    splitter = NotebookAwareTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):

        print(f"\nChunk {i + 1}")
        print("Content:", chunk.page_content)
        print("Metadata:", chunk.metadata)
        print("-" * 50)
