from django.conf import settings
from django.db import models


class DonneeCollectee(models.Model):
    """Support publicitaire recensé sur le terrain. Modèle fourni par le client,
    conservé tel quel pour rester compatible avec l'app mobile de collecte existante."""

    class EtatSupport(models.TextChoices):
        BON = "Bon", "Bon"
        DEFRAICHI = "Défraichi", "Défraichi"
        DETERIORE = "Détérioré", "Détérioré"

    agent = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    entreprise_rel = models.ForeignKey(
        "accounts.Entreprise",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="supports",
        help_text="Entreprise propriétaire (isolation multi-tenant). "
        "Le champ 'entreprise' texte ci-dessous reste conservé pour compatibilité avec l'app mobile.",
    )
    entreprise = models.CharField(max_length=50, blank=True)
    Marque = models.CharField(max_length=50, blank=True)
    ville = models.CharField(max_length=50, blank=True, default="Abidjan")
    commune = models.CharField(max_length=50, blank=True, default="Abidjan")
    region = models.CharField(max_length=50, blank=True, default="Abidjan")
    district = models.CharField(max_length=50, blank=True, default="Abidjan")
    village = models.CharField(max_length=50, blank=True, default="Abidjan")
    quartier = models.CharField(max_length=50, blank=True)
    nomsite = models.CharField(max_length=50, blank=True, default="RAS")
    type_support = models.CharField(max_length=50, blank=True)
    surface = models.FloatField(blank=True, null=True)
    nombre_support = models.FloatField(blank=True, null=True)
    nombre_face = models.FloatField(blank=True, null=True)
    surfaceODP = models.FloatField(blank=True, null=True)
    canal = models.CharField(max_length=50, blank=True)
    etat_support = models.CharField(max_length=50, blank=True, choices=EtatSupport.choices)
    typesite = models.CharField(max_length=50, blank=True)
    visibilite = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=50, blank=True)
    observation = models.CharField(max_length=50, blank=True)
    date_collecte = models.DateTimeField(auto_now_add=True, blank=True)
    image_support = models.ImageField(upload_to="collecte_images/", null=True, blank=True)
    image_support_s = models.ImageField(upload_to="collecte_images/", null=True, blank=True)
    signature = models.ImageField(upload_to="collecte_images/", null=True, blank=True)
    signature1 = models.ImageField(upload_to="collecte_images/", null=True, blank=True)
    Rnom = models.CharField(max_length=50, blank=True)
    Rprenom = models.CharField(max_length=50, blank=True)
    Rcontact = models.CharField(max_length=50, blank=True)
    Snom = models.CharField(max_length=50, blank=True)
    Sprenom = models.CharField(max_length=50, blank=True)
    Scontact = models.CharField(max_length=50, blank=True)
    duree = models.FloatField(blank=True, null=True)
    anciennete = models.BooleanField(default=False, blank=True)
    TSP = models.FloatField(blank=True, null=True)
    ODP = models.BooleanField(default=False, blank=True)
    AP = models.BooleanField(default=False, blank=True)
    APA = models.BooleanField(default=False, blank=True)
    APT = models.BooleanField(default=False, blank=True)
    AE = models.BooleanField(default=False, blank=True)
    AEA = models.BooleanField(default=False, blank=True)
    AET = models.BooleanField(default=False, blank=True)
    tauxCommune = models.BooleanField(default=False, blank=True)
    tauxRegion = models.BooleanField(default=False, blank=True)
    tauxDistrict = models.BooleanField(default=False, blank=True)
    ODP_value = models.FloatField(blank=True, null=True)
    create = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Support publicitaire"
        verbose_name_plural = "Supports publicitaires"
        ordering = ["-date_collecte"]

    def __str__(self):
        return f"{self.Marque} — {self.nomsite} ({self.commune})"


