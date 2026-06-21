from rest_framework import permissions

# SAFE_METHODS = GET, HEAD, OPTIONS (lecture seule)
# Les autres (POST, PUT, PATCH, DELETE) sont des écritures.


class RoleBasedPermission(permissions.BasePermission):
    """Permission générique paramétrable par ressource.

    Usage dans une vue :
        permission_classes = [RoleBasedPermission]
        roles_lecture = {"DG", "FINANCE", "JURIDIQUE", "MARKETING", "SUPERVISEUR", "PRESTATAIRE"}
        roles_ecriture = {"SUPERADMIN", "FINANCE", "SUPERVISEUR"}

    SUPERADMIN a toujours tous les droits, quelle que soit la ressource.
    """

    roles_lecture: set[str] = set()
    roles_ecriture: set[str] = set()

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.role == "SUPERADMIN":
            return True

        roles_lecture = getattr(view, "roles_lecture", self.roles_lecture)
        roles_ecriture = getattr(view, "roles_ecriture", self.roles_ecriture)

        if request.method in permissions.SAFE_METHODS:
            return user.role in roles_lecture or user.role in roles_ecriture
        return user.role in roles_ecriture


class SupportsPermission(RoleBasedPermission):
    """Supports publicitaires (DonneeCollectee).
    Lecture : DG, Finance, Juridique, Marketing, Superviseur, Prestataire, Agent.
    Écriture : SuperAdmin, Superviseur, Agent (l'agent ne peut éditer que ses propres
    supports — vérifié séparément via has_object_permission)."""

    roles_lecture = {"DG", "FINANCE", "JURIDIQUE", "MARKETING", "SUPERVISEUR", "PRESTATAIRE", "AGENT"}
    roles_ecriture = {"SUPERVISEUR", "AGENT"}

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role in ("SUPERADMIN", "SUPERVISEUR"):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        # Un agent ne peut modifier/supprimer que les supports qu'il a lui-même collectés.
        if user.role == "AGENT":
            return obj.agent_id == user.id
        return False


class NegociationsPermission(RoleBasedPermission):
    """Négociations fiscales.
    Lecture : DG, Finance, Juridique, Marketing, Superviseur.
    Écriture : SuperAdmin, Finance, Superviseur."""

    roles_lecture = {"DG", "FINANCE", "JURIDIQUE", "MARKETING", "SUPERVISEUR"}
    roles_ecriture = {"FINANCE", "SUPERVISEUR"}


class DossiersFiscauxPermission(RoleBasedPermission):
    """Dossiers fiscaux.
    Lecture : DG, Finance, Juridique, Superviseur.
    Écriture : SuperAdmin, Finance."""

    roles_lecture = {"DG", "FINANCE", "JURIDIQUE", "SUPERVISEUR"}
    roles_ecriture = {"FINANCE"}


class DashboardsPermission(RoleBasedPermission):
    """Dashboards agrégés (Exécutif, Négociations) — lecture seule pour tous
    les rôles métier, jamais d'écriture (ce sont des endpoints GET uniquement)."""

    roles_lecture = {"DG", "FINANCE", "JURIDIQUE", "MARKETING", "SUPERVISEUR", "PRESTATAIRE", "AGENT"}
    roles_ecriture = set()