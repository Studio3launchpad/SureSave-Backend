from rest_framework.routers import DefaultRouter
from .views import UserAuthViewSet

router = DefaultRouter()
router.register('auth', UserAuthViewSet, basename='auth')

urlpatterns = router.urls