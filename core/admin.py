from django.contrib import admin
from .models import (
    DonneeCollectee,
    Negociation,
    ArgumentairePret,
    DossierFiscal,
    AlertePrioritaire,
    ActivityLog,
)


@admin.register(DonneeCollectee)
class DonneeCollecteeAdmin(admin.ModelAdmin):
    list_display = ["Marque", "nomsite", "commune", "etat_support", "entreprise_rel", "agent", "date_collecte", "is_deleted"]
    list_filter = ["commune", "etat_support", "visibilite", "is_deleted", "entreprise_rel"]
    search_fields = ["Marque", "nomsite", "entreprise", "quartier"]
    readonly_fields = ["date_collecte", "create", "updated_at"]


@admin.register(Negociation)
class NegociationAdmin(admin.ModelAdmin):
    list_display = ["commune", "entreprise_rel", "montant_initial", "montant_negocie", "type_prochaine_action"]
    list_filter = ["commune", "type_prochaine_action", "is_deleted", "entreprise_rel"]
    search_fields = ["commune", "entreprise"]


@admin.register(ArgumentairePret)
class ArgumentairePretAdmin(admin.ModelAdmin):
    list_display = ["motif", "negociation", "cree_le"]
    list_filter = ["motif"]


@admin.register(DossierFiscal)
class DossierFiscalAdmin(admin.ModelAdmin):
    list_display = ["commune", "entreprise_rel", "fiscalite_estimee", "montant_reclame", "gap_potentiel"]
    list_filter = ["entreprise_rel"]
    search_fields = ["commune"]


@admin.register(AlertePrioritaire)
class AlertePrioritaireAdmin(admin.ModelAdmin):
    list_display = ["titre", "severite", "commune", "entreprise_rel", "est_traitee", "cree_le"]
    list_filter = ["severite", "est_traitee", "entreprise_rel"]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["description", "type_activite", "auteur", "entreprise_rel", "cree_le"]
    list_filter = ["type_activite", "entreprise_rel"]
    readonly_fields = ["cree_le"]