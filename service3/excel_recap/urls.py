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

    # creation projet:(nv , ancien)
    path('budget/nouveau-projet/', NouveauProjetView.as_view(), name='create-budget-manuel'),#valider
    path('budget/admin/patch-projet/<str:code_division>/',PatchProjetAdminView.as_view(),name='admin-patch-projet',),
    path('budget/responsable/modifier-projet/<str:code_division>/',ModifierProjetResponsableView.as_view(),name='responsable-modifier-projet',),
   
    #historique:
    path('budget/historique/<str:code_division>/',HistoriqueProjetView.as_view(),name='historique-projet'),#valider
    path('budget/historique/<str:code_division>/actif/',HistoriqueProjetView.as_view(),{'mode': 'actif'},name='historique-projet-actif'),#valider




    



    # procedure  validation par role:
    # path('budget/soumettre/<int:record_id>/',SoumettreProjetView.as_view()),
    path('budget/valider/directeur-region/<int:record_id>/',ValiderDirecteurRegionView.as_view()),
    path('budget/valider/chef/<int:record_id>/',ValiderChefView.as_view()),
    path('budget/valider/directeur/<int:record_id>/',ValiderDirecteurView.as_view()),
    path('budget/valider/divisionnaire/<int:record_id>/',ValiderDivisionnaireView.as_view()),
    path('budget/valider/divisionnaire/total/',ValiderTousProjetsDivisionnaireView.as_view(),name='valider-tous-divisionnaire'),

    # Listes par rôle
    #http://localhost:8083/recap/budget/projets/responsable/?statut=soumis
    path('budget/projets/responsable/',ListeProjetsResponsableView.as_view()),#valider

    #http://localhost:8083/recap/budget/projets/directeur-region/?statut=soumis
    # path('budget/projets/directeur-region/',ListeProjetsDirecteurRegionView.as_view()),#valider
    






    #valider

    # gets pour directeur region:
    path('budget/directeur-region/soumis/', ListeProjetsSoumisDRView.as_view(), name='dr-soumis'),
    path('budget/directeur-region/valides/', ListeProjetsValidesDRView.as_view(), name='dr-valides'),
    path('budget/directeur-region/rejetes/', ListeProjetsRejetesDRView.as_view(), name='dr-rejetes'),
    path('budget/directeur-region/reserve-directeur/', ListeProjetsReserveDirecteurDRView.as_view(), name='dr-reserve-directeur'),
    path('budget/directeur-region/tous/', ListeProjetsTousDRView.as_view(), name='dr-tous'),
    path('budget/directeur-region/valide-divisionnaire/',ListeProjetsValideDivisionnaireView.as_view(),name='valide-divisionnaire'),
    path('budget/directeur-region/rejete-divisionnaire/',ListeProjetsRejeteDivisionnaireView.as_view(),name='rejete-divisionnaire'),
    path('budget/directeur-region/annule-divisionnaire/',ListeProjetsAnnuleDivisionnaireView.as_view(),name='annule-divisionnaire'),
    path('budget/directeur-region/revoir/', ListeProjetsrevoirDRView.as_view(), name='dr-revoir'),

    # path('budget/directeur-region/historique/', ListeProjetsHistoriqueDRView.as_view(), name='dr-historique'),
    # path('budget/directeur-region/brouillon/', ListeProjetsBrouillonDRView.as_view(), name='dr-brouillon'),
    # path('budget/directeur-region/reserve-chef/', ListeProjetsReserveChefDRView.as_view(), name='dr-reserve-chef'),
   


   
    # gets pour chef:
    path('budget/chef/valider-DR/', ListeProjetsChefView.as_view(), name='chef-valides'),
    path('budget/chef/pre_approuves/', ListeProjetsChefValidesView.as_view(), name='chef-valides'),
    path('budget/chef/reserve-chef/', ListeProjetsChefReserveChefView.as_view(), name='chef-reserve-chef'),
    path('budget/chef/tous/', ListeProjetsChefTousView.as_view(), name='chef-tous'),
    # path('budget/chef/historique/', ListeProjetsChefHistoriqueView.as_view(), name='chef-historique'),




    # gets pour directeur:
    path('budget/directeur/valides-chef/', ListeProjetsDirecteurValidesChefView.as_view(), name='directeur-valides-chef'),
    # path('budget/directeur/reserve-chef/', ListeProjetsDirecteurReserveChefView.as_view(), name='directeur-reserve-chef'),
    path('budget/directeur/ChefStatus/', ListeProjetsDirecteurView.as_view(), name='directeur-projets'),
    path('budget/directeur/valides/', ListeProjetsDirecteurValidesView.as_view(), name='directeur-valides'),
    path('budget/directeur/reserve-directeur/', ListeProjetsDirecteurReserveDirecteurView.as_view(), name='directeur-reserve-directeur'),
    path('budget/directeur/tous/', ListeProjetsDirecteurTousView.as_view(), name='directeur-tous'),
    # path('budget/directeur/historique/', ListeProjetsDirecteurHistoriqueView.as_view(), name='directeur-historique'),
     


    # gets pour dividionnaire:
    path('budget/divisionnaire/valides-directeur/', ListeProjetsDivisionnaireValidesDirecteurView.as_view(), name='divisionnaire-valides-directeur'),
    path('budget/divisionnaire/termines/', ListeProjetsDivisionnaireTerminesView.as_view(), name='divisionnaire-termines'),
    path('budget/divisionnaire/valides/', ListeProjetsDivisionnaireValidesView.as_view(), name='divisionnaire-valides'),
    path('budget/divisionnaire/rejetes/', ListeProjetsDivisionnaireRejetesView.as_view(), name='divisionnaire-rejetes'),
    path('budget/divisionnaire/annules/', ListeProjetsDivisionnaireAnnulesView.as_view(), name='divisionnaire-annules'),
    path('budget/divisionnaire/tous/', ListeProjetsDivisionnaireTousView.as_view(), name='divisionnaire-tous'),
    # path('budget/divisionnaire/historique/', ListeProjetsDivisionnaireHistoriqueView.as_view(), name='divisionnaire-historique'),


    #export excel:
    path('budget/export/valides-divisionnaire/',ExportProjetsValidesDivisionnaireView.as_view(), name='export_valides_divisionnaire'),
    
    # path('budget/export/filtres/',ExportProjetsFiltresView.as_view(),name='export_filtres'),
    
    
]


