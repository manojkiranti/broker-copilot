from django.urls import path
from .views import (DashboardListAPIView)
urlpatterns = [
    path('', DashboardListAPIView.as_view(), name='dashboard-list'),
]