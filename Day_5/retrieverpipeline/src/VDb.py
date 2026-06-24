import asyncio
import os

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from .embeddings import embedder

INDEX_NAME = "ragindex"
NAMESPACE = "bot_data_source"


class VectorDatabase:
    def __init__(self):
        self.client = None
        self.index = None
        self.vector_store = None

    async def connect(self):
        """Initialize the Pinecone client and vector store."""
        if self.vector_store:
            return

        self.client, self.index, self.vector_store = await asyncio.to_thread(self._build_connection)

    def _build_connection(self):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY is not set in the environment.")

        client = Pinecone(api_key=api_key)
        index = client.Index(INDEX_NAME)
        vector_store = PineconeVectorStore(index=index, embedding=embedder, namespace=NAMESPACE)
        return client, index, vector_store

    async def disconnect(self):
        """Release the cached Pinecone client references."""
        self.client = None
        self.index = None
        self.vector_store = None

    async def retrieve_documents(self, query: str, department: str | None = None, top_k: int = 4) -> list[Document]:
        """Retrieve similar documents for the supplied query."""
        if not self.vector_store:
            await self.connect()

        search_kwargs = {"k": top_k}
        if department:
            search_kwargs["filter"] = {"department": {"$eq": department}}

        return await asyncio.to_thread(self.vector_store.similarity_search, query, **search_kwargs)


vdb = VectorDatabase()