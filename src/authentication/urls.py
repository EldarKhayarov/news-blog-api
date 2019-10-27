from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import SimpleRouter

from .views import (
    RegisterUserAPIView,
    UserViewSet,
)


app_name = 'authentication'

router = SimpleRouter()
router.register('user', UserViewSet, base_name='user')


urlpatterns = [
    path('login/refresh-token/', jwt_views.token_refresh, name='token-refresh'),
    path('login/', jwt_views.token_obtain_pair, name='token-obtain-pair'),
    path('register/', RegisterUserAPIView.as_view(), name='register'),
] + router.urls
