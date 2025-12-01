from jsonschema import ValidationError
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import (
    UserSerializer,
    SavingPlanSerializer,
    UserSavingPlanSerializer,
    SavingsGoalSerializer,
    BvnSerializer,
    GroupMemberSerializer,
    GroupContributionSerializer,
    AutoSavingScheduleSerializer,
    WalletSerializer,
    TransactionSerializer,
)
from .permissions import (
    IsOwnerOrReadOnly, 
    IsGroupAdmin, 
    IsWalletOwner, 
    IsAdminOrSelf,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
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
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from users.models import BVN

from api import serializers

User = get_user_model()

@extend_schema(tags=["User Management"])
class UserAuthViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrSelf]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        user = User.all_objects.get(pk=kwargs["pk"])
        user.delete()  # soft delete

        return Response(
            {"message": "User soft deleted successfully."},
            status=status.HTTP_200_OK
    )
@extend_schema(tags=["BVN Management"])
class BvnViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = BVN.objects.all()
    serializer_class = BvnSerializer

    def get_queryset(self):
        return BVN.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        user = self.request.user
        if BVN.objects.filter(user=user).exists():
            raise ValidationError({"detail": "BVN already submitted. You cannot create another one."})

        serializer.save(user=user, is_verified=True)

@extend_schema(tags=["Saving Plans"])
class SavingPlanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = SavingPlan.objects.all()
    serializer_class = SavingPlanSerializer
@extend_schema(tags=["User Saving Plans"])
class UserSavingPlanViewSet(viewsets.ModelViewSet):
    queryset = UserSavingPlan.objects.select_related("plan", "user").all()
    serializer_class = UserSavingPlanSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # users see only their plans; admins can see all if desired
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
@extend_schema(tags=["Savings Goals"]) 
class SavingsGoalViewSet(viewsets.ModelViewSet):
    queryset = SavingsGoal.objects.select_related("user").all().order_by("-created_at")
    serializer_class = SavingsGoalSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="contribute")
    def contribute(self, request, pk=None):
        """
        Endpoint to contribute to a goal.
        NOTE: Integrate with Transaction/Wallet system to actually move money.
        """
        goal = self.get_object()
        amount = request.data.get("amount")
        if not amount:
            return Response({"detail": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: integrate with your transaction/wallet system here
        # For now we only update saved_amount
        goal.saved_amount += float(amount)
        if goal.saved_amount >= goal.target_amount:
            goal.status = "completed"
        goal.save()
        return Response(SavingsGoalSerializer(goal).data)


# ----------------------------
# AutoSavingSchedule
# ----------------------------
@extend_schema(tags=["Auto Saving Schedules"])
class AutoSavingScheduleViewSet(viewsets.ModelViewSet):
    queryset = AutoSavingSchedule.objects.select_related("user", "goal", "user_plan").all()
    serializer_class = AutoSavingScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ----------------------------
# GroupSavingPlan + Members + Contributions
# ----------------------------
@extend_schema(tags=["Group Saving Plans"])
class GroupSavingPlanViewSet(viewsets.ModelViewSet):
    queryset = GroupSavingPlan.objects.prefetch_related("members").all().order_by("-created_at")
    serializer_class = SavingPlanSerializer 
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        
        return serializers.Serializer if self.action == "members" else SavingPlanSerializer

    def get_queryset(self):
        return GroupSavingPlan.objects.all()

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        # make creator a GroupMember admin
        GroupMember.objects.create(user=self.request.user, group=group, role="admin")

    @action(detail=True, methods=["get"], url_path="members")
    def members(self, request, pk=None):
        group = self.get_object()
        members = group.members.select_related("user").all()
        return Response(GroupMemberSerializer(members, many=True).data)

    @action(detail=True, methods=["post"], url_path="add-member")
    def add_member(self, request, pk=None):
        group = self.get_object()
        # Only group admins can add member - check
        if not group.members.filter(user=request.user, role="admin").exists():
            return Response({"detail": "Only group admins can add members."}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id required."}, status=status.HTTP_400_BAD_REQUEST)
        target_user = get_object_or_404(User, pk=user_id)

        member, created = GroupMember.objects.get_or_create(user=target_user, group=group)
        serializer = GroupMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
@extend_schema(tags=["Group Members"])
class GroupMemberViewSet(viewsets.ModelViewSet):
    queryset = GroupMember.objects.select_related("user", "group").all()
    serializer_class = GroupMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        # users can see only groups they belong to
        return self.queryset.filter(user=user)

@extend_schema(tags=["Group Contributions"])
class GroupContributionViewSet(viewsets.ModelViewSet):
    queryset = GroupContribution.objects.select_related("member", "group").all().order_by("-date_contributed")
    serializer_class = GroupContributionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Ensure user is the member who claims to contribute
        member_id = request.data.get("member")
        member = get_object_or_404(GroupMember, pk=member_id)
        if member.user != request.user:
            return Response({"detail": "You can only create contributions for yourself."}, status=status.HTTP_403_FORBIDDEN)

        # TODO: integrate with wallet/transaction before saving
        return super().create(request, *args, **kwargs) 

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def overview(self, request):
        user = request.user
        total_saving_plans = SavingPlan.objects.count()
        user_saving_plans = UserSavingPlan.objects.filter(user=user).count()
        total_savings_goals = SavingsGoal.objects.filter(user=user).count()

        data = {
            "total_saving_plans": total_saving_plans,
            "user_saving_plans": user_saving_plans,
            "total_savings_goals": total_savings_goals,
        }

        return Response(data, status=status.HTTP_200_OK)
    
@extend_schema(tags=["Wallets"])
class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def get_object(self):
        return self.request.user.wallet
@extend_schema(tags=["Transactions"]) 
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(wallet=self.request.user.wallet).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()


@extend_schema(tags=["Dashboard"])
class DashboardView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Wallet
        wallet = Wallet.objects.filter(user=user).first()
        wallet_balance = wallet.balance if wallet else 0

        # Recent Transactions
        recent_transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:5]

        # Target Savings
        #targets = TargetSaving.objects.filter(user=user)

        # Savings Plans (auto-savings)
        #auto_savings = SavingsPlan.objects.filter(user=user, is_active=True)

        # Group Savings (groups user belongs to)
        group_ids = GroupMember.objects.filter(user=user).values_list("group_id", flat=True)
        #groups = GroupSaving.objects.filter(id__in=group_ids)

        # Notifications
        #notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]

        # Upcoming Activities
        upcoming = {
            #"next_auto_save": auto_savings.first().next_run if auto_savings.exists() else None,
            #"next_target_due": targets.order_by("next_run_date").first().next_run_date if targets.exists() else None,
           # "next_group_round": groups.order_by("next_round_date").first().next_round_date if groups.exists() else None,
        }

        return Response({
            "user": {
                "name": user.get_frist_name(),
                "email": user.email,
                "bvn_verified": getattr(user, "bvn_verified", False),
            },
            "wallet": {
                "balance": wallet_balance,
                "currency": "NGN",
            },
            "transactions": TransactionSerializer(recent_transactions, many=True).data,
            # "target_savings": TargetSavingSerializer(targets, many=True).data,
            # "auto_savings": SavingsPlanSerializer(auto_savings, many=True).data,
            # "group_savings": GroupSavingSerializer(groups, many=True).data,
            # "notifications": NotificationSerializer(notifications, many=True).data,
            "upcoming": upcoming,
        })
