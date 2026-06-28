"""
models.py — VisiTrack360
Hiérarchie géographique : District > Région > Commune > Quartier > Zone
Chaque niveau porte ses propres taux fiscaux (ODP, TSP, AP, AE…).
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models


# ===========================================================================
# Entreprise
# ===========================================================================

class Entreprise(models.Model):
    nom       = models.CharField(max_length=100, unique=True)
    sigle     = models.CharField(max_length=20, blank=True)
    secteur   = models.CharField(max_length=100, blank=True)
    logo      = models.ImageField(upload_to="entreprises/logos/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    cree_le   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


# ===========================================================================
# Référentiels publicitaires (inchangés)
# ===========================================================================

class SupportPublicitaire(models.Model):
    entreprise   = models.CharField(max_length=50, blank=True)
    type_support = models.CharField(max_length=50)
    nombre_face  = models.FloatField(blank=True, null=True)
    surface      = models.FloatField(blank=True, null=True)
    create       = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Support publicitaire"
        verbose_name_plural = "Supports publicitaires"

    def __str__(self):
        return self.type_support


class Taux(models.Model):
    TTAP  = models.CharField(max_length=50)
    TTPAT = models.CharField(max_length=50)
    TAE   = models.CharField(max_length=50)
    TAEAT = models.CharField(max_length=50)

    def __str__(self):
        return f"Taux #{self.pk} — TTAP={self.TTAP}"


class Marque(models.Model):
    entreprise = models.CharField(max_length=50, blank=True)
    marque     = models.CharField(max_length=50)
    surface    = models.CharField(max_length=50, blank=True)
    create     = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.marque


class Canal(models.Model):
    canal      = models.CharField(max_length=50)
    create     = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.canal


class Site(models.Model):
    site       = models.CharField(max_length=50)
    create     = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site


class Etat(models.Model):
    etat       = models.CharField(max_length=50)
    create     = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.etat


class Visibilite(models.Model):
    visibilite = models.CharField(max_length=50)
    create     = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.visibilite


# ===========================================================================
# Mixin taux fiscaux — partagé par District, Région et Commune
# ===========================================================================

class TauxFiscauxMixin(models.Model):
    """
    Taux fiscaux communs (en %). Nullable = héritage du niveau supérieur
    si non défini localement (logique à implémenter dans le serializer).
    """
    taux_odp = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name="Taux ODP (%)", help_text="Occupation du Domaine Public",
    )
    taux_tsp = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name="Taux TSP (%)", help_text="Taxe sur Support Publicitaire",
    )
    taux_ap  = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name="Taux AP (%)", help_text="Affichage Publicitaire",
    )
    taux_apa = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name="Taux APA (%)", help_text="Affichage Publicitaire Animé",
    )
    taux_apt = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name="Taux APT (%)", help_text="Affichage Publicitaire Temporaire",
    )
    taux_ae  = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name="Taux AE (%)", help_text="Affichage Électronique",
    )
    taux_aea = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name="Taux AEA (%)", help_text="Affichage Électronique Animé",
    )
    taux_aet = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name="Taux AET (%)", help_text="Affichage Électronique Temporaire",
    )

    class Meta:
        abstract = True


# ===========================================================================
# Hiérarchie géographique stricte avec FK
# ===========================================================================

class District(TauxFiscauxMixin):
    nom        = models.CharField(max_length=100, unique=True, verbose_name="Nom du district")
    code       = models.CharField(max_length=20, blank=True, verbose_name="Code")
    is_active  = models.BooleanField(default=True)
    cree_le    = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Region(TauxFiscauxMixin):
    district   = models.ForeignKey(District, on_delete=models.PROTECT, related_name="regions")
    nom        = models.CharField(max_length=100, verbose_name="Nom de la région")
    code       = models.CharField(max_length=20, blank=True)
    is_active  = models.BooleanField(default=True)
    cree_le    = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Région"
        verbose_name_plural = "Régions"
        ordering = ["district__nom", "nom"]
        constraints = [
            models.UniqueConstraint(fields=["district", "nom"], name="unique_region_par_district"),
        ]

    def __str__(self):
        return f"{self.nom} ({self.district.nom})"


class Commune(TauxFiscauxMixin):
    region     = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="communes")
    nom        = models.CharField(max_length=100, verbose_name="Nom de la commune")
    code       = models.CharField(max_length=20, blank=True)
    is_active  = models.BooleanField(default=True)
    cree_le    = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"
        ordering = ["region__nom", "nom"]
        constraints = [
            models.UniqueConstraint(fields=["region", "nom"], name="unique_commune_par_region"),
        ]

    def __str__(self):
        return f"{self.nom} ({self.region.nom})"


class Quartier(models.Model):
    commune    = models.ForeignKey(Commune, on_delete=models.PROTECT, related_name="quartiers")
    nom        = models.CharField(max_length=100, verbose_name="Nom du quartier")
    code       = models.CharField(max_length=20, blank=True)
    is_active  = models.BooleanField(default=True)
    cree_le    = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quartier"
        verbose_name_plural = "Quartiers"
        ordering = ["commune__nom", "nom"]
        constraints = [
            models.UniqueConstraint(fields=["commune", "nom"], name="unique_quartier_par_commune"),
        ]

    def __str__(self):
        return f"{self.nom} ({self.commune.nom})"


class Zone(models.Model):
    """Niveau le plus fin : subdivision d'un quartier."""
    quartier   = models.ForeignKey(Quartier, on_delete=models.PROTECT, related_name="zones")
    nom        = models.CharField(max_length=100, verbose_name="Nom de la zone")
    code       = models.CharField(max_length=20, blank=True)
    is_active  = models.BooleanField(default=True)
    cree_le    = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ["quartier__nom", "nom"]
        constraints = [
            models.UniqueConstraint(fields=["quartier", "nom"], name="unique_zone_par_quartier"),
        ]

    def __str__(self):
        return f"{self.nom} ({self.quartier.nom})"


