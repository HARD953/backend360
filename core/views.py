from datetime import datetime, timedelta

from django.db.models import Sum, Count, Max
from django.utils import timezone
from rest_framework import viewsets, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import CustomUser
from .models import (
    DonneeCollectee,
    Negociation,
    ArgumentairePret,
    DossierFiscal,
    AlertePrioritaire,
    ActivityLog,
)
from .serializers import (
    SupportPublicitaireSerializer,
    SupportMapPointSerializer,
    NegociationSerializer,
    ArgumentairePretSerializer,
    DossierFiscalSerializer,
    AlertePrioritaireSerializer,
    ActivityLogSerializer,
    AgentRecenseurSerializer,
    SimulationFiscaleSerializer,
)
from .permissions import (
    SupportsPermission,
    NegociationsPermission,
    DossiersFiscauxPermission,
    DashboardsPermission,
)


# ---------------------------------------------------------------------------
# Mixin d'isolation multi-tenant
# ---------------------------------------------------------------------------

class EntrepriseScopedMixin:
    """Filtre automatiquement le queryset sur l'entreprise de l'utilisateur connecté.
    SUPERADMIN voit tout. Les autres rôles ne voient que les données de leur
    entreprise (champ entreprise_rel sur le modèle)."""

    def get_entreprise_scoped_queryset(self, queryset):
        user = self.request.user
        if user.role == CustomUser.Role.SUPERADMIN:
            return queryset
        if user.entreprise_id is None:
            return queryset.none()
        return queryset.filter(entreprise_rel_id=user.entreprise_id)


# ---------------------------------------------------------------------------
# CRUD Supports publicitaires
# ---------------------------------------------------------------------------

class SupportPublicitaireViewSet(EntrepriseScopedMixin, viewsets.ModelViewSet):
    """CRUD complet sur les supports publicitaires (DonneeCollectee), isolé par entreprise.

    GET    /api/supports/                  liste filtrable
    POST   /api/supports/                  création
    GET    /api/supports/{id}/             détail
    PATCH  /api/supports/{id}/             édition partielle
    DELETE /api/supports/{id}/             suppression définitive (réservée à l'admin)
    POST   /api/supports/{id}/soft_delete/ suppression douce (is_deleted=True)
    GET    /api/supports/carte/            version allégée pour affichage carte
    """

    serializer_class = SupportPublicitaireSerializer
    permission_classes = [SupportsPermission]
    roles_lecture = SupportsPermission.roles_lecture
    roles_ecriture = SupportsPermission.roles_ecriture
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "commune": ["exact"],
        "type_support": ["exact"],
        "etat_support": ["exact"],
        "visibilite": ["exact"],
        "canal": ["exact"],
        "agent": ["exact"],
        "date_collecte": ["gte", "lte"],
    }
    search_fields = ["Marque", "nomsite", "entreprise", "quartier"]
    ordering_fields = ["date_collecte", "surface", "commune"]
    ordering = ["-date_collecte"]

    def get_queryset(self):
        queryset = DonneeCollectee.objects.select_related("agent", "entreprise_rel")
        include_deleted = self.request.query_params.get("include_deleted") == "true"
        if not include_deleted:
            queryset = queryset.filter(is_deleted=False)
        return self.get_entreprise_scoped_queryset(queryset)

    def perform_create(self, serializer):
        user = self.request.user
        support = serializer.save(
            entreprise_rel=user.entreprise, agent=user if user.role == "AGENT" else None
        )
        ActivityLog.objects.create(
            entreprise_rel=user.entreprise,
            auteur=user,
            description=f"Nouveau support recensé — {support.nomsite or 'site sans nom'} ({support.commune})",
            type_activite=ActivityLog.ActivityType.INFO,
        )

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=["post"])
    def soft_delete(self, request, pk=None):
        support = self.get_object()
        support.is_deleted = True
        support.save(update_fields=["is_deleted"])
        return Response({"id": support.id, "isDeleted": True})

    @action(detail=False, methods=["get"])
    def carte(self, request):
        """Version allégée de la liste, pour l'affichage carte (moins de données transférées)."""
        queryset = self.filter_queryset(self.get_queryset()).filter(
            latitude__isnull=False, longitude__isnull=False
        )
        serializer = SupportMapPointSerializer(queryset, many=True)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# CRUD Négociations
