from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, Entreprise, AffectationAgent
from .serializers import (
    CustomUserSerializer,
    CustomUserCreateSerializer,
    CustomTokenObtainPairSerializer,
    EntrepriseSerializer,
    AffectationAgentSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """POST /api/auth/login/ — retourne access, refresh, et les infos user."""

    serializer_class = CustomTokenObtainPairSerializer


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/me/ — profil de l'utilisateur connecté."""

    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == CustomUser.Role.SUPERADMIN
        )


class CustomUserViewSet(viewsets.ModelViewSet):
    """CRUD utilisateurs — réservé aux SuperAdmin.
    GET /api/users/ | POST /api/users/ | GET/PATCH/DELETE /api/users/{id}/
    """

    queryset = CustomUser.objects.select_related("entreprise").prefetch_related("affectations")
    permission_classes = [IsSuperAdmin]
    filterset_fields = ["role", "is_active", "entreprise"]
    search_fields = ["nom", "prenom", "email"]

    def get_serializer_class(self):
        if self.action == "create":
            return CustomUserCreateSerializer
        return CustomUserSerializer


class EntrepriseViewSet(viewsets.ModelViewSet):
    """CRUD entreprises — réservé aux SuperAdmin.
    GET /api/entreprises/ | POST /api/entreprises/ | GET/PATCH/DELETE /api/entreprises/{id}/
    """

    queryset = Entreprise.objects.all()
    serializer_class = EntrepriseSerializer
    permission_classes = [IsSuperAdmin]
    search_fields = ["nom", "sigle"]


class AffectationAgentViewSet(viewsets.ModelViewSet):
    """CRUD des affectations de zones aux agents.
    GET /api/affectations/?agent={id} | POST /api/affectations/
    """

    queryset = AffectationAgent.objects.select_related("agent").all()
    serializer_class = AffectationAgentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["agent", "type_zone", "est_active"]