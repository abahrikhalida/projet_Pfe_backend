
# # models.py

# from django.db import models
# from django.utils import timezone
# from django.core.exceptions import ValidationError


# class ExcelUpload(models.Model):
#     file_name = models.CharField(max_length=255)
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(
#         max_length=20,
#         choices=[('pending','Pending'),('processed','Processed'),('failed','Failed')],
#         default='pending'
#     )

#     def __str__(self):
#         return f"{self.file_name} - {self.uploaded_at}"





# class BudgetRecord(models.Model):
#     upload = models.ForeignKey(ExcelUpload, on_delete=models.CASCADE, related_name='records')
#     activite = models.CharField(max_length=10, blank=True, null=True)
#     region = models.CharField(max_length=10, blank=True, null=True)
#     perm = models.CharField(max_length=255, blank=True, null=True)
#     famille = models.CharField(max_length=50, blank=True, null=True)
#     code_division = models.CharField(max_length=50, blank=True, null=True)
#     libelle = models.CharField(max_length=255, blank=True, null=True)
    
#     # Intervalle PMT
#     annee_debut_pmt = models.IntegerField(null=True, blank=True)
#     annee_fin_pmt = models.IntegerField(null=True, blank=True)
    
#     # Champs pour le filtrage
#     region_id = models.CharField(max_length=50, null=True, blank=True)
#     structure_id = models.CharField(max_length=50, null=True, blank=True)
#     created_by = models.IntegerField(null=True, blank=True)

#     # ✅ NOUVEAUX CHAMPS POUR LE VERSIONNEMENT
#     parent_id = models.IntegerField(null=True, blank=True)  # ID du projet original
#     version = models.IntegerField(default=1)  # Numéro de version
#     is_active = models.BooleanField(default=True)  # Version active ou archivée
#     version_comment = models.TextField(null=True, blank=True)  # Commentaire sur la modification

#     # Workflow validation
#     # STATUT_CHOICES = [
#     #     ('brouillon', 'Brouillon'),
#     #     ('soumis', 'Soumis'),
#     #     ('valide_directeur_region', 'Validé Directeur Région'),
#     #     ('valide_chef', 'Validé Chef'),
#     #     ('valide_directeur', 'Validé Directeur'),
#     #     ('valide_divisionnaire', 'Validé Divisionnaire'),
#     #     ('rejete', 'Rejeté'),
#     # ]
#     STATUT_CHOICES = [
#     ('brouillon',               'Brouillon'),
#     ('soumis',                  'Soumis'),
#     ('valide_directeur_region', 'Validé Directeur Région'),
#     ('rejete',                  'Rejeté'),
#     ('valide_agent',            'Validé Agent'),
#     ('reserve_agent',           'Réservé Agent'),
#     ('valide_chef',             'Validé Chef'),
#     ('reserve_chef',            'Réservé Chef'),
#     ('valide_directeur',        'Validé Directeur'),
#     ('reserve_directeur',       'Réservé Directeur'),
#     ('valide_divisionnaire',    'Validé Divisionnaire'),
# ]
    
#     TYPE_PROJET_CHOICES = [
#         ('en_cours', 'En cours'),
#         ('nouveau', 'Nouveau'),
#     ]

#     type_projet = models.CharField(max_length=20, choices=TYPE_PROJET_CHOICES, null=True, blank=True)

#     # Champs libres
#     description_technique = models.TextField(null=True, blank=True)
#     opportunite_projet = models.TextField(null=True, blank=True)

#     statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='brouillon')

#     # Validation workflow fields
#     commentaire_agent = models.TextField(blank=True, null=True)
#     valide_par_directeur_region = models.CharField(max_length=255, blank=True, null=True)
#     date_validation_directeur_region = models.DateTimeField(blank=True, null=True)
#     commentaire_directeur_region = models.TextField(blank=True, null=True)

#     valide_par_chef = models.CharField(max_length=255, blank=True, null=True)
#     date_validation_chef = models.DateTimeField(blank=True, null=True)
#     commentaire_chef = models.TextField(blank=True, null=True)

#     valide_par_directeur = models.CharField(max_length=255, blank=True, null=True)
#     date_validation_directeur = models.DateTimeField(blank=True, null=True)
#     commentaire_directeur = models.TextField(blank=True, null=True)

#     valide_par_divisionnaire = models.CharField(max_length=255, blank=True, null=True)
#     date_validation_divisionnaire = models.DateTimeField(blank=True, null=True)
#     commentaire_divisionnaire = models.TextField(blank=True, null=True)

#     rejete_par = models.CharField(max_length=255, blank=True, null=True)
#     date_rejet = models.DateTimeField(blank=True, null=True)
#     motif_rejet = models.TextField(blank=True, null=True)

#     # Champs numériques
#     cout_initial_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     cout_initial_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     realisation_cumul_n_mins1_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     realisation_cumul_n_mins1_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     real_s1_n_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     real_s1_n_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_s2_n_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_s2_n_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_cloture_n_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_cloture_n_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_n_plus1_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_n_plus1_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     reste_a_realiser_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     reste_a_realiser_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_n_plus2_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_n_plus2_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_n_plus3_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_n_plus3_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_n_plus4_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_n_plus4_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_n_plus5_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     prev_n_plus5_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
#     # Champs mensuels
#     janvier_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     janvier_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     fevrier_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     fevrier_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     mars_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     mars_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     avril_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     avril_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     mai_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     mai_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     juin_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     juin_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     juillet_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     juillet_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     aout_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     aout_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     septembre_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     septembre_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     octobre_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     octobre_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     novembre_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     novembre_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     decembre_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     decembre_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

#     class Meta:
#         # unique_together = [['code_division', 'version']]  # Un code_division peut avoir plusieurs versions
#         # ordering = ['-version']  # Trier par version décroissante
#         indexes = [
#         models.Index(
#             fields=['code_division', 'version'],
#             name='idx_code_division_version'
#         ),
#         models.Index(
#             fields=['code_division', 'is_active'],
#             name='idx_code_division_active'
#         ),
#     ]
#     ordering = ['-version']

#     def clean(self):
#         if self.annee_debut_pmt and self.annee_fin_pmt:
#             if self.annee_debut_pmt > self.annee_fin_pmt:
#                 raise ValidationError("L'année début doit être inférieure à l'année fin")
        
        
#         # Liste des paires (champ_total, champ_dex)
#         pairs = [
#             ('cout_initial_total', 'cout_initial_dont_dex'),
#             ('realisation_cumul_n_mins1_total', 'realisation_cumul_n_mins1_dont_dex'),
#             ('real_s1_n_total', 'real_s1_n_dont_dex'),
#             ('prev_s2_n_total', 'prev_s2_n_dont_dex'),
#             ('prev_cloture_n_total', 'prev_cloture_n_dont_dex'),
#             ('prev_n_plus1_total', 'prev_n_plus1_dont_dex'),
#             ('reste_a_realiser_total', 'reste_a_realiser_dont_dex'),
#             ('prev_n_plus2_total', 'prev_n_plus2_dont_dex'),
#             ('prev_n_plus3_total', 'prev_n_plus3_dont_dex'),
#             ('prev_n_plus4_total', 'prev_n_plus4_dont_dex'),
#             ('prev_n_plus5_total', 'prev_n_plus5_dont_dex'),
#             ('janvier_total', 'janvier_dont_dex'),
#             ('fevrier_total', 'fevrier_dont_dex'),
#             ('mars_total', 'mars_dont_dex'),
#             ('avril_total', 'avril_dont_dex'),
#             ('mai_total', 'mai_dont_dex'),
#             ('juin_total', 'juin_dont_dex'),
#             ('juillet_total', 'juillet_dont_dex'),
#             ('aout_total', 'aout_dont_dex'),
#             ('septembre_total', 'septembre_dont_dex'),
#             ('octobre_total', 'octobre_dont_dex'),
#             ('novembre_total', 'novembre_dont_dex'),
#             ('decembre_total', 'decembre_dont_dex'),
#         ]
        
#         for total_field, dex_field in pairs:
#             total = getattr(self, total_field)
#             dex = getattr(self, dex_field)
            
#             if total is not None and dex is not None and total < dex:
#                 raise ValidationError({
#                     total_field: f"Le total ({total}) ne peut pas être inférieur au DEX ({dex})",
#                     dex_field: f"Le DEX ({dex}) ne peut pas être supérieur au total ({total})"
#                 })
    
#     def save(self, *args, **kwargs):
#         # Appeler la validation avant la sauvegarde
#         self.clean()
#         super().save(*args, **kwargs)

#     # def save(self, *args, **kwargs):
#     #     # # Si c'est une nouvelle version, incrémenter automatiquement
#     #     # if not self.pk and self.parent_id:
#     #     #     parent = BudgetRecord.objects.get(id=self.parent_id)
#     #     #     self.version = parent.version + 1
#     #     super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.libelle} | {self.code_division} v{self.version} | {self.statut}"
# models.py - Version corrigée avec les bons noms de champs

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class ExcelUpload(models.Model):
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending','Pending'),('processed','Processed'),('failed','Failed')],
        default='pending'
    )

    def __str__(self):
        return f"{self.file_name} - {self.uploaded_at}"


