from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import (
    UserSerializer,
    SavingPlanSerializer,
    UserSavingPlanSerializer,
    SavingsGoalSerializer,
)
from django.contrib.auth import get_user_model
from savingplans.models import SavingPlan, UserSavingPlan, SavingsGoal

User = get_user_model()


class UserAuthViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        user = User.all_objects.get(pk=kwargs["pk"])
        user.delete()  # soft delete

        return Response(
            {"message": "User soft deleted successfully."},
            status=status.HTTP_200_OK
    )


class SavingPlanViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SavingPlan.objects.all()
    serializer_class = SavingPlanSerializer

class UserSavingPlanViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserSavingPlan.objects.all()
    serializer_class = UserSavingPlanSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
class SavingsGoalViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SavingsGoal.objects.all()
    serializer_class = SavingsGoalSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)