"""
serializers.py — VisiTrack360
Serializers pour tous les modèles : hiérarchie géo, users, entreprises, affectations.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    CustomUser,
    Entreprise,
    AffectationAgent,
    District,
    Region,
    Commune,
    Quartier,
    Zone,
    SupportPublicitaire,
    Site,
    Canal,
    Marque, 
    Etat, 
    Visibilite
)


# ===========================================================================
# Auth
# ===========================================================================


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Enrichit le token JWT avec les infos utilisateur."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["user"] = {
            "id": user.id,
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom,
            "nomComplet": user.nom_complet,
            "telephone": user.telephone,
            "role": user.role,
            "is_active": user.is_active,
            "entreprise": user.entreprise_id,
            "entrepriseNom": user.entreprise.nom if user.entreprise else None,
            "date_joined": user.date_joined,
        }
        return data


# ===========================================================================
# Entreprise
# ===========================================================================


class EntrepriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entreprise
        fields = ["id", "nom", "sigle", "secteur", "logo", "is_active", "cree_le"]
        read_only_fields = ["id", "cree_le"]


# ===========================================================================
# Hiérarchie géographique
# ===========================================================================

TAUX_FIELDS = [
    "taux_odp", "taux_tsp", "taux_ap", "taux_apa",
    "taux_apt", "taux_ae", "taux_aea", "taux_aet",
]


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ["id", "nom", "code", "is_active", "cree_le", "updated_at"] + TAUX_FIELDS
        read_only_fields = ["id", "cree_le", "updated_at"]


class DistrictLightSerializer(serializers.ModelSerializer):
    """Version légère pour les selects imbriqués."""
    class Meta:
        model = District
        fields = ["id", "nom", "code"]


class RegionSerializer(serializers.ModelSerializer):
    district_nom = serializers.CharField(source="district.nom", read_only=True)

    class Meta:
        model = Region
        fields = ["id", "district", "district_nom", "nom", "code", "is_active", "cree_le", "updated_at"] + TAUX_FIELDS
        read_only_fields = ["id", "district_nom", "cree_le", "updated_at"]


class RegionLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["id", "nom", "code", "district"]


class CommuneSerializer(serializers.ModelSerializer):
    region_nom = serializers.CharField(source="region.nom", read_only=True)
    district_nom = serializers.CharField(source="region.district.nom", read_only=True)

    class Meta:
        model = Commune
        fields = ["id", "region", "region_nom", "district_nom", "nom", "code", "is_active", "cree_le", "updated_at"] + TAUX_FIELDS
        read_only_fields = ["id", "region_nom", "district_nom", "cree_le", "updated_at"]


class CommuneLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        fields = ["id", "nom", "code", "region"]


class QuartierSerializer(serializers.ModelSerializer):
    commune_nom = serializers.CharField(source="commune.nom", read_only=True)

    class Meta:
        model = Quartier
        fields = ["id", "commune", "commune_nom", "nom", "code", "is_active", "cree_le", "updated_at"]
        read_only_fields = ["id", "commune_nom", "cree_le", "updated_at"]


class QuartierLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quartier
        fields = ["id", "nom", "code", "commune"]


class ZoneSerializer(serializers.ModelSerializer):
    quartier_nom = serializers.CharField(source="quartier.nom", read_only=True)

    class Meta:
        model = Zone
        fields = ["id", "quartier", "quartier_nom", "nom", "code", "is_active", "cree_le", "updated_at"]
        read_only_fields = ["id", "quartier_nom", "cree_le", "updated_at"]


# ===========================================================================
# AffectationAgent
# ===========================================================================


class AffectationAgentSerializer(serializers.ModelSerializer):
    """
    Lecture : expose type_zone et valeur_zone comme propriétés calculées.
    Écriture : accepte une seule FK parmi district/region/commune/quartier/zone.
    """

    # Champs calculés (read-only)
    typeZone = serializers.CharField(source="type_zone", read_only=True)
    valeurZone = serializers.CharField(source="valeur_zone", read_only=True)

    # Noms lisibles des zones (read-only, pour affichage)
    district_nom = serializers.CharField(source="district.nom", read_only=True, default=None)
    region_nom = serializers.CharField(source="region.nom", read_only=True, default=None)
    commune_nom = serializers.CharField(source="commune.nom", read_only=True, default=None)
    quartier_nom = serializers.CharField(source="quartier.nom", read_only=True, default=None)
    zone_nom = serializers.CharField(source="zone.nom", read_only=True, default=None)

    class Meta:
        model = AffectationAgent
        fields = [
            "id", "agent",
            "district", "district_nom",
            "region", "region_nom",
            "commune", "commune_nom",
            "quartier", "quartier_nom",
            "zone", "zone_nom",
            "typeZone", "valeurZone",
            "est_active", "cree_le", "updated_at",
        ]
        read_only_fields = ["id", "typeZone", "valeurZone", "cree_le", "updated_at"]

    def validate(self, attrs):
        """Exactement une FK géographique doit être renseignée."""
        geo_fields = ["district", "region", "commune", "quartier", "zone"]
        provided = [f for f in geo_fields if attrs.get(f) is not None]

        # En mode PATCH, récupérer les valeurs existantes de l'instance
        if self.instance:
            for f in geo_fields:
                if f not in attrs:
                    if getattr(self.instance, f"{f}_id") is not None:
                        provided.append(f)

        if len(provided) == 0:
            raise serializers.ValidationError("Au moins une zone géographique doit être renseignée.")
        if len(provided) > 1:
            raise serializers.ValidationError(
                f"Une seule zone géographique par affectation. Reçu : {', '.join(provided)}"
            )
        return attrs


# ===========================================================================
# CustomUser
# ===========================================================================


class AffectationLightSerializer(serializers.ModelSerializer):
    """Version allégée pour l'imbrication dans CustomUserSerializer."""

    typeZone = serializers.CharField(source="type_zone", read_only=True)
    valeurZone = serializers.CharField(source="valeur_zone", read_only=True)

    class Meta:
        model = AffectationAgent
        fields = ["id", "typeZone", "valeurZone", "est_active"]


