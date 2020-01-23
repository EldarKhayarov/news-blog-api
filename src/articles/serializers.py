from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from .models import Comment, Article, Resource


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username',)


class ResourceBaseSerializer(serializers.ModelSerializer):
    """
    Base resource serializer. Not for direct use.
    """
    delete = serializers.BooleanField(default=False, required=False, write_only=True)

    class Meta:
        abstract = True
        model = Resource
        fields = (
            'id',
            'url',
            'type',
            'delete',
        )


class ResourceCreateSerializer(ResourceBaseSerializer):
    """
    Nested serializer for creating list of articles or comments resources.
    """
    pass


class ResourceUpdateSerializer(ResourceBaseSerializer):
    """
    Nested serializer for updating list of articles or comments resources.

    `id` field is required for updating.
    """
    id = serializers.IntegerField(required=True)


class ResourceOwnerValidateMixin:
    """
    Base Resource owner serializer with `validate` method.
    """
    def validate(self, attrs):
        attrs = super().validate(attrs)

        # Author validation
        if self.context.get('request') is not None and \
                getattr(self.context['request'], 'user') is not None:
            attrs['author'] = self.context['request'].user

        elif self.context.get('user') is not None:
            attrs['author'] = self.context['user']

        else:
            raise ValidationError("User is not authenticated.")

        return attrs


class ResourceOwnerCreateMixin(ResourceOwnerValidateMixin):
    """
    Mixin for comment and article create serializers only.

    Adds custom `create` methods with creating nested `resources` objects.
    """
    def create(self, validated_data):
        resources_data = validated_data.pop('resources', None)

        # Get current model from metaclass
        object_model = self._model
        article_key, comment_key = None, None

        instance = object_model.objects.create(**validated_data)
        instance.save()

        if object_model is Article:
            article_key = instance
        elif object_model is Comment:
            comment_key = instance
        else:
            raise TypeError("Type of resources owner must be Comment or Article.")

        if resources_data is not None:
            # if validated data has resources
            # create resources in database
            Resource.objects.bulk_create(
                [Resource(
                    article=article_key,
                    comment=comment_key,
                    url=r['url'],
                    type=r['type']
                ) for r in resources_data]
            )

        return instance


class ResourceOwnerUpdateMixin(ResourceOwnerValidateMixin):
    """
    Mixin for comment and article update serializers only.

    Adds custom `update` method with updating nested `resources` objects.
    """
    def update(self, instance, validated_data):
        resources_data = validated_data.pop('resources')
        # Get current model from metaclass
        object_model = self._model

        # update all fields in instance
        instance = super().update(instance, validated_data)

        if resources_data is not None:
            if object_model is Article:
                resources_queryset = Resource.objects.filter(
                    is_deleted=False, article=instance
                )
            elif object_model is Comment:
                resources_queryset = Resource.objects.filter(
                    is_deleted=False, comment=instance
                )
            else:
                raise TypeError(
                    "Type of resources owner must be Comment or Article."
                )

            for r_data in resources_data:
                # Get resource by given id
                resource = resources_queryset.get(id=r_data['id'])
                if resource is None:
                    raise ValueError("There is not a resource with such id.")

                # If flag 'delete' is True
                # Deleting an instance
                if r_data.get('delete', False):
                    resource.delete()
                    continue

                # if flag isn't exists or false
                # Update all fields
                for key, value in r_data.items():
                    setattr(resource, key, value)

                resource.save()

        return instance


class CommentBaseSerializer(serializers.ModelSerializer):
    """
    Base comment serializer. Not for use.
    """
    author = AuthorSerializer()
    # Resources field required

    _model = Comment

    class Meta:
        abstract = True
        model = Comment
        fields = (
            'author',
            'created_at',
            'text',
            'resources',
        )
        read_only_fields = ('author', 'created_at')


class CommentCreateRetrieveSerializer(
    ResourceOwnerCreateMixin, CommentBaseSerializer
):
    """
    Comment serializer for creating, getting an instance/list of instances.
    """
    resources = ResourceCreateSerializer(many=True)

    def validate(self, attrs):
        if self.context.get('article') is None:
            raise KeyError("Add article to context.")

        attrs['article'] = self.context['article']
        return super().validate(attrs)


class CommentUpdateSerializer(ResourceOwnerUpdateMixin, CommentBaseSerializer):
    """
    Comment serializer for updating (`PUT`, `PATCH`) request methods.
    """
    resources = ResourceUpdateSerializer(many=True)


class ArticleDetailBaseSerializer(serializers.ModelSerializer):
    """
    Base article serializer. Not for direct use.
    """
    author = AuthorSerializer(read_only=True)
    # Resources field required
    # Comments field required

    _model = Article

    class Meta:
        abstract = True
        model = Article
        fields = (
            'title',
            'description',
            'text',
            'preview_image',
            'author',
            'created_at',
            'resources',
            'comments',
        )
        read_only_fields = ('created_at', 'comments')


class ArticleCreateRetrieveSerializer(
    ResourceOwnerCreateMixin, ArticleDetailBaseSerializer
):
    """
    Article serializer for creating, getting an instance/list of instances.
    """
    resources = ResourceCreateSerializer(many=True)
    comments = CommentCreateRetrieveSerializer(many=True, read_only=True)


class ArticleUpdateSerializer(
    ResourceOwnerUpdateMixin, ArticleDetailBaseSerializer
):
    """
    Article serializer for updating (`PUT`, `PATCH`) request methods.
    """
    resources = ResourceUpdateSerializer(many=True)
    comments = CommentUpdateSerializer(many=True, read_only=True)


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            'title',
            'description',
            'preview_image',
            'slug',
        )
        read_only_fields = fields
