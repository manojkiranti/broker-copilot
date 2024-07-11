from rest_framework.response import Response
from rest_framework import status
from rest_framework.views  import APIView
import os
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime, timedelta
from django.shortcuts import render

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from django.conf import settings
# Create your views here.

# Your connection string
connection_string = os.getenv('AZURE_STORAGE_ANZ_CONNECTION_STRING')
# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)


class DocsListAPIView(APIView):
    @swagger_auto_schema(tags=['ANZ Wiki Service'])
    def get(self, request, *args, **kwargs):
        container_name = "anz"
        blob_list = self.list_blobs_in_container(container_name)
        if blob_list is None:
            return Response({"error": "Failed to retrieve blobs"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        blobs_info = []
        for blob in blob_list:
            blob_url = self.get_blob_url(container_name, blob.name)
            blobs_info.append({
                'name': blob.name,
                'url': blob_url,
                'size': blob.size,
                'last_modified': blob.last_modified
            })
        response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": blobs_info,
            }
        return Response(response_data, status=status.HTTP_200_OK)

    def list_blobs_in_container(self, container_name):
        try:
            container_client = blob_service_client.get_container_client(container_name)
            return list(container_client.list_blobs())
        except Exception as e:
            print(f"Error listing blobs: {e}")
            return None

    def get_blob_url(self, container_name, blob_name):
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Generate SAS token to access blob
        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
        )
        return f"{blob_client.url}?{sas_token}"