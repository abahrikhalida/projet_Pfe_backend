
from rest_framework import serializers
from .models import Agent, User
import cloudinary.uploader
from django.contrib.auth.hashers import make_password
import secrets
import requests
from .discovery import discover_service


SERVICE_NAME = "SERVICE-NODE-PARAM"


# ==================================================
# USER SERIALIZER
# ==================================================
class UserSerializer(serializers.ModelSerializer):
    photo_profil = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "id", "email", "nom", "prenom", "password",
            "role", "region_id", "structure_id",
            "is_staff", "is_superuser", "photo_profil"
        ]
        extra_kwargs = {
            "password":     {"write_only": True, "required": False},
            "role":         {"required": True},
            "region_id":    {"required": False, "allow_null": True},
            "structure_id": {"required": False, "allow_null": True},
        }

    # ==================================================
    # VALIDATION GLOBALE
    # ==================================================
    def validate(self, data):
        role         = data.get('role', getattr(self.instance, 'role', None))
        region_id    = data.get('region_id')
        structure_id = data.get('structure_id')

        if role == 'directeur_region':
            if region_id:
                # Fourni → on vérifie
                self._verify_region(region_id)
            data['structure_id'] = None
            # region_id pas fourni → OK, on laisse null

        elif role == 'responsable_structure':
            if structure_id and not region_id:
                raise serializers.ValidationError({
                    "region_id": "Obligatoire si structure_id est fourni."
                })
            if region_id:
                self._verify_region(region_id)
            if structure_id and region_id:
                self._verify_structure(structure_id, region_id)

        else:
            data['region_id']    = None
            data['structure_id'] = None

        return data

    # # ==================================================
    # # VERIFY REGION
    # # ==================================================
    # def _verify_region(self, region_id):
    #     try:
    #         base_url = discover_service(SERVICE_NAME)
    #         #http://localhost:8083/params/regions/id/69da8935965379472c259d76
    #         url      = f"{base_url}/params/regions/id/{region_id}"

    #         print(f"[DEBUG] URL région : {url}")

    #         resp = requests.get(url, timeout=3)

    #         print(f"[DEBUG] Status     : {resp.status_code}")
    #         print(f"[DEBUG] Body       : {resp.text}")

    #         if resp.status_code == 400:
    #             raise serializers.ValidationError({
    #                 "region_id": "ID région invalide (format ObjectId incorrect)."
    #             })

    #         if resp.status_code == 404:
    #             raise serializers.ValidationError({
    #                 "region_id": "Région introuvable."
    #             })

    #         if resp.status_code != 200:
    #             raise serializers.ValidationError({
    #                 "region_id": "Erreur lors de la vérification de la région."
    #             })

    #         body   = resp.json()
    #         region = body.get('data', {})

    #         if not region:
    #             raise serializers.ValidationError({
    #                 "region_id": "Réponse région invalide."
    #             })

    #         if not region.get('is_active', True):
    #             raise serializers.ValidationError({
    #                 "region_id": "Région inactive."
    #             })

    #         return region

    #     except serializers.ValidationError:
    #         raise

    #     except requests.exceptions.RequestException as e:
    #         print(f"[DEBUG] RequestException région : {e}")
    #         raise serializers.ValidationError({
    #             "region_id": "Service région indisponible, réessayez."
    #         })

    # # ==================================================
    # # VERIFY STRUCTURE
    # # ==================================================
    # def _verify_structure(self, structure_id, region_id):
    #     try:
    #         base_url = discover_service(SERVICE_NAME)
    #         url      = f"{base_url}/api/structures/{structure_id}"

    #         print(f"[DEBUG] URL structure : {url}")

    #         resp = requests.get(url, timeout=3)

    #         print(f"[DEBUG] Status        : {resp.status_code}")
    #         print(f"[DEBUG] Body          : {resp.text}")

    #         if resp.status_code == 400:
    #             raise serializers.ValidationError({
    #                 "structure_id": "ID structure invalide (format ObjectId incorrect)."
    #             })

    #         if resp.status_code == 404:
    #             raise serializers.ValidationError({
    #                 "structure_id": "Structure introuvable."
    #             })

    #         if resp.status_code != 200:
    #             raise serializers.ValidationError({
    #                 "structure_id": "Erreur lors de la vérification de la structure."
    #             })

    #         body      = resp.json()
    #         structure = body.get('data', {})

    #         if not structure:
    #             raise serializers.ValidationError({
    #                 "structure_id": "Réponse structure invalide."
    #             })

    #         if str(structure.get('region')) != str(region_id):
    #             raise serializers.ValidationError({
    #                 "structure_id": "Cette structure n'appartient pas à la région indiquée."
    #             })

    #         if not structure.get('is_active', True):
    #             raise serializers.ValidationError({
    #                 "structure_id": "Structure inactive."
    #             })

    #         return structure

    #     except serializers.ValidationError:
    #         raise

    #     except requests.exceptions.RequestException as e:
    #         print(f"[DEBUG] RequestException structure : {e}")
    #         raise serializers.ValidationError({
    #             "structure_id": "Service structure indisponible, réessayez."
    #         })

    # ==================================================
    # CREATE
    # ==================================================
    def create(self, validated_data):
        photo = validated_data.pop("photo_profil", None)

        if not validated_data.get("password"):
            generated_password         = secrets.token_urlsafe(8)
            validated_data["password"] = make_password(generated_password)
            self.generated_password    = generated_password

        if photo:
            result = cloudinary.uploader.upload(photo)
            validated_data["photo_profil"] = result["secure_url"]

        user = super().create(validated_data)
        user.generated_password = getattr(self, "generated_password", None)
        return user

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self, instance, validated_data):
        photo = validated_data.pop("photo_profil", None)

        if photo:
            result = cloudinary.uploader.upload(photo)
            validated_data["photo_profil"] = result["secure_url"]

        password = validated_data.pop("password", None)
        if password:
            validated_data["password"] = make_password(password)

        return super().update(instance, validated_data)


# ==================================================
# AGENT SERIALIZER
# ==================================================
class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Agent
        fields = [
            'id', 'nom', 'prenom', 'email', 'adresse',
            'date_naissance', 'sexe', 'telephone',
            'matricule', 'is_activated'
        ]