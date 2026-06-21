from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Entreprise(models.Model):
    """Entreprise cliente (ex: MTN-CI). Pivot du multi-tenant : toute donnée
    métier (supports, négociations, dossiers fiscaux) est rattachée à une entreprise."""

    nom = models.CharField(max_length=100, unique=True)
    sigle = models.CharField(max_length=20, blank=True)
    secteur = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class CustomUserManager(BaseUserManager):
    """Manager pour CustomUser, authentification par email plutôt que username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", CustomUser.Role.SUPERADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superuser doit avoir is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Utilisateur de la plateforme. Rôles alignés sur le dossier de cadrage
    (section 2 : DG, finance, juridique, marketing, superviseur, agent terrain, prestataire)."""

    class Role(models.TextChoices):
        SUPERADMIN = "SUPERADMIN", "SuperAdmin"
        DIRECTION_GENERALE = "DG", "Direction Générale"
        FINANCE = "FINANCE", "Finance"
        JURIDIQUE = "JURIDIQUE", "Juridique"
        MARKETING = "MARKETING", "Marketing"
        SUPERVISEUR = "SUPERVISEUR", "Superviseur"
        AGENT = "AGENT", "Agent recenseur"
        PRESTATAIRE = "PRESTATAIRE", "Prestataire"

    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    entreprise = models.ForeignKey(
        Entreprise,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="utilisateurs",
    )
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.AGENT)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
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


class AffectationAgent(models.Model):
    """Zone géographique assignée à un agent pour la collecte terrain.
    Un agent peut avoir plusieurs affectations (ex: deux communes)."""

    class TypeZone(models.TextChoices):
        QUARTIER = "QUARTIER", "Quartier"
        COMMUNE = "COMMUNE", "Commune"
        REGION = "REGION", "Région"

    agent = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="affectations",
        limit_choices_to={"role": CustomUser.Role.AGENT},
    )
    type_zone = models.CharField(max_length=20, choices=TypeZone.choices)
    valeur_zone = models.CharField(
        max_length=100, help_text="Nom du quartier, de la commune ou de la région"
    )
    est_active = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Affectation agent"
        verbose_name_plural = "Affectations agents"
        ordering = ["agent", "type_zone"]
        constraints = [
            models.UniqueConstraint(
                fields=["agent", "type_zone", "valeur_zone"],
                name="unique_affectation_par_agent",
            )
        ]

    def __str__(self):
        return f"{self.agent.nom_complet} → {self.get_type_zone_display()} : {self.valeur_zone}"