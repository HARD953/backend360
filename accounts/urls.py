"""
urls.py — VisiTrack360
Routes API complètes : auth, users, entreprises, géographie, affectations.
"""
 
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
 
from .views import (
    CustomTokenObtainPairView,
    MeView,
    CustomUserViewSet,
    EntrepriseViewSet,
    AffectationAgentViewSet,
    DistrictViewSet,
    RegionViewSet,
    CommuneViewSet,
    QuartierViewSet,
    ZoneViewSet,
)
 
router = DefaultRouter()
router.register(r"users",        CustomUserViewSet,       basename="users")
router.register(r"entreprises",  EntrepriseViewSet,       basename="entreprises")
router.register(r"affectations", AffectationAgentViewSet, basename="affectations")
 
# Hiérarchie géographique
router.register(r"geo/districts", DistrictViewSet, basename="districts")
router.register(r"geo/regions",   RegionViewSet,   basename="regions")
router.register(r"geo/communes",  CommuneViewSet,  basename="communes")
router.register(r"geo/quartiers", QuartierViewSet, basename="quartiers")
router.register(r"geo/zones",     ZoneViewSet,     basename="zones")

urlpatterns = [
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]