from rest_framework import serializers
from .models import *


# ---------------------------------------------------------------------------
# Supports publicitaires (DonneeCollectee)
# ---------------------------------------------------------------------------

class SupportPublicitaireSerializer(serializers.ModelSerializer):
    """Sérialise DonneeCollectee avec des noms de champs alignés sur le front
    (camelCase, cohérent avec SupportPublicitaire dans types/dashboard.ts)."""

    marque = serializers.CharField(source="Marque")
    nomSite = serializers.CharField(source="nomsite")
    typeSupport = serializers.CharField(source="type_support")
    nombreFace = serializers.FloatField(source="nombre_face")
    nombreSupport = serializers.FloatField(source="nombre_support")
    surfaceODP = serializers.FloatField()
    etatSupport = serializers.CharField(source="etat_support")
    typeSite = serializers.CharField(source="typesite")
    agentNom = serializers.SerializerMethodField()
    responsableNom = serializers.CharField(source="Rnom")
    responsablePrenom = serializers.CharField(source="Rprenom")
    responsableContact = serializers.CharField(source="Rcontact")
    signataireNom = serializers.CharField(source="Snom")
    signatairePrenom = serializers.CharField(source="Sprenom")
    signataireContact = serializers.CharField(source="Scontact")
    tsp = serializers.FloatField(source="TSP")
    odp = serializers.BooleanField(source="ODP")
    odpValue = serializers.FloatField(source="ODP_value")
    ap = serializers.BooleanField(source="AP")
    apa = serializers.BooleanField(source="APA")
    apt = serializers.BooleanField(source="APT")
    ae = serializers.BooleanField(source="AE")
    aea = serializers.BooleanField(source="AEA")
    aet = serializers.BooleanField(source="AET")
    tauxCommune = serializers.BooleanField()
    tauxRegion = serializers.BooleanField()
    tauxDistrict = serializers.BooleanField()
    dateCollecte = serializers.DateTimeField(source="date_collecte", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    isDeleted = serializers.BooleanField(source="is_deleted")
    imageSupport = serializers.ImageField(source="image_support", required=False, allow_null=True)
    imageSupportSecondaire = serializers.ImageField(
        source="image_support_s", required=False, allow_null=True
    )

    class Meta:
        model = DonneeCollectee
        fields = [
            "id",
            "marque",
            "entreprise",
            "entreprise_rel",
            "agent",
            "agentNom",
            "ville",
            "commune",
            "region",
            "district",
            "village",
            "quartier",
            "nomSite",
            "latitude",
            "longitude",
            "typeSupport",
            "surface",
            "nombreSupport",
            "nombreFace",
            "surfaceODP",
            "canal",
            "etatSupport",
            "typeSite",
            "visibilite",
            "description",
            "observation",
            "responsableNom",
            "responsablePrenom",
            "responsableContact",
            "signataireNom",
            "signatairePrenom",
            "signataireContact",
            "duree",
            "anciennete",
            "tsp",
            "odp",
            "odpValue",
            "ap",
            "apa",
            "apt",
            "ae",
            "aea",
            "aet",
            "tauxCommune",
            "tauxRegion",
            "tauxDistrict",
            "imageSupport",
            "imageSupportSecondaire",
            "dateCollecte",
            "updatedAt",
            "isDeleted",
        ]
        read_only_fields = ["id", "entreprise_rel"]

    def get_agentNom(self, obj):
        return obj.agent.nom_complet if obj.agent else None


class SupportMapPointSerializer(serializers.ModelSerializer):
    """Version allégée pour l'affichage carte : uniquement les champs nécessaires
    au rendu des pins, pour éviter de transférer 40 champs par support sur de gros volumes."""

    nomSite = serializers.CharField(source="nomsite")
    marque = serializers.CharField(source="Marque")
    typeSupport = serializers.CharField(source="type_support")
    etatSupport = serializers.CharField(source="etat_support")

    class Meta:
        model = DonneeCollectee
        fields = ["id", "nomSite", "marque", "typeSupport", "etatSupport", "commune", "latitude", "longitude"]


# ---------------------------------------------------------------------------
# Négociations
# ---------------------------------------------------------------------------

class ArgumentairePretSerializer(serializers.ModelSerializer):
    iconKey = serializers.CharField(source="motif")
    label = serializers.CharField(source="get_motif_display", read_only=True)

    class Meta:
        model = ArgumentairePret
        fields = ["id", "iconKey", "label", "negociation"]


class NegociationSerializer(serializers.ModelSerializer):
    montantInitial = serializers.DecimalField(
        source="montant_initial", max_digits=14, decimal_places=2
    )
    montantRecalcule = serializers.DecimalField(
        source="montant_recalcule", max_digits=14, decimal_places=2
    )
    montantNegocie = serializers.DecimalField(
        source="montant_negocie", max_digits=14, decimal_places=2, allow_null=True
    )
    economie = serializers.SerializerMethodField()
    nextAction = serializers.SerializerMethodField()

    class Meta:
        model = Negociation
        fields = [
            "id",
            "commune",
            "entreprise",
            "entreprise_rel",
            "montantInitial",
            "montantRecalcule",
            "montantNegocie",
            "economie",
            "nextAction",
        ]
        read_only_fields = ["entreprise_rel"]

    def get_economie(self, obj):
        return obj.economie

    def get_nextAction(self, obj):
        if not obj.type_prochaine_action:
            return None
        date_str = (
            obj.date_prochaine_action.strftime("%d/%m/%Y")
            if obj.date_prochaine_action
            else ""
        )
        label_map = {
            "reunion": f"Réunion - {date_str}",
            "argumentaire": f"Envoi d'argumentaire - {date_str}",
            "relance": f"Relance - {date_str}",
        }
        return {
            "type": obj.type_prochaine_action,
            "label": label_map.get(obj.type_prochaine_action, date_str),
        }


# ---------------------------------------------------------------------------
# Dossiers fiscaux & alertes
# ---------------------------------------------------------------------------

class DossierFiscalSerializer(serializers.ModelSerializer):
    fiscaliteEstimee = serializers.DecimalField(
        source="fiscalite_estimee", max_digits=14, decimal_places=2
    )
    montantReclame = serializers.DecimalField(
        source="montant_reclame", max_digits=14, decimal_places=2
    )
    gapPotentiel = serializers.SerializerMethodField()

    class Meta:
        model = DossierFiscal
        fields = ["id", "commune", "entreprise_rel", "fiscaliteEstimee", "montantReclame", "gapPotentiel"]
        read_only_fields = ["entreprise_rel"]

    def get_gapPotentiel(self, obj):
        return obj.gap_potentiel


class AlertePrioritaireSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="titre")
    severity = serializers.CharField(source="severite")
    timeAgo = serializers.SerializerMethodField()

    class Meta:
        model = AlertePrioritaire
        fields = ["id", "title", "description", "severity", "commune", "timeAgo", "est_traitee"]

    def get_timeAgo(self, obj):
        from django.utils.timesince import timesince

        return f"Il y a {timesince(obj.cree_le)}"