class CustomUserSerializer(serializers.ModelSerializer):
    nomComplet = serializers.CharField(source="nom_complet", read_only=True)
    entrepriseNom = serializers.CharField(source="entreprise.nom", read_only=True, default=None)
    affectations = AffectationLightSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id", "email", "nom", "prenom", "nomComplet",
            "telephone", "entreprise", "entrepriseNom",
            "role", "is_active", "date_joined", "affectations",
        ]
        read_only_fields = ["id", "nomComplet", "entrepriseNom", "date_joined", "affectations"]


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer d'écriture uniquement.
    La réponse POST est re-sérialisée via CustomUserSerializer
    (voir CustomUserViewSet.create) pour inclure affectations, nomComplet, etc.
    """

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            "id", "email", "password", "nom", "prenom",
            "telephone", "entreprise", "role", "is_active",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

 
class SupportPublicitaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportPublicitaire
        fields = [
            "id", "entreprise", "type_support",
            "nombre_face", "surface",
            "create", "updated_at",
        ]
        read_only_fields = ["id", "create", "updated_at"]
 
 
class MarqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marque
        fields = [
            "id", "entreprise", "marque",
            "surface", "create", "updated_at",
        ]
        read_only_fields = ["id", "create", "updated_at"]
 
 
class CanalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canal
        fields = ["id", "canal", "create", "updated_at"]
        read_only_fields = ["id", "create", "updated_at"]
 
 
class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ["id", "site", "create", "updated_at"]
        read_only_fields = ["id", "create", "updated_at"]
 
 
class EtatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etat
        fields = ["id", "etat", "create", "updated_at"]
        read_only_fields = ["id", "create", "updated_at"]
 
 
class VisibiliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visibilite
        fields = ["id", "visibilite", "create", "updated_at"]
        read_only_fields = ["id", "create", "updated_at"]
 

