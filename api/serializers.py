from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from users.models import CustomUser
from rest_framework import serializers
from django.contrib.auth import authenticate

User = CustomUser

class CustomRegisterSerializer(RegisterSerializer):
    username = None 
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True, max_length=15)
    full_name = serializers.CharField(required = True, max_length=30)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("An account with this phone number already exists.")
        return value

    def get_cleaned_data(self):
        """Override to clean only fields that exist."""
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
            'full_name': self.validated_data.get('full_name', ''),
        }
    
    def save(self, request):
        user = User.objects.create_user(
            email=self.validated_data['email'],
            password=self.validated_data['password1'],
            phone_number=self.validated_data['phone_number'],
            full_name=self.validated_data['full_name'],
        )
        return user


class CustomLoginSerializer(LoginSerializer):
    """Custom login serializer that uses email field instead of username."""
    username = None

    # Make email or phone field required
    email_or_phone = serializers.CharField(required=True)

    def authenticate(self, **kwargs):
        email_or_phone = self.validated_data.get('email_or_phone')
        password = self.validated_data.get('password')

        user = authenticate(
            self.context['request'],
            username=email_or_phone,
            password=password,
        )
        return user