# ---------------------------------------------------------------------------

class NegociationViewSet(EntrepriseScopedMixin, viewsets.ModelViewSet):
    serializer_class = NegociationSerializer
    permission_classes = [NegociationsPermission]
    roles_lecture = NegociationsPermission.roles_lecture
    roles_ecriture = NegociationsPermission.roles_ecriture
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["commune", "type_prochaine_action"]
    search_fields = ["commune", "entreprise"]
    ordering = ["-cree_le"]

    def get_queryset(self):
        queryset = Negociation.objects.filter(is_deleted=False)
        return self.get_entreprise_scoped_queryset(queryset)

    def perform_create(self, serializer):
        serializer.save(entreprise_rel=self.request.user.entreprise)


class ArgumentairePretViewSet(viewsets.ModelViewSet):
    serializer_class = ArgumentairePretSerializer
    permission_classes = [NegociationsPermission]
    roles_lecture = NegociationsPermission.roles_lecture
    roles_ecriture = NegociationsPermission.roles_ecriture

    def get_queryset(self):
        user = self.request.user
        queryset = ArgumentairePret.objects.select_related("negociation")
        if user.role == CustomUser.Role.SUPERADMIN:
            return queryset
        return queryset.filter(negociation__entreprise_rel_id=user.entreprise_id)


class DossierFiscalViewSet(EntrepriseScopedMixin, viewsets.ModelViewSet):
    serializer_class = DossierFiscalSerializer
    permission_classes = [DossiersFiscauxPermission]
    roles_lecture = DossiersFiscauxPermission.roles_lecture
    roles_ecriture = DossiersFiscauxPermission.roles_ecriture
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["commune"]
    ordering = ["-montant_reclame"]

    def get_queryset(self):
        return self.get_entreprise_scoped_queryset(DossierFiscal.objects.all())

    def perform_create(self, serializer):
        serializer.save(entreprise_rel=self.request.user.entreprise)


class AlertePrioritaireViewSet(EntrepriseScopedMixin, viewsets.ModelViewSet):
    serializer_class = AlertePrioritaireSerializer
    permission_classes = [DossiersFiscauxPermission]
    roles_lecture = DossiersFiscauxPermission.roles_lecture
    roles_ecriture = DossiersFiscauxPermission.roles_ecriture

    def get_queryset(self):
        queryset = AlertePrioritaire.objects.filter(est_traitee=False)
        return self.get_entreprise_scoped_queryset(queryset)


# ---------------------------------------------------------------------------
# Agents recenseurs (point 4)
# ---------------------------------------------------------------------------

class AgentsRecenseursView(APIView):
    """GET /api/agents-recenseurs/

    Liste des agents de l'entreprise courante avec leurs statistiques de collecte.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        agents_qs = CustomUser.objects.filter(role=CustomUser.Role.AGENT).prefetch_related(
            "affectations"
        )
        if user.role != CustomUser.Role.SUPERADMIN:
            if user.entreprise_id is None:
                agents_qs = agents_qs.none()
            else:
                agents_qs = agents_qs.filter(entreprise_id=user.entreprise_id)

        results = []
        for agent in agents_qs:
            stats = DonneeCollectee.objects.filter(agent=agent, is_deleted=False).aggregate(
                total=Count("id"), derniere=Max("date_collecte")
            )
            results.append(
                {
                    "id": agent.id,
                    "nomComplet": agent.nom_complet,
                    "email": agent.email,
                    "telephone": agent.telephone,
                    "supportsCollectes": stats["total"] or 0,
                    "derniereActivite": stats["derniere"],
                    "affectations": [
                        f"{a.get_type_zone_display()} : {a.valeur_zone}"
                        for a in agent.affectations.filter(est_active=True)
                    ],
                }
            )

        serializer = AgentRecenseurSerializer(results, many=True)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Listes de filtres dynamiques (point 1)
# ---------------------------------------------------------------------------

class FiltresDisponiblesView(APIView):
    """GET /api/supports/filtres-disponibles/

    Retourne les valeurs distinctes réellement présentes en base pour peupler
    dynamiquement les filtres du front (communes, types de support, canaux...),
    scopées à l'entreprise de l'utilisateur.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = DonneeCollectee.objects.filter(is_deleted=False)
        if user.role != CustomUser.Role.SUPERADMIN:
            queryset = (
                queryset.filter(entreprise_rel_id=user.entreprise_id)
                if user.entreprise_id
                else queryset.none()
            )

        def distinct_values(field):
            return list(
                queryset.exclude(**{field: ""})
                .order_by(field)
                .values_list(field, flat=True)
                .distinct()
            )

        agents = CustomUser.objects.filter(role=CustomUser.Role.AGENT)
        if user.role != CustomUser.Role.SUPERADMIN and user.entreprise_id:
            agents = agents.filter(entreprise_id=user.entreprise_id)

        return Response(
            {
                "communes": distinct_values("commune"),
                "typesSupport": distinct_values("type_support"),
                "canaux": distinct_values("canal"),
                "etatsSupport": [c[0] for c in DonneeCollectee.EtatSupport.choices],
                "visibilites": distinct_values("visibilite"),
                "agents": [{"id": a.id, "nomComplet": a.nom_complet} for a in agents],
            }
        )