class Negociation(models.Model):
    """Dossier de négociation fiscale par commune (Dashboard Négociations & Économies)."""

    class TypeProchaineAction(models.TextChoices):
        REUNION = "reunion", "Réunion"
        ARGUMENTAIRE = "argumentaire", "Envoi d'argumentaire"
        RELANCE = "relance", "Relance"

    entreprise_rel = models.ForeignKey(
        "accounts.Entreprise",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="negociations",
    )
    entreprise = models.CharField(max_length=100, blank=True)
    commune = models.CharField(max_length=50)
    montant_initial = models.DecimalField(max_digits=14, decimal_places=2)
    montant_recalcule = models.DecimalField(max_digits=14, decimal_places=2)
    montant_negocie = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    type_prochaine_action = models.CharField(
        max_length=20, choices=TypeProchaineAction.choices, blank=True
    )
    date_prochaine_action = models.DateTimeField(null=True, blank=True)

    agent_responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Négociation"
        verbose_name_plural = "Négociations"
        ordering = ["-cree_le"]

    def __str__(self):
        return f"Négociation {self.commune} — {self.montant_negocie or self.montant_initial} FCFA"

    @property
    def economie(self):
        if self.montant_negocie is None:
            return None
        return self.montant_initial - self.montant_negocie

    @property
    def taux_reduction(self):
        if not self.montant_initial or self.montant_negocie is None:
            return None
        return round((1 - (self.montant_negocie / self.montant_initial)) * 100, 1)


class ArgumentairePret(models.Model):
    """Compteur de dossiers prêts à argumenter, par motif (Supports absents, Doublons...)."""

    class Motif(models.TextChoices):
        SUPPORTS_ABSENTS = "absent", "Supports absents"
        DOUBLONS = "doublon", "Doublons"
        MAUVAISE_PERIODE = "periode", "Mauvaise période"
        MAUVAISE_SURFACE = "surface", "Mauvaise surface"

    negociation = models.ForeignKey(
        Negociation, related_name="argumentaires", on_delete=models.CASCADE
    )
    motif = models.CharField(max_length=20, choices=Motif.choices)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Argumentaire prêt"
        verbose_name_plural = "Argumentaires prêts"

    def __str__(self):
        return f"{self.get_motif_display()} — {self.negociation.commune}"


class DossierFiscal(models.Model):
    """Dossier de suivi fiscal global par commune (alimente le Dashboard Exécutif :
    fiscalité estimée, montant réclamé, gap potentiel)."""

    entreprise_rel = models.ForeignKey(
        "accounts.Entreprise",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="dossiers_fiscaux",
    )
    commune = models.CharField(max_length=50)
    fiscalite_estimee = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    montant_reclame = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dossier fiscal"
        verbose_name_plural = "Dossiers fiscaux"
        ordering = ["-montant_reclame"]

    def __str__(self):
        return f"Dossier fiscal {self.commune}"

    @property
    def gap_potentiel(self):
        return self.montant_reclame - self.fiscalite_estimee


class AlertePrioritaire(models.Model):
    """Alerte affichée sur le Dashboard Exécutif (écarts fiscaux, supports à vérifier...)."""

    class Severite(models.TextChoices):
        ELEVEE = "Élevée", "Élevée"
        MOYENNE = "Moyenne", "Moyenne"
        FAIBLE = "Faible", "Faible"

    entreprise_rel = models.ForeignKey(
        "accounts.Entreprise",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="alertes",
    )
    titre = models.CharField(max_length=150)
    description = models.CharField(max_length=255, blank=True)
    severite = models.CharField(max_length=10, choices=Severite.choices)
    commune = models.CharField(max_length=50, blank=True)
    est_traitee = models.BooleanField(default=False)

    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Alerte prioritaire"
        verbose_name_plural = "Alertes prioritaires"
        ordering = ["-cree_le"]

    def __str__(self):
        return self.titre


class ActivityLog(models.Model):
    """Journal d'activité, alimente 'Activité récente' du Dashboard Exécutif
    et l'historique d'un agent. Créé automatiquement par les vues (pas de saisie manuelle)."""

    class ActivityType(models.TextChoices):
        SUCCESS = "success", "Succès"
        INFO = "info", "Information"
        WARNING = "warning", "Avertissement"

    entreprise_rel = models.ForeignKey(
        "accounts.Entreprise",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activites",
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    description = models.CharField(max_length=255)
    type_activite = models.CharField(
        max_length=10, choices=ActivityType.choices, default=ActivityType.INFO
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activité"
        verbose_name_plural = "Activités"
        ordering = ["-cree_le"]

    def __str__(self):
        return self.description