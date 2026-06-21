from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Entreprise, AffectationAgent


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ["nom", "sigle", "secteur", "is_active"]
    search_fields = ["nom", "sigle"]


class AffectationInline(admin.TabularInline):
    model = AffectationAgent
    extra = 1


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["email", "nom", "prenom", "role", "entreprise", "is_active"]
    list_filter = ["role", "is_active", "entreprise"]
    search_fields = ["email", "nom", "prenom"]
    ordering = ["nom"]
    inlines = [AffectationInline]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informations personnelles", {"fields": ("nom", "prenom", "telephone", "entreprise", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "nom", "prenom", "role", "password1", "password2"),
        }),
    )
    readonly_fields = ["date_joined"]


@admin.register(AffectationAgent)
class AffectationAgentAdmin(admin.ModelAdmin):
    list_display = ["agent", "type_zone", "valeur_zone", "est_active"]
    list_filter = ["type_zone", "est_active"]
    search_fields = ["agent__nom", "agent__prenom", "valeur_zone"]