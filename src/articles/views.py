from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
)

from .permissions import IsRedactorOrReadOnly
from .models import Article
from .serializers import (
    ArticleCreateRetrieveSerializer,
    ArticleUpdateSerializer,
    ArticleListSerializer,
    CommentCreateRetrieveSerializer,
)


class ArticleViewSet(
    CreateModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    queryset = Article.objects.all()
    serializer_class = ArticleCreateRetrieveSerializer
    lookup_field = 'slug'
    permission_classes = (IsRedactorOrReadOnly,)

    def update(self, request, *args, **kwargs):
        self.serializer_class = ArticleUpdateSerializer
        return super().update(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['POST'],
        url_path='add_comment',
        permission_classes=(IsAuthenticated,),
        serializer_class=CommentCreateRetrieveSerializer
    )
    def add_comment(self, request, slug=None):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request, 'article': self.get_object()}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class MainPageAPIView(ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer
    permission_classes = (AllowAny,)
