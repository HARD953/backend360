from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, Entreprise, AffectationAgent


class EntrepriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entreprise
        fields = ["id", "nom", "sigle", "secteur", "logo", "is_active", "cree_le"]
        read_only_fields = ["id", "cree_le"]


class AffectationAgentSerializer(serializers.ModelSerializer):
    agentNom = serializers.CharField(source="agent.nom_complet", read_only=True)
    typeZone = serializers.CharField(source="type_zone")
    valeurZone = serializers.CharField(source="valeur_zone")
    estActive = serializers.BooleanField(source="est_active")

    class Meta:
        model = AffectationAgent
        fields = ["id", "agent", "agentNom", "typeZone", "valeurZone", "estActive", "cree_le"]
        read_only_fields = ["id", "cree_le"]


class CustomUserSerializer(serializers.ModelSerializer):
    nomComplet = serializers.CharField(source="nom_complet", read_only=True)
    entrepriseNom = serializers.CharField(source="entreprise.nom", read_only=True, default=None)
    affectations = AffectationAgentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "nom",
            "prenom",
            "nomComplet",
            "telephone",
            "entreprise",
            "entrepriseNom",
            "role",
            "is_active",
            "date_joined",
            "affectations",
        ]
        read_only_fields = ["id", "date_joined"]


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "password",
            "nom",
            "prenom",
            "telephone",
            "entreprise",
            "role",
        ]

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Ajoute le rôle, l'entreprise et le nom complet dans le payload JWT,
    pour que le front affiche l'utilisateur sans appel API supplémentaire."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["nomComplet"] = user.nom_complet
        token["entrepriseId"] = user.entreprise_id
        token["entrepriseNom"] = user.entreprise.nom if user.entreprise else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = CustomUserSerializer(self.user).data
        return data