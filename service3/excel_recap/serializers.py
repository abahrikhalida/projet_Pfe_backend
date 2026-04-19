
from rest_framework import serializers
from .models import ExcelUpload, BudgetRecord
from .mappings import REGION_MAPPING, ACTIVITE_MAPPING, get_famille_nom


class BudgetRecordSerializer(serializers.ModelSerializer):

    # 🔥 champs calculés
    region_nom = serializers.SerializerMethodField()
    activite_nom = serializers.SerializerMethodField()
    famille_nom = serializers.SerializerMethodField()

    # ✅ intervalle pour le frontend
    intervalle_pmt = serializers.SerializerMethodField()

    class Meta:
        model = BudgetRecord
        fields = '__all__'  # inclut intervalle_pmt automatiquement

    # ─────────────────────────
    # MAPPINGS
    # ─────────────────────────

    def get_region_nom(self, obj):
        code = str(obj.region or '').strip()
        return REGION_MAPPING.get(code, code)

    def get_activite_nom(self, obj):
        code = str(obj.activite or '').strip()
        return ACTIVITE_MAPPING.get(code, code)

    def get_famille_nom(self, obj):
        code = str(obj.famille or '').strip()
        return get_famille_nom(code)

    # ─────────────────────────
    # INTERVALLE PMT (READ)
    # ─────────────────────────

    def get_intervalle_pmt(self, obj):
        if obj.annee_debut_pmt and obj.annee_fin_pmt:
            return [obj.annee_debut_pmt, obj.annee_fin_pmt]
        return None

    # ─────────────────────────
    # INTERVALLE PMT (WRITE)
    # ─────────────────────────

    def create(self, validated_data):
        intervalle = self.initial_data.get('intervalle_pmt', None)

        if intervalle and len(intervalle) == 2:
            validated_data['annee_debut_pmt'] = intervalle[0]
            validated_data['annee_fin_pmt'] = intervalle[1]

        return super().create(validated_data)

    def update(self, instance, validated_data):
        intervalle = self.initial_data.get('intervalle_pmt', None)

        if intervalle and len(intervalle) == 2:
            instance.annee_debut_pmt = intervalle[0]
            instance.annee_fin_pmt = intervalle[1]

        return super().update(instance, validated_data)
    

class ExcelUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcelUpload
        fields = ['id', 'file_name', 'uploaded_at', 'status']

class ExcelFileSerializer(serializers.Serializer):
     file = serializers.FileField()