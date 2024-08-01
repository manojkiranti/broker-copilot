from rest_framework import permissions
from django.contrib import admin
from django.shortcuts import render
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import TemplateView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path as url 
# from accounts.views import my_view
import anz.urls
import ai_service.urls
import opportunity_app.urls
import compliance_service.urls
import utils.urls
import dashboard_app.urls
# def get_redirect_url(request, *args, **kwargs):
#     return render(request, 'index.html')


schema_view = get_schema_view(
    openapi.Info(
        title="Broker Copilot API",
        default_version='v1',
        description="API documentation",
        terms_of_service="",
        contact=openapi.Contact(email=""),
        license=openapi.License(name=""),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('accounts.urls')),
    path('api/', include('services.urls')),
    path('api/anz/', include(anz.urls)),
    path('api/ai/', include(ai_service.urls)),
    path('api/', include(opportunity_app.urls)),
    path('api/comliance-note/', include(compliance_service.urls)),
    path('api/utils/', include(utils.urls)),
    path('api/dashboard/', include(dashboard_app.urls)),
    # path('', my_view, name='my-view'),
    

    # path('', TemplateView.as_view(template_name='index.html')),
    path('docs', schema_view.with_ui('swagger',
         cache_timeout=0), name="schema-swagger-ui"),
    # path('', TemplateView.as_view(template_name='index.html')),
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns.append(url(r'^.*$', get_redirect_url))

