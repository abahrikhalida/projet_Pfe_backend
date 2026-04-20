from django.urls import path
from .views import *

urlpatterns = [
    # Upload
    path('upload/',        ExcelUploadView.as_view(),      name='excel-upload'),
    path('uploads/',       UploadListView.as_view(),        name='upload-list'),
    path('records/',       BudgetRecordListView.as_view(),  name='record-list'),#valider

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




    # validation
    # path('budget/soumettre/<int:record_id>/',                  SoumettreProjetView.as_view()),
    # path('budget/valider/directeur-region/<int:record_id>/',   ValiderDirecteurRegionView.as_view()),
    # path('budget/valider/chef/<int:record_id>/',               ValiderChefView.as_view()),
    # path('budget/valider/directeur/<int:record_id>/',          ValiderDirecteurView.as_view()),
    # path('budget/valider/divisionnaire/<int:record_id>/',      ValiderDivisionnnaireView.as_view()),
    # path('budget/statut/<int:record_id>/', StatutValidationView.as_view()),






    path('budget/soumettre/<int:record_id>/',SoumettreProjetView.as_view()),

    # Workflow validation
    path('budget/valider/directeur-region/<int:record_id>/',ValiderDirecteurRegionView.as_view()),
    path('budget/valider/agent/<int:record_id>/',ValiderAgentView.as_view()),
    path('budget/valider/chef/<int:record_id>/',ValiderChefView.as_view()),
    path('budget/valider/directeur/<int:record_id>/',ValiderDirecteurView.as_view()),
    path('budget/valider/divisionnaire/<int:record_id>/',ValiderDivisionnnaireView.as_view()),

    # Listes par rôle
    # Listes par rôle
    #http://localhost:8083/recap/budget/projets/responsable/?statut=brouillon
    path('budget/projets/responsable/',ListeProjetsResponsableView.as_view()),#valider
    #http://localhost:8083/recap/budget/projets/directeur-region/?statut=soumis
    path('budget/projets/directeur-region/',ListeProjetsDirecteurRegionView.as_view()),#valider
    
    path('budget/projets/agent/',ListeProjetsAgentView.as_view()),
    path('budget/projets/chef/',ListeProjetsChefView.as_view()),
    path('budget/projets/directeur/',ListeProjetsDirecteurView.as_view()),
    path('budget/projets/divisionnaire/',ListeProjetsDivisionnnaireView.as_view()),


    # 1. Responsable Structure → voir ses projets en brouillon
    path('mes-projets/brouillon/',MesProjetsBrouillonView.as_view(),name='mes-projets-brouillon'),
    
    # 2. Directeur Région → voir les projets soumis dans sa région
    path('projets/soumis/region/',ProjetsSoumisParRegionView.as_view(),name='projets-soumis-region'),
    
    # 2b. Version avec filtres optionnels (optionnel)
    path('projets/soumis/region/filtre/',ProjetsSoumisParRegionFiltreView.as_view(),name='projets-soumis-region-filtre'),
    
    # 3. Chef → voir les projets validés par directeurs région
    path('projets/valides/directeur-region/',ProjetsValidesDirecteurRegionView.as_view(),name='projets-valides-directeur-region'),
    
    # 4. Directeur → voir les projets validés par les chefs
    path('projets/valides/chef/',ProjetsValidesChefView.as_view(),name='projets-valides-chef'),
    
    # 5. Divisionnaire → voir les projets validés par les directeurs
    path('projets/valides/directeur/',ProjetsValidesDirecteurView.as_view(),name='projets-valides-directeur'),
    
]


