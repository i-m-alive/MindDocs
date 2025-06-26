from azure.storage.blob import BlobServiceClient
import os

AZURE_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER")
AZURE_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def get_blob_url_from_filename(filename: str) -> str:
    blob_service = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
    blob_client = blob_service.get_blob_client(container=AZURE_CONTAINER_NAME, blob=filename)
    return blob_client.url