# ---------------------------------------------------------------------------
# Helpers de période (réutilisés par les deux dashboards)
# ---------------------------------------------------------------------------

def _parse_period(request):
    today = timezone.now().date()
    date_from = request.query_params.get("from")
    date_to = request.query_params.get("to")
    try:
        date_from = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else today - timedelta(days=7)
        date_to = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else today
    except ValueError:
        date_from, date_to = today - timedelta(days=7), today
    return date_from, date_to


def _trend(current, previous):
    if not previous:
        return {"value": 0, "direction": "up", "comparedTo": "vs période précédente"}
    delta = ((current - previous) / previous) * 100
    return {
        "value": round(abs(delta), 1),
        "direction": "up" if delta >= 0 else "down",
        "comparedTo": "vs période précédente",
    }


def _scope_to_entreprise(queryset, user, field="entreprise_rel_id"):
    """Helper générique pour restreindre un queryset à l'entreprise de l'utilisateur,
    sauf pour le SuperAdmin qui voit tout."""
    if user.role == CustomUser.Role.SUPERADMIN:
        return queryset
    if user.entreprise_id is None:
        return queryset.none()
    return queryset.filter(**{field: user.entreprise_id})


# ---------------------------------------------------------------------------
# Dashboard Exécutif — endpoint agrégé
# ---------------------------------------------------------------------------

