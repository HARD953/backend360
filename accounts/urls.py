from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView,
    MeView,
    CustomUserViewSet,
    EntrepriseViewSet,
    AffectationAgentViewSet,
)

router = DefaultRouter()
router.register("users", CustomUserViewSet, basename="user")
router.register("entreprises", EntrepriseViewSet, basename="entreprise")
router.register("affectations", AffectationAgentViewSet, basename="affectation")

urlpatterns = [
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]