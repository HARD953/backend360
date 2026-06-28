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
    # Auth
    path("auth/login/",   CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(),          name="token_refresh"),
    path("auth/me/",      MeView.as_view(),                    name="me"),

    # Tous les ViewSets
    path("", include(router.urls)),
]

# Résumé des endpoints générés :
#
# POST   /api/auth/login/
# POST   /api/auth/refresh/
# GET    /api/auth/me/
# PATCH  /api/auth/me/
#
# GET    /api/users/               ?role=&is_active=&entreprise=&search=
# POST   /api/users/
# GET    /api/users/{id}/
# PATCH  /api/users/{id}/
# DELETE /api/users/{id}/
#
# GET    /api/entreprises/         ?search=
# POST   /api/entreprises/
# GET    /api/entreprises/{id}/
# PATCH  /api/entreprises/{id}/
# DELETE /api/entreprises/{id}/
#
# GET    /api/affectations/        ?agent=&est_active=
# POST   /api/affectations/
# GET    /api/affectations/{id}/
# PATCH  /api/affectations/{id}/
# DELETE /api/affectations/{id}/
#
# GET    /api/geo/districts/       ?is_active=&search=
# POST   /api/geo/districts/
# GET    /api/geo/districts/{id}/
# PATCH  /api/geo/districts/{id}/
# DELETE /api/geo/districts/{id}/
#
# GET    /api/geo/regions/         ?district=&is_active=&search=
# POST   /api/geo/regions/
# GET    /api/geo/regions/{id}/
# PATCH  /api/geo/regions/{id}/
# DELETE /api/geo/regions/{id}/
#
# GET    /api/geo/communes/        ?region=&is_active=&search=
# POST   /api/geo/communes/
# GET    /api/geo/communes/{id}/
# PATCH  /api/geo/communes/{id}/
# DELETE /api/geo/communes/{id}/
#
# GET    /api/geo/quartiers/       ?commune=&is_active=&search=
# POST   /api/geo/quartiers/
# GET    /api/geo/quartiers/{id}/
# PATCH  /api/geo/quartiers/{id}/
# DELETE /api/geo/quartiers/{id}/
#
# GET    /api/geo/zones/           ?quartier=&is_active=&search=
# POST   /api/geo/zones/
# GET    /api/geo/zones/{id}/
# PATCH  /api/geo/zones/{id}/
# DELETE /api/geo/zones/{id}/