from rest_framework.routers import DefaultRouter
from .views import (
    UserAuthViewSet,
    SavingPlanViewSet,
    UserSavingPlanViewSet,
    SavingsGoalViewSet,
    BvnViewSet,
    AutoSavingScheduleViewSet,
    GroupSavingPlanViewSet,
    GroupContributionViewSet,
    GroupMemberViewSet,
    WalletViewSet,
    TransactionViewSet,
    DashboardView,
)

router = DefaultRouter()
router.register('auth', UserAuthViewSet, basename='auth')
router.register('saving-plans', SavingPlanViewSet, basename='saving-plans')
router.register('user-saving-plans', UserSavingPlanViewSet, basename='user-saving-plans')
router.register('savings-goals', SavingsGoalViewSet, basename='savings-goals')
router.register('bvns', BvnViewSet, basename='bvns')
router.register('auto-saving-schedules', AutoSavingScheduleViewSet, basename='auto-saving-schedules')
router.register('group-saving-plans', GroupSavingPlanViewSet, basename='group-saving-plans')
router.register('group-contributions', GroupContributionViewSet, basename='group-contributions')
router.register('group-members', GroupMemberViewSet, basename='group-members')
router.register('wallets', WalletViewSet, basename='wallets')
router.register('transactions', TransactionViewSet, basename='transactions')
router.register('dashboardView', DashboardView, basename='dashboards')


urlpatterns = router.urls