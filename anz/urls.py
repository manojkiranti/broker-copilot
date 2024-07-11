from django.urls import path, include

from anz.views import DocsListAPIView

urlpatterns = [
    path('documents/', DocsListAPIView.as_view(), name="anz_docs_list"),
]
