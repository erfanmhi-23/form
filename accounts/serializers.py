from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import User


User = get_user_model()

class UserSerializer(ModelSerializer) :
    class Meta : 
        model = User
        fields = ('id','username','email')
    

class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class OTPWithPasswordSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    password = serializers.CharField(write_only=True, min_length=8)


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email','password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user