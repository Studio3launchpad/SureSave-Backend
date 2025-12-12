from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from users.models import CustomUser, UserProfile, BVN
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from payments.models import Card
from savingplans.models import (
    SavingPlan,
    UserSavingPlan,
    SavingsGoal,
    AutoSavingSchedule,
    GroupMember,
    GroupSavingPlan,
    GroupContribution,
    Wallet,
    Transaction,
)

User = CustomUser


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=15)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists.")
        return value

    # def validate_phone_number(self, value):
    #     if User.objects.filter(phone_number=value).exists():
    #         raise serializers.ValidationError(
    #             "An account with this phone number already exists.")
    #     return value

    def get_cleaned_data(self):
        """Override to clean only fields that exist."""
        return {
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
        }

    def save(self, request):
        validated_data = self.validated_data

        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password1'],
        )
        return user


class CustomLoginSerializer(LoginSerializer):
    username = None
    email_or_phone = serializers.CharField(required=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        password = attrs.get('password')

        if not email_or_phone or not password:
            raise serializers.ValidationError(
                "Must include 'email_or_phone' and 'password'."
            )

        user = authenticate(self.context.get('request'),
                            username=email_or_phone, password=password)

        if user is None:
            raise serializers.ValidationError(
                "Unable to log in with provided credentials."
            )

        if not getattr(user, 'is_active', True):
            raise serializers.ValidationError("User account is disabled.")

        # Attach user
        attrs['user'] = user
        attrs['email'] = email_or_phone
        attrs['username'] = email_or_phone

        refresh = RefreshToken.for_user(user)
        attrs['access'] = str(refresh.access_token)
        attrs['refresh'] = str(refresh)

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'address', 'date_of_birth',
                  'city', 'state', 'zip_code', 'country',]


class BvnSerializer(serializers.ModelSerializer):
    class Meta:
        model = BVN
        fields = ['id', 'bvn_number',]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number',
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
    plan = SavingPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SavingPlan.objects.all(), source="plan", write_only=True)

    class Meta:
        model = UserSavingPlan
        fields = [
            "id",
            "user",
            "plan",
            "plan_id",
            "amount",
            "current_balance",
            "start_date",
            "end_date",
            "is_active",
        ]
        read_only_fields = ("current_balance",)
        extra_kwargs = {"user": {"read_only": True}}

    def create(self, validated_data):
        # user will be set in view
        return super().create(validated_data)


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


class AutoSavingScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoSavingSchedule
        fields = "__all__"
        read_only_fields = ("created_at",)
        extra_kwargs = {"user": {"read_only": True}}

    def validate(self, attrs):
        if not attrs.get("goal") and not attrs.get("user_plan"):
            raise serializers.ValidationError(
                "Either 'goal' or 'user_plan' must be provided.")
        return attrs


class GroupMemberSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GroupMember
        fields = ("id", "user", "user_detail", "group", "role", "joined_at")
        read_only_fields = ("joined_at",)

    def get_user_detail(self, obj):
        return {"id": obj.user.id, "email": obj.user.email}


class GroupContributionSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(
        queryset=GroupMember.objects.all())
    group = serializers.PrimaryKeyRelatedField(
        queryset=GroupSavingPlan.objects.all())

    class Meta:
        model = GroupContribution
        fields = ("id", "member", "group", "amount", "date_contributed")
        read_only_fields = ("date_contributed",)

    def validate(self, data):
        # ensure member belongs to group
        member = data.get("member")
        group = data.get("group")
        if member.group_id != group.id:
            raise serializers.ValidationError(
                "Member does not belong to the provided group.")
        return data


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'currency']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'wallet', 'amount', 'type', 'reference',
            'description', 'created_at', 'receiver_wallet'
        ]
        read_only_fields = ['wallet', 'created_at']

    def validate(self, data):
        wallet = self.context['request'].user.wallet
        amount = data['amount']

        if data['type'] == 'withdrawal' and wallet.balance < amount:
            raise serializers.ValidationError("Insufficient balance.")

        if data['type'] == 'transfer':
            if 'receiver_wallet' not in data:
                raise serializers.ValidationError(
                    "Receiver wallet is required.")
            if data['receiver_wallet'] == wallet:
                raise serializers.ValidationError(
                    "You cannot transfer to yourself.")
            if wallet.balance < amount:
                raise serializers.ValidationError(
                    "Insufficient balance for transfer.")

        return data

    def create(self, validated_data):
        wallet = self.context['request'].user.wallet
        amount = validated_data['amount']
        tx_type = validated_data['type']

        # Apply wallet balance update
        if tx_type == 'deposit':
            wallet.balance += amount

        elif tx_type == 'withdrawal':
            wallet.balance -= amount

        elif tx_type == 'transfer':
            receiver_wallet = validated_data['receiver_wallet']
            wallet.balance -= amount
            receiver_wallet.balance += amount
            receiver_wallet.save()

        wallet.save()

        validated_data['wallet'] = wallet
        return super().create(validated_data)


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            'id', 'user', 'card_holder_name', 'card_number',
            'expiry_date', 'cvv', 'card_password', 'is_default',            
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']
        extra_kwargs = {
            'card_password': {'write_only': True}
        }

    def create(self, validated_data):
        raw_password = validated_data.pop('card_password')
        card = Card(**validated_data)
        card.set_card_password(raw_password)
        card.save()
        return card
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["card_number"] = f"**** **** **** {instance.card_number[-4:]}"
        return data

    
class CardVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
