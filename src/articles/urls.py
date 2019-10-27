from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    ArticleViewSet,
    MainPageAPIView
)


app_name = 'article'

router = SimpleRouter()
router.register('article', ArticleViewSet, base_name='article')


urlpatterns = router.urls + [
    path('main/', MainPageAPIView.as_view(), name='main-page')
]
