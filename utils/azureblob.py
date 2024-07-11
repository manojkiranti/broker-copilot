# from azure.storage.blob import BlobServiceClient

# AZURE_ACCOUNT_NAME = 'stcg7senu7vkm7o'
# AZURE_CONTAINER = 'content'
# AZURE_ACCOUNT_KEY = 'QW4DZbbDb9dyhvL3+6a+kokEG9CkUDn13F17bbjq/d4J9LtE4QA6cRWDNlw08A+JvwSHLNKRcmW6+AStUAWl5g==' 

# blob_service = BlobServiceClient(AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY)
# blobfile = []
# generator = blob_service.list_blobs(AZURE_CONTAINER, prefix="/", delimiter="")
# for blob in generator:
#     blobname = blob.name.split('/')[-1]
#     blobfile.append(blobname)
#     print("\t Blob name: " + blob.name)
# print(blobfile)

import json


from azure.storage.blob import BlobServiceClient

# Your connection string
connection_string = "DefaultEndpointsProtocol=https;AccountName=stgbcrboqdvs2n4;AccountKey=+s4l6vp7Rlz8ZL4glsxhuH+nX9knrDYJ6oRyAT4hBq1fgF7AMy6jyJfInwdHaMFkh68Y6NK419xt+AStl9U7gA==;EndpointSuffix=core.windows.net"

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# List all blobs in a container
def list_blobs_in_container(container_name):
    try:
        container_client = blob_service_client.get_container_client(container_name)
        print(f"Listing blobs in container '{container_name}':")
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            print(f"\tBlob name: {blob.name}")
    except Exception as e:
        print(f"Error listing blobs: {e}")

# Example usage
container_name = "content"
list_blobs_in_container(container_name)