# ===========================================================================
# Utilisateurs
# ===========================================================================

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "SUPERADMIN")
        if not extra_fields["is_staff"]:
            raise ValueError("Le superuser doit avoir is_staff=True")
        if not extra_fields["is_superuser"]:
            raise ValueError("Le superuser doit avoir is_superuser=True")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        SUPERADMIN  = "SUPERADMIN",  "SuperAdmin"
        DG          = "DG",          "Direction Générale"
        FINANCE     = "FINANCE",     "Finance"
        JURIDIQUE   = "JURIDIQUE",   "Juridique"
        MARKETING   = "MARKETING",   "Marketing"
        SUPERVISEUR = "SUPERVISEUR", "Superviseur"
        AGENT       = "AGENT",       "Agent recenseur"
        PRESTATAIRE = "PRESTATAIRE", "Prestataire"

    email       = models.EmailField(unique=True)
    nom         = models.CharField(max_length=100)
    prenom      = models.CharField(max_length=100)
    telephone   = models.CharField(max_length=20, blank=True)
    entreprise  = models.ForeignKey(
        Entreprise, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="utilisateurs",
    )
    role        = models.CharField(max_length=30, choices=Role.choices, default=Role.AGENT)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()
    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["nom", "prenom"]

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["nom", "prenom"]

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


# ===========================================================================
# Affectation agent — FK directes vers les niveaux géographiques
# ===========================================================================

class AffectationAgent(models.Model):
    """
    Zone d'intervention d'un agent recenseur.
    Une seule des cinq FK doit être renseignée (la plus précise).
    La propriété `type_zone` / `valeur_zone` permet une lecture unifiée.
    """
    agent    = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name="affectations",
        limit_choices_to={"role": CustomUser.Role.AGENT},
    )

    district = models.ForeignKey(District, null=True, blank=True, on_delete=models.SET_NULL, related_name="affectations")
    region   = models.ForeignKey(Region,   null=True, blank=True, on_delete=models.SET_NULL, related_name="affectations")
    commune  = models.ForeignKey(Commune,  null=True, blank=True, on_delete=models.SET_NULL, related_name="affectations")
    quartier = models.ForeignKey(Quartier, null=True, blank=True, on_delete=models.SET_NULL, related_name="affectations")
    zone     = models.ForeignKey(Zone,     null=True, blank=True, on_delete=models.SET_NULL, related_name="affectations")

    est_active = models.BooleanField(default=True)
    cree_le    = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Affectation agent"
        verbose_name_plural = "Affectations agents"
        ordering = ["agent__nom"]

    def clean(self):
        fks = [self.district_id, self.region_id, self.commune_id, self.quartier_id, self.zone_id]
        renseignees = [f for f in fks if f is not None]
        if len(renseignees) == 0:
            raise ValidationError("Au moins une zone géographique doit être renseignée.")
        if len(renseignees) > 1:
            raise ValidationError("Une seule zone géographique par affectation.")

    @property
    def type_zone(self):
        if self.zone_id:      return "ZONE"
        if self.quartier_id:  return "QUARTIER"
        if self.commune_id:   return "COMMUNE"
        if self.region_id:    return "REGION"
        if self.district_id:  return "DISTRICT"
        return None

    @property
    def valeur_zone(self):
        if self.zone_id:      return self.zone.nom
        if self.quartier_id:  return self.quartier.nom
        if self.commune_id:   return self.commune.nom
        if self.region_id:    return self.region.nom
        if self.district_id:  return self.district.nom
        return None

    def __str__(self):
        return f"{self.agent.nom_complet} → {self.type_zone} : {self.valeur_zone}"