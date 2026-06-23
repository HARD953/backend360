from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupportPublicitaireViewSet,
    NegociationViewSet,
    ArgumentairePretViewSet,
    DossierFiscalViewSet,
    AlertePrioritaireViewSet,
    DashboardExecutifView,
    DashboardNegociationsView,
    AgentsRecenseursView,
    FiltresDisponiblesView,
)
from .views import SimulationFiscaleViewSet, AnalyseGapsView

router = DefaultRouter()
router.register("supports", SupportPublicitaireViewSet, basename="support")
router.register("negociations", NegociationViewSet, basename="negociation")
router.register("argumentaires", ArgumentairePretViewSet, basename="argumentaire")
router.register("dossiers-fiscaux", DossierFiscalViewSet, basename="dossier-fiscal")
router.register("alertes", AlertePrioritaireViewSet, basename="alerte")
router.register("simulations", SimulationFiscaleViewSet, basename="simulation")

urlpatterns = [
    path("dashboards/executif/", DashboardExecutifView.as_view(), name="dashboard-executif"),
    path("dashboards/negociations/", DashboardNegociationsView.as_view(), name="dashboard-negociations"),
    path("agents-recenseurs/", AgentsRecenseursView.as_view(), name="agents-recenseurs"),
    path("supports/filtres-disponibles/", FiltresDisponiblesView.as_view(), name="filtres-disponibles"),
    path("analyse-gaps/", AnalyseGapsView.as_view(), name="analyse-gaps"),
    path("", include(router.urls)),
]