# ---------------------------------------------------------------------------
# Activité & Agents
# ---------------------------------------------------------------------------

class ActivityLogSerializer(serializers.ModelSerializer):
    description = serializers.CharField()
    type = serializers.CharField(source="type_activite")
    timeAgo = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ["id", "description", "type", "timeAgo"]

    def get_timeAgo(self, obj):
        from django.utils.timesince import timesince

        return f"Il y a {timesince(obj.cree_le)}"


class AgentRecenseurSerializer(serializers.Serializer):
    """Vue agrégée d'un agent : identité + statistiques de collecte.
    Construit manuellement (pas un ModelSerializer) car il combine CustomUser
    et des agrégats calculés sur DonneeCollectee."""

    id = serializers.IntegerField()
    nomComplet = serializers.CharField()
    email = serializers.EmailField()
    telephone = serializers.CharField()
    supportsCollectes = serializers.IntegerField()
    derniereActivite = serializers.DateTimeField(allow_null=True)
    affectations = serializers.ListField(child=serializers.CharField())

class SimulationFiscaleSerializer(serializers.ModelSerializer):
    coutTSP = serializers.DecimalField(source="cout_tsp", max_digits=14, decimal_places=2)
    coutODP = serializers.DecimalField(source="cout_odp", max_digits=14, decimal_places=2)
    coutTotal = serializers.DecimalField(source="cout_total", max_digits=14, decimal_places=2)
    riqueFiscal = serializers.CharField(source="risque_fiscal")
    dureesMois = serializers.IntegerField(source="duree_mois")
    tauxTSP = serializers.FloatField(source="taux_tsp")
    odpApplicable = serializers.BooleanField(source="odp_applicable")
    taxesCommunales = serializers.BooleanField(source="taxes_communales")
    typeSupport = serializers.CharField(source="type_support")
    creeLe = serializers.DateTimeField(source="cree_le", read_only=True)

    class Meta:
        model = SimulationFiscale
        fields = [
            "id", "nom", "campagne", "marque", "statut",
            "commune", "region", "district",
            "typeSupport", "canal", "surface", "dureesMois", "quantite",
            "tauxTSP", "odpApplicable", "taxesCommunales",
            "coutTSP", "coutODP", "coutTotal", "riqueFiscal",
            "creeLe",
        ]
        read_only_fields = ["id", "coutTSP", "coutODP", "coutTotal", "riqueFiscal", "creeLe"]


