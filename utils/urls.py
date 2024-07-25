from django.urls import path, include

from utils.views import WebsiteDataListAPIView, WesiteDataDetailAPIView, WebsiteDataLabelsAPIView, WebisteCreateContactAPIView
urlpatterns = [
    path('get_website_data/<int:pk>', WebsiteDataListAPIView.as_view(), name="website_data"),
    path('get_website_data/<int:pk>/detail/', WesiteDataDetailAPIView.as_view(), name="website__data_detail"),
    path('get_website_data/labels/', WebsiteDataLabelsAPIView.as_view(), name="website__data_labels"),
    path('get_website_data/contact/', WebisteCreateContactAPIView.as_view(), name="website__data_contact"),
]
