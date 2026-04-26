from django.urls import path
from .views import *

urlpatterns = [
    # Upload
    path('upload/',        ExcelUploadView.as_view(),      name='excel-upload'),
    path('uploads/',       UploadListView.as_view(),        name='upload-list'),
    path('records/',       BudgetRecordListView.as_view(),  name='record-list'),#valider
    path('projet/<int:id>/', GetProjetByIdView.as_view(), name='get-projet-by-id'),


    # Recaps
    path('region/',   RecapParRegionView.as_view(),  name='recap-region'),#valider
    path('famille/',  RecapParFamilleView.as_view(), name='recap-famille'),#valider
    path('activite/', RecapParActiviteView.as_view(),name='recap-activite'),#valider
    path('global/',   RecapGlobalView.as_view(),     name='recap-global'),#valider
    path('famille-par-activite/', RecapFamilleParActiviteView.as_view()),#valider
    path('export/pdf/<int:pk>/', BudgetRecordPDFView.as_view(), name='budget-pdf'),#valider
    path('region-famille/', RecapRegionFamilleView.as_view(), name='recap-region-famille'),#valider
    path('verification/', VerificationCalculsView.as_view(), name='verification-calculs'),
    path('budget/nouveau-projet/', NouveauProjetView.as_view(), name='create-budget-manuel'),#valider
    # path('budget/modifier-projet/<str:code_division>/', ModifierProjetView.as_view(), name='modifier-projet'),#valider
    path('budget/admin/patch-projet/<str:code_division>/',PatchProjetAdminView.as_view(),name='admin-patch-projet',),
    path('budget/responsable/modifier-projet/<str:code_division>/',ModifierProjetResponsableView.as_view(),name='responsable-modifier-projet',),
    # path('budget/restaurer/<str:code_division>/<int:version>/',RestaurerVersionView.as_view(),name='restaurer-version'),
    # path('budget/historique/<str:code_division>/', HistoriqueProjetView.as_view(), name='historique-projet'),
    
    # path('budget/projet/<str:code_division>/', BudgetRecordByCodeDivisionView.as_view()),

    #historique:
    path('budget/historique/<str:code_division>/',HistoriqueProjetView.as_view(),name='historique-projet'),#valider
    path('budget/historique/<str:code_division>/actif/',HistoriqueProjetView.as_view(),{'mode': 'actif'},name='historique-projet-actif'),#valider




    



    # procedure  validation par role:
    # path('budget/soumettre/<int:record_id>/',SoumettreProjetView.as_view()),
    path('budget/valider/directeur-region/<int:record_id>/',ValiderDirecteurRegionView.as_view()),
    path('budget/valider/agent/<int:record_id>/',ValiderAgentView.as_view()),
    path('budget/valider/chef/<int:record_id>/',ValiderChefView.as_view()),
    path('budget/valider/directeur/<int:record_id>/',ValiderDirecteurView.as_view()),
    path('budget/valider/divisionnaire/<int:record_id>/',ValiderDivisionnnaireView.as_view()),

    # Listes par rôle
    #http://localhost:8083/recap/budget/projets/responsable/?statut=brouillon
    path('budget/projets/responsable/',ListeProjetsResponsableView.as_view()),#valider

    #http://localhost:8083/recap/budget/projets/directeur-region/?statut=soumis
    # path('budget/projets/directeur-region/',ListeProjetsDirecteurRegionView.as_view()),#valider
    






    #valider

    # gets pour directeur region:
    path('budget/directeur-region/soumis/', ListeProjetsSoumisDRView.as_view(), name='dr-soumis'),
    path('budget/directeur-region/valides/', ListeProjetsValidesDRView.as_view(), name='dr-valides'),
    path('budget/directeur-region/reserve-chef/', ListeProjetsReserveChefDRView.as_view(), name='dr-reserve-chef'),
    path('budget/directeur-region/reserve-directeur/', ListeProjetsReserveDirecteurDRView.as_view(), name='dr-reserve-directeur'),
    path('budget/directeur-region/tous/', ListeProjetsTousDRView.as_view(), name='dr-tous'),
    path('budget/directeur-region/historique/', ListeProjetsHistoriqueDRView.as_view(), name='dr-historique'),
    path('budget/directeur-region/rejetes/', ListeProjetsRejetesDRView.as_view(), name='dr-rejetes'),
    path('budget/directeur-region/brouillon/', ListeProjetsBrouillonDRView.as_view(), name='dr-brouillon'),



    # gets pour agent:
    path('budget/agent/valides-dr/', ListeProjetsAgentValidesDRView.as_view(), name='agent-valides-dr'),
    path('budget/agent/reserve/', ListeProjetsAgentReserveView.as_view(), name='agent-reserve'),
    path('budget/agent/valides/', ListeProjetsAgentValidesView.as_view(), name='agent-valides'),
    path('budget/agent/tous/', ListeProjetsAgentTousView.as_view(), name='agent-tous'),
    path('budget/agent/historique/', ListeProjetsAgentHistoriqueView.as_view(), name='agent-historique'),

    # gets pour chef:
    # path('budget/chef/valides-agent/', ListeProjetsChefValidesAgentView.as_view(), name='chef-valides-agent'),
    # path('budget/chef/reserve-agent/', ListeProjetsChefReserveAgentView.as_view(), name='chef-reserve-agent'),
    path('budget/chef/AgentStatus/', ListeProjetsChefView.as_view(), name='chef-valides'),
    path('budget/chef/valides/', ListeProjetsChefValidesView.as_view(), name='chef-valides'),
    path('budget/chef/reserve-chef/', ListeProjetsChefReserveChefView.as_view(), name='chef-reserve-chef'),
    path('budget/chef/tous/', ListeProjetsChefTousView.as_view(), name='chef-tous'),
    path('budget/chef/historique/', ListeProjetsChefHistoriqueView.as_view(), name='chef-historique'),




    # gets pour directeur:
    path('budget/directeur/valides-chef/', ListeProjetsDirecteurValidesChefView.as_view(), name='directeur-valides-chef'),
    # path('budget/directeur/reserve-chef/', ListeProjetsDirecteurReserveChefView.as_view(), name='directeur-reserve-chef'),
    path('budget/directeur/ChefStatus/', ListeProjetsDirecteurView.as_view(), name='directeur-projets'),
    path('budget/directeur/valides/', ListeProjetsDirecteurValidesView.as_view(), name='directeur-valides'),
    path('budget/directeur/reserve-directeur/', ListeProjetsDirecteurReserveDirecteurView.as_view(), name='directeur-reserve-directeur'),
    path('budget/directeur/tous/', ListeProjetsDirecteurTousView.as_view(), name='directeur-tous'),
    path('budget/directeur/historique/', ListeProjetsDirecteurHistoriqueView.as_view(), name='directeur-historique'),
     
    # gets pour dividionnaire:
    path('budget/divisionnaire/valides-directeur/', ListeProjetsDivisionnaireValidesDirecteurView.as_view(), name='divisionnaire-valides-directeur'),
    # path('budget/divisionnaire/reserve-directeur/', ListeProjetsDivisionnaireReserveDirecteurView.as_view(), name='divisionnaire-reserve-directeur'),
    path('budget/divisionnaire/directeurStatus/', ListeProjetsDivisionnaireView.as_view(), name='divisionnaire-valides'),
    path('budget/divisionnaire/termines/', ListeProjetsDivisionnaireTerminesView.as_view(), name='divisionnaire-termines'),

    path('budget/divisionnaire/valides/', ListeProjetsDivisionnaireValidesView.as_view(), name='divisionnaire-valides'),
    path('budget/divisionnaire/rejetes/', ListeProjetsDivisionnaireRejetesView.as_view(), name='divisionnaire-rejetes'),
    path('budget/divisionnaire/tous/', ListeProjetsDivisionnaireTousView.as_view(), name='divisionnaire-tous'),
    path('budget/divisionnaire/historique/', ListeProjetsDivisionnaireHistoriqueView.as_view(), name='divisionnaire-historique'),
    
    
]


