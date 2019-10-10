from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework import mixins

from .permissions import IsSelf
from .serializers import (RegisterSerializer,
                          UpdateUserSerializer,
                          ChangePasswordSerializer,
                          )

User = get_user_model()


class RegisterUserAPIView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        User.objects.create_user(
            email=data['email'],
            username=data['username'],
            password=data['password']
        )


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    lookup_field = 'username'
    queryset = User.objects.filter(is_active=True, is_superuser=False)
    permission_classes = (AllowAny,)
    serializer_class = UpdateUserSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsSelf,),
        url_name='change_password'
    )
    def change_password(self, request, pk=None, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        user = self.get_object()

        is_valid = serializer.is_valid()
        if type(serializer.data.get('current_password')) == str:
            if not user.check_password(serializer.data['current_password']):
                return Response(
                    data={'detail': "Wrong password.", 'code': "password_change"},
                    status=status.HTTP_403_FORBIDDEN
                )

        if serializer.is_valid():
            # Everything is Ok
            # Set new password
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response(
                data={'detail': "Set new password."},
                status=status.HTTP_200_OK
            )

        # data is not valid
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
