import secrets
from django.utils.text import slugify
from django.db import models
from django.conf import settings


class DonneeCollectee(models.Model):
    """Support publicitaire recensé sur le terrain.
    Un même PDV (point de vente) peut accueillir plusieurs supports :
    ils partagent alors le même `pdv_reference`, mais chaque ligne
    reste indépendante (pas de synchro automatique entre supports liés).
    """

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

    # --- Regroupement PDV ---
    pdv_reference = models.SlugField(
        max_length=80,
        db_index=True,
        blank=True,
        help_text="Identifiant du PDV, partagé par tous les supports d'un même point de vente. "
        "Auto-généré à la création si absent (nouveau PDV), ou fourni par le client mobile "
        "quand l'agent rattache un support à un PDV existant (revisite).",
    )

    # --- Infos PDV (dupliquées par support, volontairement non synchronisées) ---
    Marque = models.CharField(max_length=50, blank=True)
    ville = models.CharField(max_length=50, blank=True, default="Abidjan")
    commune = models.CharField(max_length=50, blank=True, default="Abidjan")
    region = models.CharField(max_length=50, blank=True, default="Abidjan")
    district = models.CharField(max_length=50, blank=True, default="Abidjan")
    village = models.CharField(max_length=50, blank=True, default="Abidjan")
    quartier = models.CharField(max_length=50, blank=True)
    nomsite = models.CharField(max_length=50, blank=True, default="RAS")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    Rnom = models.CharField(max_length=50, blank=True)
    Rprenom = models.CharField(max_length=50, blank=True)
    Rcontact = models.CharField(max_length=50, blank=True)

    # --- Infos support (spécifiques à chaque ligne) ---
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
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Support publicitaire"
        verbose_name_plural = "Supports publicitaires"
        ordering = ["-date_collecte"]
        indexes = [models.Index(fields=["pdv_reference"])]

    def __str__(self):
        return f"{self.Marque} — {self.nomsite} ({self.commune})"

    def _generate_pdv_reference(self) -> str:
        base = slugify(f"{self.commune}-{self.quartier}-{self.nomsite}")[:60] or "pdv"
        suffix = secrets.token_hex(3)  # 6 caractères, évite les collisions
        return f"{base}-{suffix}"

    def save(self, *args, **kwargs):
        # Nouveau PDV : pas de pdv_reference fourni par le client mobile -> on le génère.
        # Revisite : le client envoie le pdv_reference existant -> on le respecte tel quel.
        if not self.pdv_reference:
            self.pdv_reference = self._generate_pdv_reference()
        super().save(*args, **kwargs)


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
    

class SimulationFiscale(models.Model):
    """Simulation du coût fiscal d'une campagne avant déploiement (section 4 du document)."""

    class Statut(models.TextChoices):
        BROUILLON = "brouillon", "Brouillon"
        VALIDE = "valide", "Validé"

    entreprise_rel = models.ForeignKey(
        "accounts.Entreprise", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="simulations"
    )
    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    nom = models.CharField(max_length=150)
    campagne = models.CharField(max_length=100, blank=True)
    marque = models.CharField(max_length=100, blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.BROUILLON)

    # Zone
    commune = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)
    district = models.CharField(max_length=50, blank=True)

    # Support
    type_support = models.CharField(max_length=50, blank=True)
    canal = models.CharField(max_length=50, blank=True)
    surface = models.FloatField(null=True, blank=True)
    duree_mois = models.IntegerField(default=12)
    quantite = models.IntegerField(default=1)

    # Fiscalité
    taux_tsp = models.FloatField(default=5.0, help_text="Taux TSP en %")
    odp_applicable = models.BooleanField(default=False)
    taxes_communales = models.BooleanField(default=True)

    # Résultats calculés
    cout_tsp = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cout_odp = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cout_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    risque_fiscal = models.CharField(
        max_length=10,
        choices=[("Faible", "Faible"), ("Moyen", "Moyen"), ("Élevé", "Élevé")],
        blank=True
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Simulation fiscale"
        verbose_name_plural = "Simulations fiscales"
        ordering = ["-cree_le"]

    def __str__(self):
        return f"{self.nom} — {self.commune}"

    def calculer(self):
        """Calcule le coût fiscal estimé et met à jour les champs calculés."""
        surface = self.surface or 0
        duree = self.duree_mois or 12
        quantite = self.quantite or 1

        # Base TSP : surface × durée × taux × quantité
        base = surface * (duree / 12) * quantite
        self.cout_tsp = round(base * self.taux_tsp * 1000, 2)

        # ODP : forfait par support par mois si applicable
        self.cout_odp = round(
            (50000 * quantite * duree) if self.odp_applicable else 0, 2
        )

        self.cout_total = float(self.cout_tsp) + float(self.cout_odp)

        # Risque fiscal selon le gap potentiel
        if self.cout_total > 5_000_000:
            self.risque_fiscal = "Élevé"
        elif self.cout_total > 1_000_000:
            self.risque_fiscal = "Moyen"
        else:
            self.risque_fiscal = "Faible"


class OrdreDeRecettes(models.Model):
    """Ordre de recettes reçu d'une collectivité (commune, région, district).
    Correspond à la section 5 du document de cadrage."""

    class TypeCollectivite(models.TextChoices):
        COMMUNE = "commune", "Commune"
        REGION = "region", "Région"
        DISTRICT = "district", "District"

    class Statut(models.TextChoices):
        RECU = "recu", "Reçu"
        EN_ANALYSE = "en_analyse", "En analyse"
        CONTESTE = "conteste", "Contesté"
        VALIDE = "valide", "Validé"
        NEGOCIE = "negocie", "Négocié"
        PAYE = "paye", "Payé"

    entreprise_rel = models.ForeignKey(
        "accounts.Entreprise", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="ordres_recettes"
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="ordres_recettes"
    )

    # Collectivité
    type_collectivite = models.CharField(
        max_length=20, choices=TypeCollectivite.choices, default=TypeCollectivite.COMMUNE
    )
    nom_collectivite = models.CharField(max_length=100)
    commune = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)
    district = models.CharField(max_length=50, blank=True)
    interlocuteur = models.CharField(max_length=100, blank=True)

    # Document
    reference = models.CharField(max_length=100, blank=True)
    date_emission = models.DateField(null=True, blank=True)
    periode_debut = models.DateField(null=True, blank=True)
    periode_fin = models.DateField(null=True, blank=True)
    piece_jointe = models.FileField(
        upload_to="ordres_recettes/", null=True, blank=True
    )

    # Montants
    montant_reclame = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    penalites = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    frais_annexes = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Supports facturés
    nombre_supports_factures = models.IntegerField(default=0)
    type_support_facture = models.CharField(max_length=50, blank=True)
    surface_facturee = models.FloatField(null=True, blank=True)
    localite_facturee = models.CharField(max_length=100, blank=True)

    # Statut & suivi
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.RECU
    )
    prochaine_action = models.CharField(max_length=255, blank=True)
    commentaire = models.TextField(blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Ordre de recettes"
        verbose_name_plural = "Ordres de recettes"
        ordering = ["-cree_le"]

    def __str__(self):
        return f"Ordre {self.reference or self.id} — {self.nom_collectivite}"

    @property
    def montant_total(self):
        return float(self.montant_reclame) + float(self.penalites) + float(self.frais_annexes)