class OrdreDeRecettesSerializer(serializers.ModelSerializer):
    montantReclame = serializers.DecimalField(source="montant_reclame", max_digits=14, decimal_places=2)
    penalites = serializers.DecimalField(max_digits=14, decimal_places=2)
    fraisAnnexes = serializers.DecimalField(source="frais_annexes", max_digits=14, decimal_places=2)
    montantTotal = serializers.SerializerMethodField()
    typeCollectivite = serializers.CharField(source="type_collectivite")
    nomCollectivite = serializers.CharField(source="nom_collectivite")
    dateEmission = serializers.DateField(source="date_emission", allow_null=True)
    periodeDebut = serializers.DateField(source="periode_debut", allow_null=True)
    periodeFin = serializers.DateField(source="periode_fin", allow_null=True)
    nombreSupportsFactures = serializers.IntegerField(source="nombre_supports_factures")
    typeSupportFacture = serializers.CharField(source="type_support_facture")
    surfaceFacturee = serializers.FloatField(source="surface_facturee", allow_null=True)
    localiteFacturee = serializers.CharField(source="localite_facturee")
    prochaineAction = serializers.CharField(source="prochaine_action")
    pieceJointe = serializers.FileField(source="piece_jointe", required=False, allow_null=True)
    responsableNom = serializers.SerializerMethodField()
    creeLe = serializers.DateTimeField(source="cree_le", read_only=True)
    modifieLe = serializers.DateTimeField(source="modifie_le", read_only=True)

    class Meta:
        model = OrdreDeRecettes
        fields = [
            "id", "typeCollectivite", "nomCollectivite",
            "commune", "region", "district", "interlocuteur",
            "reference", "dateEmission", "periodeDebut", "periodeFin",
            "pieceJointe",
            "montantReclame", "penalites", "fraisAnnexes", "montantTotal",
            "nombreSupportsFactures", "typeSupportFacture",
            "surfaceFacturee", "localiteFacturee",
            "statut", "prochaineAction", "commentaire",
            "responsable", "responsableNom",
            "creeLe", "modifieLe",
        ]
        read_only_fields = ["id", "montantTotal", "creeLe", "modifieLe"]

    def get_montantTotal(self, obj):
        return obj.montant_total

    def get_responsableNom(self, obj):
        return obj.responsable.nom_complet if obj.responsable else None