class BudgetRecord(models.Model):
    upload = models.ForeignKey(ExcelUpload, on_delete=models.CASCADE, related_name='records')
    activite = models.CharField(max_length=10, blank=True, null=True)
    # region = models.CharField(max_length=10, blank=True, null=True)
    region_direction = models.CharField(max_length=50,blank=True,null=True,help_text="code_region si structure | code_direction si département")
    perm = models.CharField(max_length=255, blank=True, null=True)
    famille = models.CharField(max_length=50, blank=True, null=True)
    code_division = models.CharField(max_length=50, blank=True, null=True)
    libelle = models.CharField(max_length=255, blank=True, null=True)
    
    # Intervalle PMT
    annee_debut_pmt = models.IntegerField(null=True, blank=True)
    annee_fin_pmt = models.IntegerField(null=True, blank=True)
    
    # Champs pour le filtrage
    region_id = models.CharField(max_length=50, null=True, blank=True)
    structure_id = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    # Ajouter si absents :
    direction_id   = models.CharField(max_length=50, null=True, blank=True)
    departement_id = models.CharField(max_length=50, null=True, blank=True)

    # ✅ VERSIONNEMENT
    parent_id = models.IntegerField(null=True, blank=True)
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    version_comment = models.TextField(null=True, blank=True)

    # ================================================================
    # STATUTS SÉPARÉS
    # ================================================================
    
    # STATUT WORKFLOW - Suivi de l'avancement dans le circuit
    STATUT_WORKFLOW_CHOICES = [
        ('soumis', 'Soumis'),
        ('pre_approuve_chef', 'Pré-approuvé Chef'),
        ('reserve_chef', 'Réservé Chef'),
        ('reserve_directeur', 'Réservé Directeur'),
        ('approuve_directeur', 'Approuvé Directeur'),
    ]
    
    # STATUT FINAL - Décisions finales
    STATUT_FINAL_CHOICES = [
        ('valide_divisionnaire', 'Validé Divisionnaire'),
        ('rejete_divisionnaire', 'Rejeté Divisionnaire'),
        ('annule_divisionnaire', 'Annulé Divisionnaire'),
        ('valide_directeur_region', 'Validé Directeur Région'),
        ('rejete_directeur_region', 'Rejeté Directeur Région'),
    ]
    
    statut_workflow = models.CharField(
        max_length=30,
        choices=STATUT_WORKFLOW_CHOICES,
        null=True,
        blank=True,
        help_text="Avancement dans le circuit de validation"
    )
    
    statut_final = models.CharField(
        max_length=30,
        choices=STATUT_FINAL_CHOICES,
        null=True,
        blank=True,
        help_text="Statut final après décision terminale"
    )
    
    TYPE_PROJET_CHOICES = [
        ('en_cours', 'En cours'),
        ('nouveau', 'Nouveau'),
    ]

    type_projet = models.CharField(max_length=20, choices=TYPE_PROJET_CHOICES, null=True, blank=True)

    # Champs libres
    description_technique = models.TextField(null=True, blank=True)
    opportunite_projet = models.TextField(null=True, blank=True)

    # Propriété de compatibilité
    @property
    def statut(self):
        """Propriété de compatibilité retournant le statut actuel"""
        if self.statut_final:
            return self.statut_final
        return self.statut_workflow or 'brouillon'
    
    @statut.setter
    def statut(self, value):
        """Setter de compatibilité"""
        if value in dict(self.STATUT_FINAL_CHOICES).keys():
            self.statut_final = value
            self.statut_workflow = None
        elif value in dict(self.STATUT_WORKFLOW_CHOICES).keys():
            self.statut_workflow = value
        elif value == 'brouillon':
            self.statut_workflow = None
            self.statut_final = None

    # ================================================================
    # CHAMPS DE VALIDATION RENOMMÉS CORRECTEMENT
    # ================================================================
    
    
    # DIRECTEUR RÉGION - valide ou rejette
    valide_par_directeur_region = models.CharField(max_length=255, blank=True, null=True)
    date_validation_directeur_region = models.DateTimeField(blank=True, null=True)
    commentaire_directeur_region = models.TextField(blank=True, null=True)
    
    # Rejet par directeur région
    rejete_par_directeur_region = models.CharField(max_length=255, blank=True, null=True)
    date_rejet_directeur_region = models.DateTimeField(blank=True, null=True)
    motif_rejet_directeur_region = models.TextField(blank=True, null=True)
    
    # CHEF - pré-approuve ou réserve
    preapprouve_par_chef = models.CharField(max_length=255, blank=True, null=True)
    date_preapprouve_chef = models.DateTimeField(blank=True, null=True)
    commentaire_preapprouve_chef = models.TextField(blank=True, null=True)
    
    reserve_par_chef = models.CharField(max_length=255, blank=True, null=True)
    date_reserve_chef = models.DateTimeField(blank=True, null=True)
    commentaire_reserve_chef = models.TextField(blank=True, null=True)
    
    # DIRECTEUR NATIONAL - approuve ou réserve
    approuve_par_directeur = models.CharField(max_length=255, blank=True, null=True)
    date_approuve_directeur = models.DateTimeField(blank=True, null=True)
    commentaire_approuve_directeur = models.TextField(blank=True, null=True)
    
    reserve_par_directeur = models.CharField(max_length=255, blank=True, null=True)
    date_reserve_directeur = models.DateTimeField(blank=True, null=True)
    commentaire_reserve_directeur = models.TextField(blank=True, null=True)
    
    # DIVISIONNAIRE - valide, rejette ou annule
    valide_par_divisionnaire = models.CharField(max_length=255, blank=True, null=True)
    date_validation_divisionnaire = models.DateTimeField(blank=True, null=True)
    commentaire_divisionnaire = models.TextField(blank=True, null=True)
    
    rejete_par_divisionnaire = models.CharField(max_length=255, blank=True, null=True)
    date_rejet_divisionnaire = models.DateTimeField(blank=True, null=True)
    motif_rejet_divisionnaire = models.TextField(blank=True, null=True)
    
    annule_par_divisionnaire = models.CharField(max_length=255, blank=True, null=True)
    date_annulation_divisionnaire = models.DateTimeField(blank=True, null=True)
    motif_annulation_divisionnaire = models.TextField(blank=True, null=True)
    
    # Champs génériques (pour compatibilité et historiques)
    rejete_par = models.CharField(max_length=255, blank=True, null=True)
    date_rejet = models.DateTimeField(blank=True, null=True)
    motif_rejet = models.TextField(blank=True, null=True)

    # Champs numériques (inchangés)
    cout_initial_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    cout_initial_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    realisation_cumul_n_mins1_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    realisation_cumul_n_mins1_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    real_s1_n_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    real_s1_n_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_s2_n_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_s2_n_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_cloture_n_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_cloture_n_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_n_plus1_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_n_plus1_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    reste_a_realiser_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    reste_a_realiser_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_n_plus2_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_n_plus2_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_n_plus3_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_n_plus3_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_n_plus4_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_n_plus4_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_n_plus5_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prev_n_plus5_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    janvier_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    janvier_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    fevrier_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    fevrier_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    mars_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    mars_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    avril_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    avril_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    mai_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    mai_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    juin_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    juin_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    juillet_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    juillet_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    aout_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    aout_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    septembre_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    septembre_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    octobre_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    octobre_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    novembre_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    novembre_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    decembre_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    decembre_dont_dex = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['code_division', 'version'], name='idx_code_division_version'),
            models.Index(fields=['code_division', 'is_active'], name='idx_code_division_active'),
            models.Index(fields=['statut_workflow'], name='idx_statut_workflow'),
            models.Index(fields=['statut_final'], name='idx_statut_final'),
            models.Index(fields=['region_id', 'statut_workflow'], name='idx_region_workflow'),
        ]
        ordering = ['-version']

    def clean(self):
        if self.annee_debut_pmt and self.annee_fin_pmt:
            if self.annee_debut_pmt > self.annee_fin_pmt:
                raise ValidationError("L'année début doit être inférieure à l'année fin")
        
        pairs = [
            ('cout_initial_total', 'cout_initial_dont_dex'),
            ('realisation_cumul_n_mins1_total', 'realisation_cumul_n_mins1_dont_dex'),
            ('real_s1_n_total', 'real_s1_n_dont_dex'),
            ('prev_s2_n_total', 'prev_s2_n_dont_dex'),
            ('prev_cloture_n_total', 'prev_cloture_n_dont_dex'),
            ('prev_n_plus1_total', 'prev_n_plus1_dont_dex'),
            ('reste_a_realiser_total', 'reste_a_realiser_dont_dex'),
            ('prev_n_plus2_total', 'prev_n_plus2_dont_dex'),
            ('prev_n_plus3_total', 'prev_n_plus3_dont_dex'),
            ('prev_n_plus4_total', 'prev_n_plus4_dont_dex'),
            ('prev_n_plus5_total', 'prev_n_plus5_dont_dex'),
            ('janvier_total', 'janvier_dont_dex'),
            ('fevrier_total', 'fevrier_dont_dex'),
            ('mars_total', 'mars_dont_dex'),
            ('avril_total', 'avril_dont_dex'),
            ('mai_total', 'mai_dont_dex'),
            ('juin_total', 'juin_dont_dex'),
            ('juillet_total', 'juillet_dont_dex'),
            ('aout_total', 'aout_dont_dex'),
            ('septembre_total', 'septembre_dont_dex'),
            ('octobre_total', 'octobre_dont_dex'),
            ('novembre_total', 'novembre_dont_dex'),
            ('decembre_total', 'decembre_dont_dex'),
        ]
        
        for total_field, dex_field in pairs:
            total = getattr(self, total_field)
            dex = getattr(self, dex_field)
            
            if total is not None and dex is not None and total < dex:
                raise ValidationError({
                    total_field: f"Le total ({total}) ne peut pas être inférieur au DEX ({dex})",
                    dex_field: f"Le DEX ({dex}) ne peut pas être supérieur au total ({total})"
                })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        workflow = self.statut_workflow or 'brouillon'
        final = self.statut_final or '-'
        return f"{self.libelle} | {self.code_division} v{self.version} | Workflow:{workflow} | Final:{final}"