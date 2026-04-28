# from django.contrib import admin
# from .models import ExcelUpload, BudgetRecord

# @admin.register(BudgetRecord)
# class BudgetRecordAdmin(admin.ModelAdmin):
#     list_display = [
#         'id', 'region', 'famille', 'activite', 'libelle',
#         'credit_initial_total',
#         'realisation_cumul_total',
#         'prev_2016_total', 'prev_2017_total',
#         'prev_2018_total', 'prev_2019_total',
#         'janvier_total', 'fevrier_total', 'mars_total',
#         'avril_total', 'mai_total', 'juin_total',
#         'juillet_total', 'aout_total', 'septembre_total',
#         'octobre_total', 'novembre_total', 'decembre_total',
#     ]
#     list_filter = ['region', 'famille', 'activite']
#     search_fields = ['libelle', 'region']
from django.contrib import admin
from .models import ExcelUpload, BudgetRecord

@admin.register(ExcelUpload)
class ExcelUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'status', 'uploaded_at']

@admin.register(BudgetRecord)
class BudgetRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'region_direction', 'famille', 'activite', 'libelle',
        'cout_initial_total',
        'realisation_cumul_n_mins1_total',
        'real_s1_n_total',
        'prev_s2_n_total',
        'prev_cloture_n_total',
        'prev_n_plus1_total',
        'reste_a_realiser_total',
        'prev_n_plus2_total',
        'prev_n_plus3_total',
        'prev_n_plus4_total',
        'prev_n_plus5_total',
        'janvier_total', 'fevrier_total', 'mars_total',
        'avril_total', 'mai_total', 'juin_total',
        'juillet_total', 'aout_total', 'septembre_total',
        'octobre_total', 'novembre_total', 'decembre_total',
    ]
    list_filter = ['region_direction', 'famille', 'activite']
    search_fields = ['libelle', 'region_direction']