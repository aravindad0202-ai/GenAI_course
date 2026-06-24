from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_docs(documents):
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size = 500,
        chunk_overlap = 120
    )
    docs = splitter.split_documents(documents)
    return docs