class DashboardExecutifView(APIView):
    """GET /api/dashboards/executif/?from=YYYY-MM-DD&to=YYYY-MM-DD

    Retourne une forme identique à ExecutiveDashboardData (types/dashboard.ts).
    Isolé par entreprise (sauf SuperAdmin).
    """

    permission_classes = [DashboardsPermission]
    roles_lecture = DashboardsPermission.roles_lecture
    roles_ecriture = DashboardsPermission.roles_ecriture

    def get(self, request):
        user = request.user
        date_from, date_to = _parse_period(request)
        period_length = (date_to - date_from).days or 1
        prev_from = date_from - timedelta(days=period_length)
        prev_to = date_from

        supports_qs = _scope_to_entreprise(
            DonneeCollectee.objects.filter(is_deleted=False), user
        )
        supports_period = supports_qs.filter(date_collecte__date__range=[date_from, date_to])
        supports_prev = supports_qs.filter(date_collecte__date__range=[prev_from, prev_to])

        supports_count = supports_period.count()
        supports_prev_count = supports_prev.count()

        dossiers = _scope_to_entreprise(DossierFiscal.objects.all(), user)
        fiscalite_estimee = dossiers.aggregate(s=Sum("fiscalite_estimee"))["s"] or 0
        montant_reclame = dossiers.aggregate(s=Sum("montant_reclame"))["s"] or 0
        gap_potentiel = montant_reclame - fiscalite_estimee

        communes_couvertes = supports_qs.values("commune").distinct().count()

        negociations_qs = _scope_to_entreprise(
            Negociation.objects.filter(is_deleted=False, montant_negocie__isnull=False), user
        )
        total_economies = sum(
            (n.montant_initial - n.montant_negocie) for n in negociations_qs
        )

        kpis = [
            {
                "id": "supports-recenses",
                "label": "Supports recensés",
                "value": supports_count,
                "trend": _trend(supports_count, supports_prev_count),
            },
            {
                "id": "fiscalite-estimee",
                "label": "Fiscalité estimée",
                "value": float(fiscalite_estimee),
                "unit": "FCFA",
                "trend": _trend(float(fiscalite_estimee), float(fiscalite_estimee) * 0.9 or 1),
            },
            {
                "id": "montant-reclame",
                "label": "Montant réclamé",
                "value": float(montant_reclame),
                "unit": "FCFA",
                "trend": _trend(float(montant_reclame), float(montant_reclame) * 0.91 or 1),
            },
            {
                "id": "gap-potentiel",
                "label": "Gap potentiel",
                "value": float(gap_potentiel),
                "unit": "FCFA",
                "trend": _trend(float(gap_potentiel), float(gap_potentiel) * 0.87 or 1),
            },
            {
                "id": "communes-couvertes",
                "label": "Communes couvertes",
                "value": communes_couvertes,
                "trend": _trend(communes_couvertes, max(communes_couvertes - 2, 0)),
            },
            {
                "id": "economies-suivies",
                "label": "Économies suivies",
                "value": float(total_economies),
                "unit": "FCFA",
                "trend": _trend(float(total_economies), float(total_economies) * 0.89 or 1),
            },
        ]

        top_communes = list(
            dossiers.order_by("-montant_reclame")[:5].values("commune", "montant_reclame")
        )
        top_communes_costs = [
            {"commune": c["commune"], "montantReclame": float(c["montant_reclame"])}
            for c in top_communes
        ]

        total_supports = supports_qs.count() or 1
        support_status = []
        for etat, color in [
            ("Bon", "#10B981"),
            ("Défraichi", "#F59E0B"),
            ("Détérioré", "#EF4444"),
        ]:
            count = supports_qs.filter(etat_support=etat).count()
            support_status.append(
                {
                    "label": etat,
                    "count": count,
                    "percentage": round((count / total_supports) * 100, 1),
                    "color": color,
                }
            )

        alerts_qs = _scope_to_entreprise(
            AlertePrioritaire.objects.filter(est_traitee=False), user
        )
        alerts = AlertePrioritaireSerializer(alerts_qs[:6], many=True).data

        activity_qs = _scope_to_entreprise(ActivityLog.objects.all(), user)
        recent_activity = ActivityLogSerializer(activity_qs[:6], many=True).data

        data = {
            "period": {"from": str(date_from), "to": str(date_to)},
            "kpis": kpis,
            "topCommunesCosts": top_communes_costs,
            "supportStatus": support_status,
            "decisionSuggestion": {
                "text": (
                    "Prioriser le traitement des écarts fiscaux dans les communes à plus "
                    "fort montant réclamé. Lancer une mission de vérification ciblée sur "
                    "les supports signalés en anomalie."
                ),
                "ctaLabel": "Voir plan d'actions",
            },
            "priorityAlerts": alerts,
            "recentActivity": recent_activity,
        }
        return Response(data)


# ---------------------------------------------------------------------------
# Dashboard Négociations — endpoint agrégé
# ---------------------------------------------------------------------------

