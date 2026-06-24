import asyncio
import os

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from .embeddings import embedder

INDEX_NAME = "ragindex" #lower case alphanumeric
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

        self.client, self.index, self.vector_store = await asyncio.to_thread(self._build_pinecone_connection)

    def _build_pinecone_connection(self):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY is not set in the environment.")

        cloud = os.getenv("PINECONE_CLOUD", "aws")
        region = os.getenv("PINECONE_REGION", "us-east-1")

        client = Pinecone(api_key=api_key)
        existing_indexes = client.list_indexes().names()

        if INDEX_NAME not in existing_indexes:
            index_dimension = len(embedder.embed_query("pinecone index dimension probe"))
            client.create_index(
                name=INDEX_NAME,
                dimension=index_dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud=cloud, region=region),
            )

        index = client.Index(INDEX_NAME)
        vector_store = PineconeVectorStore(index=index, embedding=embedder, namespace=NAMESPACE)
        return client, index, vector_store

    async def disconnect(self):
        """Release the cached Pinecone client references."""
        self.client = None
        self.index = None
        self.vector_store = None

    async def upload_documents(self, documents: list[Document]) -> list[str]:
        """Upload LangChain documents without removing existing vectors."""
        if not self.vector_store:
            await self.connect()

        if not documents:
            return []

        return await asyncio.to_thread(self.vector_store.add_documents, documents)

    async def delete_documents_by_source(self, file_name: str) -> dict:
        """Delete vectors whose metadata source matches the provided file name."""
        if not self.index:
            await self.connect()

        if not file_name:
            return {"deleted_count": 0}

        await asyncio.to_thread(
            self.index.delete,
            namespace=NAMESPACE,
            filter={"source": {"$eq": file_name}},
        )
        return {"source": file_name, "deleted": True}


vdb = VectorDatabase()