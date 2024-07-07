from azure.storage.blob import BlobServiceClient

AZURE_ACCOUNT_NAME = 'stgbcrboqdvs2n4'
AZURE_CONTAINER = 'content'
AZURE_ACCOUNT_KEY = '+s4l6vp7Rlz8ZL4glsxhuH+nX9knrDYJ6oRyAT4hBq1fgF7AMy6jyJfInwdHaMFkh68Y6NK419xt+AStl9U7gA==' 

blob_service = BlobServiceClient(AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY)
blobfile = []
generator = blob_service.list_blobs(AZURE_CONTAINER, prefix="/", delimiter="")
for blob in generator:
    blobname = blob.name.split('/')[-1]
    blobfile.append(blobname)
    print("\t Blob name: " + blob.name)
print(blobfile)
