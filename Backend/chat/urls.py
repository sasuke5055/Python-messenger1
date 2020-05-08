from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from django.views.generic import TemplateView
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
   path('', views.room, name='room'),
   path('api-token-auth/', views.CustomObtainAuthToken.as_view(), name='api_token_auth'),
   path('rest-auth/registration/', include('rest_auth.registration.urls')),
   path('contacts/', views.ContactsView.as_view(), name='contacts'),
   path('conversations/',views.ConversationsView.as_view(), name='conversations'),
   path('messages/<pk>', views.ConversationMessagesView.as_view(), name='messages'),
   url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]