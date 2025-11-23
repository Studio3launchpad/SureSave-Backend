from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from users.models import CustomUser, UserProfile
from rest_framework import serializers
from django.contrib.auth import authenticate
from savingplans.models import SavingPlan, UserSavingPlan, SavingsGoal

User = CustomUser


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True, max_length=15)
    full_name = serializers.CharField(required=True, max_length=30)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists.")
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "An account with this phone number already exists.")
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

    def validate(self, attrs):
        # Use attrs (already-populated dict) instead of self.validated_data
        email_or_phone = attrs.get('email_or_phone')
        password = attrs.get('password')

        if not email_or_phone or not password:
            raise serializers.ValidationError(
                "Must include 'email_or_phone' and 'password'.")

        user = authenticate(self.context.get('request'),
                            username=email_or_phone, password=password)

        if user is None:
            raise serializers.ValidationError(
                "Unable to log in with provided credentials.")

        # Optional: check if user is active
        if not getattr(user, 'is_active', True):
            raise serializers.ValidationError("User account is disabled.")

        # Attach user to attrs for the view to use
        attrs['user'] = user
        # Map email_or_phone into expected fields so other code can read it
        # Prefer the provided email_or_phone over any explicit 'email' field
        attrs['email'] = email_or_phone
        attrs['username'] = email_or_phone
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'address', 'date_of_birth',
                  'city', 'state', 'zip_code', 'country',]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'full_name',
                  'is_verified', 'is_active', 'date_joined', 'role', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create profile
        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class SavingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingPlan
        fields = '__all__'


class UserSavingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSavingPlan
        fields = '__all__'


class SavingsGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsGoal
        fields = '__all__'
        read_only_fields = ['saved_amount', 'created_at', 'updated_at']

    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Target amount must be greater than zero.")
        return value

    def validate(self, data):
        target_date = data.get('target_date')
        if target_date and target_date <= serializers.DateField().to_representation(serializers.DateField().today()):
            raise serializers.ValidationError(
                "Target date must be in the future.")
        return data