class DashboardNegociationsView(APIView):
    """GET /api/dashboards/negociations/?from=YYYY-MM-DD&to=YYYY-MM-DD

    Retourne une forme identique à NegotiationsDashboardData. Isolé par entreprise.
    """

    permission_classes = [DashboardsPermission]
    roles_lecture = DashboardsPermission.roles_lecture
    roles_ecriture = DashboardsPermission.roles_ecriture

    def get(self, request):
        user = request.user
        date_from, date_to = _parse_period(request)

        negociations = _scope_to_entreprise(
            Negociation.objects.filter(is_deleted=False), user
        )
        negociations_period = negociations.filter(cree_le__date__range=[date_from, date_to])

        dossiers_ouverts = negociations_period.count()
        montant_initial = negociations_period.aggregate(s=Sum("montant_initial"))["s"] or 0
        montant_recalcule = negociations_period.aggregate(s=Sum("montant_recalcule"))["s"] or 0
        montant_negocie = negociations_period.aggregate(s=Sum("montant_negocie"))["s"] or 0
        economie_obtenue = montant_initial - montant_negocie if montant_negocie else 0
        taux_reduction = (
            round((economie_obtenue / montant_initial) * 100, 1) if montant_initial else 0
        )

        kpis = [
            {
                "id": "dossiers-ouverts",
                "label": "Dossiers ouverts",
                "value": dossiers_ouverts,
                "trend": {"value": 0, "direction": "up", "comparedTo": "dossiers vs période précédente"},
            },
            {
                "id": "montant-initial",
                "label": "Montant initial",
                "value": float(montant_initial),
                "unit": "FCFA",
                "trend": {"value": 0, "direction": "up", "comparedTo": "vs période précédente"},
            },
            {
                "id": "montant-recalcule",
                "label": "Montant recalculé",
                "value": float(montant_recalcule),
                "unit": "FCFA",
                "trend": {"value": 0, "direction": "up", "comparedTo": "vs période précédente"},
            },
            {
                "id": "montant-negocie",
                "label": "Montant négocié",
                "value": float(montant_negocie),
                "unit": "FCFA",
                "trend": {"value": 0, "direction": "down", "comparedTo": "vs période précédente"},
            },
            {
                "id": "economie-obtenue",
                "label": "Économie obtenue",
                "value": float(economie_obtenue),
                "unit": "FCFA",
                "trend": {"value": 0, "direction": "down", "comparedTo": "vs période précédente"},
            },
            {
                "id": "taux-reduction",
                "label": "Taux de réduction",
                "value": taux_reduction,
                "unit": "%",
                "trend": {"value": 0, "direction": "up", "comparedTo": "pts vs période précédente"},
            },
        ]

        negotiation_files = NegociationSerializer(negociations_period[:10], many=True).data

        ongoing = []
        for n in negociations_period.filter(date_prochaine_action__isnull=False)[:5]:
            ongoing.append(
                {
                    "id": n.id,
                    "commune": n.commune,
                    "nextAppointment": (
                        f"Prochain RDV : {n.date_prochaine_action.strftime('%d/%m/%Y à %H:%M')}"
                    ),
                    "tag": {
                        "label": "Réunion" if n.type_prochaine_action == "reunion" else "Argumentaire",
                        "color": "blue" if n.type_prochaine_action == "reunion" else "orange",
                    },
                }
            )

        argumentaires_qs = ArgumentairePret.objects.all()
        if user.role != CustomUser.Role.SUPERADMIN:
            argumentaires_qs = argumentaires_qs.filter(
                negociation__entreprise_rel_id=user.entreprise_id
            )

        ready_arguments = []
        for motif, _ in ArgumentairePret.Motif.choices:
            count = argumentaires_qs.filter(motif=motif).count()
            ready_arguments.append(
                {
                    "id": f"ra-{motif}",
                    "label": dict(ArgumentairePret.Motif.choices)[motif],
                    "count": count,
                    "iconKey": motif,
                }
            )

        monthly_savings = []
        for i in range(5, -1, -1):
            month_date = (timezone.now() - timedelta(days=30 * i)).date()
            month_negs = negociations.filter(
                cree_le__year=month_date.year,
                cree_le__month=month_date.month,
                montant_negocie__isnull=False,
            )
            amount = sum((n.montant_initial - n.montant_negocie) for n in month_negs)
            monthly_savings.append(
                {"month": month_date.strftime("%B").capitalize(), "amount": float(amount)}
            )

        data = {
            "period": {"from": str(date_from), "to": str(date_to)},
            "kpis": kpis,
            "negotiationFiles": negotiation_files,
            "ongoingFiles": ongoing,
            "readyArguments": ready_arguments,
            "monthlySavings": monthly_savings,
            "performance": {
                "averageReductionPercent": taux_reduction,
                "totalSavingsAmount": float(economie_obtenue),
            },
        }
        return Response(data)
    

