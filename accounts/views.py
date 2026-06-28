"""
views.py — VisiTrack360
ViewSets pour tous les modèles : auth, users, entreprises, hiérarchie géo, affectations.
"""

from rest_framework import generics, permissions, viewsets, filters, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    CustomUser,
    Entreprise,
    AffectationAgent,
    District,
    Region,
    Commune,
    Quartier,
    Zone,
)
from .serializers import (
    CustomUserSerializer,
    CustomUserCreateSerializer,
    CustomTokenObtainPairSerializer,
    EntrepriseSerializer,
    AffectationAgentSerializer,
    DistrictSerializer,
    RegionSerializer,
    CommuneSerializer,
    QuartierSerializer,
    ZoneSerializer,
)


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == CustomUser.Role.SUPERADMIN
        )


class IsSuperAdminOrReadOnly(permissions.BasePermission):
    """Lecture pour tous les authentifiés, écriture réservée au SuperAdmin."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == CustomUser.Role.SUPERADMIN


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class CustomTokenObtainPairView(TokenObtainPairView):
    """POST /api/auth/login/ — retourne access, refresh, et les infos user."""
    serializer_class = CustomTokenObtainPairSerializer


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/me/ — profil de l'utilisateur connecté."""
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---------------------------------------------------------------------------
# Users & Entreprises
# ---------------------------------------------------------------------------


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    CRUD utilisateurs — réservé aux SuperAdmin.
    GET /api/users/ | POST /api/users/ | GET/PATCH/DELETE /api/users/{id}/
    Filtres : ?role=AGENT&is_active=true&entreprise=1
    Recherche : ?search=dupont
    """
    queryset = (
        CustomUser.objects
        .select_related("entreprise")
        .prefetch_related("affectations")
        .order_by("nom", "prenom")
    )
    permission_classes = [IsSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["role", "is_active", "entreprise"]
    search_fields = ["nom", "prenom", "email"]

    def get_serializer_class(self):
        if self.action == "create":
            return CustomUserCreateSerializer
        return CustomUserSerializer

    def create(self, request, *args, **kwargs):
        """
        Crée l'utilisateur via CustomUserCreateSerializer (champ password),
        puis retourne la représentation complète via CustomUserSerializer
        (avec affectations, nomComplet, entrepriseNom…) pour que le front
        n'ait jamais de champ undefined.
        """
        write_serializer = CustomUserCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        write_serializer.is_valid(raise_exception=True)
        user = write_serializer.save()

        # Re-fetch avec les relations nécessaires au read serializer
        user = (
            CustomUser.objects
            .select_related("entreprise")
            .prefetch_related("affectations")
            .get(pk=user.pk)
        )
        read_serializer = CustomUserSerializer(user, context={"request": request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class EntrepriseViewSet(viewsets.ModelViewSet):
    """
    CRUD entreprises — réservé aux SuperAdmin.
    GET /api/entreprises/ | POST /api/entreprises/ | GET/PATCH/DELETE /api/entreprises/{id}/
    """
    queryset = Entreprise.objects.all().order_by("nom")
    serializer_class = EntrepriseSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ["nom", "sigle"]


# ---------------------------------------------------------------------------
# Hiérarchie géographique
# ---------------------------------------------------------------------------


class DistrictViewSet(viewsets.ModelViewSet):
    """
    CRUD districts.
    GET /api/geo/districts/ | POST | GET/PATCH/DELETE /api/geo/districts/{id}/
    Filtres : ?is_active=true
    Recherche : ?search=abidjan
    """
    queryset = District.objects.all().order_by("nom")
    serializer_class = DistrictSerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["is_active"]
    search_fields = ["nom", "code"]


class RegionViewSet(viewsets.ModelViewSet):
    """
    CRUD régions.
    Filtres : ?district=1&is_active=true
    """
    queryset = Region.objects.select_related("district").all().order_by("district__nom", "nom")
    serializer_class = RegionSerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["district", "is_active"]
    search_fields = ["nom", "code"]


class CommuneViewSet(viewsets.ModelViewSet):
    """
    CRUD communes.
    Filtres : ?region=1&is_active=true
    """
    queryset = (
        Commune.objects
        .select_related("region", "region__district")
        .all()
        .order_by("region__nom", "nom")
    )
    serializer_class = CommuneSerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["region", "is_active"]
    search_fields = ["nom", "code"]


class QuartierViewSet(viewsets.ModelViewSet):
    """
    CRUD quartiers.
    Filtres : ?commune=1&is_active=true
    """
    queryset = (
        Quartier.objects
        .select_related("commune")
        .all()
        .order_by("commune__nom", "nom")
    )
    serializer_class = QuartierSerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["commune", "is_active"]
    search_fields = ["nom", "code"]


class ZoneViewSet(viewsets.ModelViewSet):
    """
    CRUD zones.
    Filtres : ?quartier=1&is_active=true
    """
    queryset = (
        Zone.objects
        .select_related("quartier")
        .all()
        .order_by("quartier__nom", "nom")
    )
    serializer_class = ZoneSerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["quartier", "is_active"]
    search_fields = ["nom", "code"]


# ---------------------------------------------------------------------------
# Affectations
# ---------------------------------------------------------------------------


class AffectationAgentViewSet(viewsets.ModelViewSet):
    """
    CRUD des affectations de zones aux agents.
    GET /api/affectations/?agent=1 | POST /api/affectations/
    Filtres : ?agent=1&est_active=true
    """
    queryset = (
        AffectationAgent.objects
        .select_related(
            "agent",
            "district", "region", "commune", "quartier", "zone"
        )
        .all()
        .order_by("agent__nom")
    )
    serializer_class = AffectationAgentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["agent", "est_active"]