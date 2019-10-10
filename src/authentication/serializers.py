from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers

UserModel = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            'username',
            'email',
            'password',
        )

    def validate(self, attrs):
        # validate_email(attrs['email'])
        validate_password(attrs['password'])
        return attrs


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            'id',
            'username',
            'email',
            'is_staff',
        )
        read_only_fields = ('id', 'is_staff')


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, attrs):
        validate_password(attrs['new_password'])

        # if validatable password is equals current password,
        # validation will fall
        if attrs['new_password'] == attrs['current_password']:
            raise ValidationError("Current password is equals new password.")

        return attrs

    def create(self, validated_data):
        raise NotImplementedError("You can't create password.")

    def update(self, instance, validated_data):
        raise NotImplementedError("You can't update password.")