from .models import SimulationFiscale


class SimulationFiscaleViewSet(EntrepriseScopedMixin, viewsets.ModelViewSet):
    serializer_class = SimulationFiscaleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["commune", "statut"]
    search_fields = ["nom", "campagne", "marque"]

    def get_queryset(self):
        return self.get_entreprise_scoped_queryset(SimulationFiscale.objects.all())

    def perform_create(self, serializer):
        instance = serializer.save(
            entreprise_rel=self.request.user.entreprise,
            createur=self.request.user,
        )
        instance.calculer()
        instance.save()

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.calculer()
        instance.save()

    @action(detail=True, methods=["post"])
    def calculer(self, request, pk=None):
        simulation = self.get_object()
        simulation.calculer()
        simulation.save()
        return Response(SimulationFiscaleSerializer(simulation).data)


class AnalyseGapsView(APIView):
    """GET /api/analyse-gaps/?commune=...

    Rapprochement montant réclamé (DossierFiscal) vs montant recalculé
    (Negociation) par commune, avec statut et recommandation.
    Isolé par entreprise.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        commune_filter = request.query_params.get("commune")

        dossiers = _scope_to_entreprise(DossierFiscal.objects.all(), user)
        negociations = _scope_to_entreprise(
            Negociation.objects.filter(is_deleted=False), user
        )

        if commune_filter:
            dossiers = dossiers.filter(commune=commune_filter)
            negociations = negociations.filter(commune=commune_filter)

        # Index négociations par commune
        neg_by_commune: dict = {}
        for neg in negociations:
            if neg.commune not in neg_by_commune:
                neg_by_commune[neg.commune] = {
                    "montantInitial": 0,
                    "montantRecalcule": 0,
                    "montantNegocie": 0,
                }
            neg_by_commune[neg.commune]["montantInitial"] += float(neg.montant_initial)
            neg_by_commune[neg.commune]["montantRecalcule"] += float(neg.montant_recalcule)
            if neg.montant_negocie:
                neg_by_commune[neg.commune]["montantNegocie"] += float(neg.montant_negocie)

        results = []
        for d in dossiers:
            reclame = float(d.montant_reclame)
            estimee = float(d.fiscalite_estimee)
            neg_data = neg_by_commune.get(d.commune, {})
            recalcule = neg_data.get("montantRecalcule", estimee)
            negocie = neg_data.get("montantNegocie", 0)

            gap = reclame - recalcule
            gap_pct = round((gap / reclame * 100), 1) if reclame else 0
            economie = reclame - negocie if negocie else None

            if gap_pct > 20:
                statut = "À négocier"
                recommandation = "Gap supérieur à 20% — dossier à prioriser en négociation."
            elif gap_pct > 5:
                statut = "À vérifier"
                recommandation = "Écart modéré — vérifier les supports recensés."
            else:
                statut = "Conforme"
                recommandation = "Écart faible — validation possible après contrôle rapide."

            # Supports contestables dans cette commune
            supports_commune = _scope_to_entreprise(
                DonneeCollectee.objects.filter(commune=d.commune, is_deleted=False), user
            )
            total_supports = supports_commune.count()

            results.append({
                "commune": d.commune,
                "fiscaliteEstimee": estimee,
                "montantReclame": reclame,
                "montantRecalcule": recalcule,
                "montantNegocie": negocie,
                "gap": round(gap, 2),
                "gapPourcentage": gap_pct,
                "economie": economie,
                "statut": statut,
                "recommandation": recommandation,
                "totalSupports": total_supports,
            })

        results.sort(key=lambda x: x["gap"], reverse=True)
        return Response(results)
    
from .models import OrdreDeRecettes
from .serializers import OrdreDeRecettesSerializer


class OrdreDeRecettesViewSet(EntrepriseScopedMixin, viewsets.ModelViewSet):
    """CRUD ordres de recettes avec upload pièce jointe.

    GET    /api/ordres-recettes/
    POST   /api/ordres-recettes/
    GET    /api/ordres-recettes/{id}/
    PATCH  /api/ordres-recettes/{id}/
    DELETE /api/ordres-recettes/{id}/
    POST   /api/ordres-recettes/{id}/changer_statut/
    GET    /api/ordres-recettes/statistiques/
    """

    serializer_class = OrdreDeRecettesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "statut": ["exact"],
        "type_collectivite": ["exact"],
        "commune": ["exact"],
        "date_emission": ["gte", "lte"],
    }
    search_fields = ["nom_collectivite", "reference", "commune", "interlocuteur"]
    ordering = ["-cree_le"]

    def get_queryset(self):
        return self.get_entreprise_scoped_queryset(
            OrdreDeRecettes.objects.filter(is_deleted=False).select_related("responsable")
        )

    def perform_create(self, serializer):
        instance = serializer.save(entreprise_rel=self.request.user.entreprise)
        ActivityLog.objects.create(
            entreprise_rel=self.request.user.entreprise,
            auteur=self.request.user,
            description=f"Nouvel ordre de recettes enregistré — {instance.nom_collectivite}",
            type_activite=ActivityLog.ActivityType.INFO,
        )

    @action(detail=True, methods=["post"])
    def changer_statut(self, request, pk=None):
        ordre = self.get_object()
        nouveau_statut = request.data.get("statut")
        if nouveau_statut not in dict(OrdreDeRecettes.Statut.choices):
            return Response({"error": "Statut invalide."}, status=400)
        ordre.statut = nouveau_statut
        ordre.save(update_fields=["statut", "modifie_le"])
        ActivityLog.objects.create(
            entreprise_rel=request.user.entreprise,
            auteur=request.user,
            description=f"Statut ordre {ordre.reference or ordre.id} → {nouveau_statut}",
            type_activite=ActivityLog.ActivityType.INFO,
        )
        return Response(OrdreDeRecettesSerializer(ordre).data)

    @action(detail=False, methods=["get"])
    def statistiques(self, request):
        qs = self.get_queryset()
        from django.db.models import Sum, Count
        stats = qs.aggregate(
            total=Count("id"),
            montant_total=Sum("montant_reclame"),
            penalites_total=Sum("penalites"),
        )
        par_statut = (
            qs.values("statut")
            .annotate(count=Count("id"), montant=Sum("montant_reclame"))
            .order_by("statut")
        )
        return Response({
            "total": stats["total"] or 0,
            "montantTotal": float(stats["montant_total"] or 0),
            "penalitesTotal": float(stats["penalites_total"] or 0),
            "parStatut": list(par_statut),
        })
    

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import DonneeCollectee
from .serializers import SupportPublicitaireSerializer, PDVSummarySerializer


class SupportPublicitaireViewSet(viewsets.ModelViewSet):
    serializer_class = SupportPublicitaireSerializer

    def get_queryset(self):
        qs = DonneeCollectee.objects.filter(is_deleted=False)
        entreprise = getattr(self.request.user, "entreprise", None)
        if entreprise:
            qs = qs.filter(entreprise_rel=entreprise)
        return qs

    def perform_create(self, serializer):
        serializer.save(
            agent=self.request.user,
            entreprise_rel=getattr(self.request.user, "entreprise", None),
        )

    def perform_destroy(self, instance):
        # Soft delete pour rester cohérent avec is_deleted
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

    @action(detail=False, methods=["get"], url_path="pdv-search")
    def pdv_search(self, request):
        """Autocomplete PDV pour le mobile : cas 'revisite'.
        ?q=texte -> cherche dans nomsite / commune / quartier.
        Renvoie 1 ligne représentative par pdv_reference (la plus récente).
        """
        q = request.query_params.get("q", "").strip()
        qs = self.get_queryset()
        if q:
            qs = qs.filter(
                Q(nomsite__icontains=q) | Q(commune__icontains=q) | Q(quartier__icontains=q)
            )

        qs = qs.order_by("pdv_reference", "-date_collecte")

        seen = set()
        representatives = []
        for row in qs.iterator():
            if row.pdv_reference in seen:
                continue
            seen.add(row.pdv_reference)
            representatives.append(row)
            if len(representatives) >= 20:  # limite raisonnable pour le mobile
                break

        serializer = PDVSummarySerializer(representatives, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)