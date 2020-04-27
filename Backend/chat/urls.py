from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('conversations/',views.ConversationsView.as_view(), name='conversations'),
]