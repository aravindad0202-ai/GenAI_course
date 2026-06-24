import importlib
import os

CONTAINER_NAME = "ingestiondata"

print('Initializing blob')
class BlobDatabase:
    def __init__(self):
        self.service_client = None
        self.container_client = None
        print('Initializing blob 222')

    async def connect(self):
        """Initialize the Azure Blob client and ensure the container exists."""
        if self.container_client:
            return

        blob_module = importlib.import_module("azure.storage.blob.aio")
        core_exceptions = importlib.import_module("azure.core.exceptions")
        BlobServiceClient = blob_module.BlobServiceClient
        ResourceExistsError = core_exceptions.ResourceExistsError

        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING is not set in the environment.")

        self.service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.service_client.get_container_client(CONTAINER_NAME)

        try:
            await self.container_client.create_container()
        except ResourceExistsError:
            pass

    async def disconnect(self):
        """Release the cached Azure Blob client references."""
        if self.service_client:
            await self.service_client.close()

        self.service_client = None
        self.container_client = None

    async def upload_file(self, file_name: str, file_content: bytes) -> dict:
        """Store a file in the ingestiondata container."""
        if not self.container_client:
            await self.connect()

        blob_client = self.container_client.get_blob_client(file_name)
        await blob_client.upload_blob(file_content, overwrite=True)
        return {"container": CONTAINER_NAME, "blob_name": file_name}

    async def list_files(self) -> list[dict]:
        """List all files currently stored in the container."""
        if not self.container_client:
            await self.connect()

        files = []
        async for blob in self.container_client.list_blobs():
            files.append({"name": blob.name, "size": getattr(blob, "size", None)})
        return files

    async def delete_file(self, file_name: str) -> dict:
        """Delete a file from the container."""
        if not self.container_client:
            await self.connect()

        blob_client = self.container_client.get_blob_client(file_name)
        await blob_client.delete_blob()
        return {"container": CONTAINER_NAME, "blob_name": file_name, "deleted": True}


blobdb = BlobDatabase()