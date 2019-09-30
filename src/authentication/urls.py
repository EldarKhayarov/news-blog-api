from django.urls import path
from rest_framework_simplejwt import views as jwt_views


app_name = 'authentication'


urlpatterns = [
    path('token/', jwt_views.token_obtain_pair, name='token-obtain-pair'),
    path('token/refresh/', jwt_views.token_refresh, name='token-refresh'),
]