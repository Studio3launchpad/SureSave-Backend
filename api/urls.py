from rest_framework.routers import DefaultRouter
from .views import (
    UserAuthViewSet,
    SavingPlanViewSet,
    UserSavingPlanViewSet,
    SavingsGoalViewSet,
)

router = DefaultRouter()
router.register('auth', UserAuthViewSet, basename='auth')
router.register('saving-plans', SavingPlanViewSet, basename='saving-plans')
router.register('user-saving-plans', UserSavingPlanViewSet, basename='user-saving-plans')
router.register('savings-goals', SavingsGoalViewSet, basename='savings-goals')

urlpatterns = router.urls