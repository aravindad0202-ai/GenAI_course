import asyncio

from .documentParser import DocumentParser
from .chunker import split_docs
from .BlobDb import blobdb
from .VDb import vdb
async def ingest_data(fileName, fileContent, department):
    parser = DocumentParser(fileName=fileName, fileContent=fileContent, department=department)
    docs = await asyncio.to_thread(parser.parse_document)
    docs = await asyncio.to_thread(split_docs, docs)
    vector_result = await vdb.upload_documents(docs)
    blob_result = await blobdb.upload_file(fileName, fileContent)
    return {
        "message": "Upload successful",
        "vector_result": vector_result,
        "blob_result": blob_result,
    }