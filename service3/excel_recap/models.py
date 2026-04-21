
# models.py

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
    region = models.CharField(max_length=10, blank=True, null=True)
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

    # ✅ NOUVEAUX CHAMPS POUR LE VERSIONNEMENT
    parent_id = models.IntegerField(null=True, blank=True)  # ID du projet original
    version = models.IntegerField(default=1)  # Numéro de version
    is_active = models.BooleanField(default=True)  # Version active ou archivée
    version_comment = models.TextField(null=True, blank=True)  # Commentaire sur la modification

    # Workflow validation
    # STATUT_CHOICES = [
    #     ('brouillon', 'Brouillon'),
    #     ('soumis', 'Soumis'),
    #     ('valide_directeur_region', 'Validé Directeur Région'),
    #     ('valide_chef', 'Validé Chef'),
    #     ('valide_directeur', 'Validé Directeur'),
    #     ('valide_divisionnaire', 'Validé Divisionnaire'),
    #     ('rejete', 'Rejeté'),
    # ]
    STATUT_CHOICES = [
    ('brouillon',               'Brouillon'),
    ('soumis',                  'Soumis'),
    ('valide_directeur_region', 'Validé Directeur Région'),
    ('rejete',                  'Rejeté'),
    ('valide_agent',            'Validé Agent'),
    ('reserve_agent',           'Réservé Agent'),
    ('valide_chef',             'Validé Chef'),
    ('reserve_chef',            'Réservé Chef'),
    ('valide_directeur',        'Validé Directeur'),
    ('reserve_directeur',       'Réservé Directeur'),
    ('valide_divisionnaire',    'Validé Divisionnaire'),
]
    
    TYPE_PROJET_CHOICES = [
        ('en_cours', 'En cours'),
        ('nouveau', 'Nouveau'),
    ]

    type_projet = models.CharField(max_length=20, choices=TYPE_PROJET_CHOICES, null=True, blank=True)

    # Champs libres
    description_technique = models.TextField(null=True, blank=True)
    opportunite_projet = models.TextField(null=True, blank=True)

    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='brouillon')

    # Validation workflow fields
    commentaire_agent = models.TextField(blank=True, null=True)
    valide_par_directeur_region = models.CharField(max_length=255, blank=True, null=True)
    date_validation_directeur_region = models.DateTimeField(blank=True, null=True)
    commentaire_directeur_region = models.TextField(blank=True, null=True)

    valide_par_chef = models.CharField(max_length=255, blank=True, null=True)
    date_validation_chef = models.DateTimeField(blank=True, null=True)
    commentaire_chef = models.TextField(blank=True, null=True)

    valide_par_directeur = models.CharField(max_length=255, blank=True, null=True)
    date_validation_directeur = models.DateTimeField(blank=True, null=True)
    commentaire_directeur = models.TextField(blank=True, null=True)

    valide_par_divisionnaire = models.CharField(max_length=255, blank=True, null=True)
    date_validation_divisionnaire = models.DateTimeField(blank=True, null=True)
    commentaire_divisionnaire = models.TextField(blank=True, null=True)

    rejete_par = models.CharField(max_length=255, blank=True, null=True)
    date_rejet = models.DateTimeField(blank=True, null=True)
    motif_rejet = models.TextField(blank=True, null=True)

    # Champs numériques
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
    
    # Champs mensuels
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
        # unique_together = [['code_division', 'version']]  # Un code_division peut avoir plusieurs versions
        # ordering = ['-version']  # Trier par version décroissante
        indexes = [
        models.Index(
            fields=['code_division', 'version'],
            name='idx_code_division_version'
        ),
        models.Index(
            fields=['code_division', 'is_active'],
            name='idx_code_division_active'
        ),
    ]
    ordering = ['-version']

    def clean(self):
        if self.annee_debut_pmt and self.annee_fin_pmt:
            if self.annee_debut_pmt > self.annee_fin_pmt:
                raise ValidationError("L'année début doit être inférieure à l'année fin")

    def save(self, *args, **kwargs):
        # # Si c'est une nouvelle version, incrémenter automatiquement
        # if not self.pk and self.parent_id:
        #     parent = BudgetRecord.objects.get(id=self.parent_id)
        #     self.version = parent.version + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.libelle} | {self.code_division} v{self.version} | {self.statut}"