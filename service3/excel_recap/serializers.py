
from rest_framework import serializers
from .models import ExcelUpload, BudgetRecord
from .mappings import  ACTIVITE_MAPPING
import requests


def get_service_param_url():
    try:
        print("[DEBUG] Trying to resolve SERVICE-NODE-PARAM from Eureka...")
        res = requests.get(
            "http://localhost:8761/eureka/apps/SERVICE-NODE-PARAM",
            headers={'Accept': 'application/json'},
            timeout=5
        )
        
        if res.status_code == 200:
            data = res.json()
            instances = data['application']['instance']
            instance = instances[0] if isinstance(instances, list) else instances
            host = instance['hostName']
            port = instance['port']['$']
            url = f"http://{host}:{port}"
            print(f"[DEBUG] Service resolved from Eureka: {url}")
            
            # Vérifier si le service est accessible
            try:
                test_resp = requests.get(f"{url}/params/regions", timeout=2)
                if test_resp.status_code == 200:
                    print(f"[DEBUG] Service is accessible on {url}")
                    return url
                else:
                    print(f"[DEBUG] Service on {url} returned {test_resp.status_code}, using fallback")
            except Exception as test_e:
                print(f"[DEBUG] Service on {url} not accessible: {test_e}")
        else:
            print(f"[DEBUG] Eureka returned status {res.status_code}")
            
    except Exception as e:
        print(f"[DEBUG] Error resolving SERVICE-NODE-PARAM from Eureka: {e}")
    
    # Fallback vers le bon port
    print("[DEBUG] Using fallback URL: http://localhost:8083")
    return "http://localhost:8083"

class BudgetRecordSerializer(serializers.ModelSerializer):

    # 🔥 champs calculés
    region_nom = serializers.SerializerMethodField()
    activite_nom = serializers.SerializerMethodField()
    famille_nom = serializers.SerializerMethodField()
    direction_nom  = serializers.SerializerMethodField()
    #####################################################
    direction_region_code = serializers.SerializerMethodField()
    direction_region_nom = serializers.SerializerMethodField()

    # ✅ intervalle pour le frontend
    intervalle_pmt = serializers.SerializerMethodField()

    class Meta:
        model = BudgetRecord
        fields = '__all__'  # inclut intervalle_pmt automatiquement
    
    # def get_region_nom(self, obj):
    #     """Récupère le nom de la région depuis le service param"""
    #     try:
    #         # Récupérer le token depuis le contexte de la requête
    #         request = self.context.get('request')
    #         token = request.headers.get('Authorization', '') if request else ''
            
    #         service_url = get_service_param_url()
            
    #         # Appel à votre endpoint avec l'ID MongoDB
    #         response = requests.get(
    #             f"{service_url}/params/regions/id/{obj.region_id}",  # Utilise region_id (ObjectId MongoDB)
    #             headers={'Authorization': token},
    #             timeout=3
    #         )
            
    #         if response.status_code == 200:
    #             region_data = response.json().get('data', {})
    #             return region_data.get('nom_region')  # Retourne le nom
    #         else:
    #             return obj.region  # Fallback: retourne le code si erreur
                
    #     except Exception as e:
    #         # Log l'erreur mais ne casse pas la sérialisation
    #         print(f"Erreur récupération nom région: {e}")
    #         return obj.region  # Fallback: retourne le code
    def get_region_nom(self, obj):
        """Récupère le nom de la région depuis le service param"""
        try:
            request = self.context.get('request')
            token = request.headers.get('Authorization', '') if request else ''
            
            if not token:
                print("[DEBUG REGION] No token available")
                return obj.region
            
            service_url = get_service_param_url()
            
            # ✅ Utilisez le code de la région, pas l'ID MongoDB
            url = f"{service_url}/params/regions/{obj.region}"
            print(f"[DEBUG REGION] Calling URL: {url}")
            
            response = requests.get(
                url,
                headers={'Authorization': token},
                timeout=3
            )
            
            print(f"[DEBUG REGION] Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"[DEBUG REGION] Response: {response_data}")
                
                # Selon votre MongoDB, le champ est 'nom_region'
                region_data = response_data.get('data', {})
                nom = region_data.get('nom_region')
                
                if nom:
                    print(f"[DEBUG REGION] Found nom_region: {nom}")
                    return nom
                else:
                    print(f"[DEBUG REGION] No nom_region in response")
                    return obj.region
            else:
                print(f"[DEBUG REGION] Error {response.status_code}, response: {response.text}")
                return obj.region
                
        except Exception as e:
            print(f"[DEBUG REGION] Exception: {e}")
            return obj.region
        

    # def get_famille_nom(self, obj):
    #     """Récupère le nom de la famille depuis le service param"""
    #     try:
    #         request = self.context.get('request')
    #         token = request.headers.get('Authorization', '') if request else ''
            
    #         service_url = get_service_param_url()
            
    #         # DEBUG: Afficher l'URL complète
    #         url = f"{service_url}/params/familles/by-code/{obj.famille}"
    #         print(f"[DEBUG FAMILLE] Calling URL: {url}")
    #         print(f"[DEBUG FAMILLE] Token: {token[:50]}..." if token else "[DEBUG FAMILLE] No token")
            
    #         response = requests.get(
    #             url,
    #             headers={'Authorization': token},
    #             timeout=3
    #         )
            
    #         print(f"[DEBUG FAMILLE] Status: {response.status_code}")
    #         print(f"[DEBUG FAMILLE] Response: {response.text[:200]}")
            
    #         if response.status_code == 200:
    #             famille_data = response.json().get('data', {})
    #             nom = famille_data.get('nom_famille')
    #             print(f"[DEBUG FAMILLE] Found nom_famille: {nom}")
    #             return nom
    #         else:
    #             print(f"[DEBUG FAMILLE] Error, returning fallback: {obj.famille}")
    #             return obj.famille
                
    #     except Exception as e:
    #         print(f"[DEBUG FAMILLE] Exception: {e}")
    #         return obj.famille
    def get_famille_nom(self, obj):
        """
        Récupère le nom de la famille selon le type de projet
        - Projet structure (region) → /params/familles/by-code/
        - Projet département (direction) → /params/familles-direction/code/
        """
        if not obj.famille:
            return None
        
        try:
            request = self.context.get('request')
            token = request.headers.get('Authorization', '') if request else ''
            service_url = get_service_param_url()
            
            # 🔥 LA MODIFICATION CLÉ : Détection du type de projet
            if obj.region and not obj.direction:
                # Cas 1: Projet structure (a une région)
                url = f"{service_url}/params/familles/by-code/{obj.famille}"
                print(f"[DEBUG] Appel API familles (structure): {url}")
                
            elif obj.direction and not obj.region:
                # Cas 2: Projet département (a une direction)
                url = f"{service_url}/params/familles-direction/code/{obj.famille}"
                print(f"[DEBUG] Appel API familles-direction (département): {url}")
                
            else:
                # Cas 3: Projet non reconnu
                print(f"[DEBUG] Type de projet non reconnu - region={obj.region}, direction={obj.direction}")
                return obj.famille
            
            response = requests.get(
                url,
                headers={'Authorization': token},
                timeout=3
            )
            
            if response.status_code == 200:
                famille_data = response.json().get('data', {})
                nom = famille_data.get('nom_famille')
                return nom if nom else obj.famille
            else:
                return obj.famille
                
        except Exception as e:
            print(f"[DEBUG] Exception: {e}")
            return obj.famille  
    
    
    # ── Nom de la direction (département uniquement) ──────────────────
    def get_direction_nom(self, obj):
        """Résout le nom depuis obj.direction via /params/directions/code/{code}"""
        if not obj.direction:
            return None
        try:
            request     = self.context.get('request')
            token       = request.headers.get('Authorization', '') if request else ''
            service_url = get_service_param_url()
            url         = f"{service_url}/params/directions/code/{obj.direction}"
            resp        = requests.get(url, headers={'Authorization': token}, timeout=3)
            if resp.status_code == 200:
                return resp.json().get('data', {}).get('nom_direction', obj.direction)
        except Exception:
            pass
        return obj.direction
    def get_direction_region_code(self, obj):
        """
        Retourne le code direction (si projet département) ou code région (si projet structure)
        """
        if obj.direction and not obj.region:
            # Projet département
            return obj.direction
        elif obj.region and not obj.direction:
            # Projet structure
            return obj.region
        return None

    def get_direction_region_nom(self, obj):
        """
        Retourne le nom de la direction (si projet département) ou nom de la région (si projet structure)
        """
        if obj.direction and not obj.region:
            # Projet département - récupérer le nom de la direction
            try:
                request = self.context.get('request')
                token = request.headers.get('Authorization', '') if request else ''
                service_url = get_service_param_url()
                url = f"{service_url}/params/directions/code/{obj.direction}"
                resp = requests.get(url, headers={'Authorization': token}, timeout=3)
                if resp.status_code == 200:
                    return resp.json().get('data', {}).get('nom_direction', obj.direction)
                else:
                    return obj.direction
            except Exception:
                return obj.direction
                
        elif obj.region and not obj.direction:
            # Projet structure - récupérer le nom de la région
            try:
                request = self.context.get('request')
                token = request.headers.get('Authorization', '') if request else ''
                service_url = get_service_param_url()
                url = f"{service_url}/params/regions/{obj.region}"
                resp = requests.get(url, headers={'Authorization': token}, timeout=3)
                if resp.status_code == 200:
                    region_data = resp.json().get('data', {})
                    return region_data.get('nom_region', obj.region)
                else:
                    return obj.region
            except Exception:
                return obj.region
                
        return None
    # ─────────────────────────
    # MAPPINGS
    # ─────────────────────────

    # def get_region_nom(self, obj):
    #     code = str(obj.region or '').strip()
    #     return REGION_MAPPING.get(code, code)

    def get_activite_nom(self, obj):
        code = str(obj.activite or '').strip()
        return ACTIVITE_MAPPING.get(code, code)

    
    # ─────────────────────────
    # INTERVALLE PMT (READ)
    # ─────────────────────────
    def get_intervalle_pmt(self, obj):
        if obj.annee_debut_pmt and obj.annee_fin_pmt:
            return [obj.annee_debut_pmt, obj.annee_fin_pmt]
        return None

    # def get_intervalle_pmt(self, obj):
    #     if obj.annee_debut_pmt and obj.annee_fin_pmt:
    #         return [obj.annee_debut_pmt, obj.annee_fin_pmt]
    #     return None

    # # ─────────────────────────
    # # INTERVALLE PMT (WRITE)
    # # ─────────────────────────

    # def create(self, validated_data):
    #     intervalle = self.initial_data.get('intervalle_pmt', None)

    #     if intervalle and len(intervalle) == 2:
    #         validated_data['annee_debut_pmt'] = intervalle[0]
    #         validated_data['annee_fin_pmt'] = intervalle[1]

    #     return super().create(validated_data)

    # def update(self, instance, validated_data):
    #     intervalle = self.initial_data.get('intervalle_pmt', None)

    #     if intervalle and len(intervalle) == 2:
    #         instance.annee_debut_pmt = intervalle[0]
    #         instance.annee_fin_pmt = intervalle[1]

    #     return super().update(instance, validated_data)
    # ─────────────────────────────────────────────────────────────────
    # WRITE : gérer intervalle_pmt et calcul automatique fin = debut + 4
    # ─────────────────────────────────────────────────────────────────
    def _process_intervalle(self, validated_data):
        """Calcule automatiquement annee_fin_pmt = annee_debut_pmt + 4"""
        
        # Récupérer les données brutes de la requête
        intervalle = self.initial_data.get('intervalle_pmt', None)
        annee_debut = self.initial_data.get('annee_debut_pmt', None)
        
        # Cas 1: L'utilisateur envoie intervalle_pmt = [debut, fin]
        if intervalle and isinstance(intervalle, list) and len(intervalle) == 2:
            validated_data['annee_debut_pmt'] = intervalle[0]
            validated_data['annee_fin_pmt'] = intervalle[1]
            print(f"[DEBUG] Cas 1: intervalle {intervalle}")
        
        # Cas 2: L'utilisateur envoie intervalle_pmt = [debut] uniquement
        elif intervalle and isinstance(intervalle, list) and len(intervalle) == 1:
            validated_data['annee_debut_pmt'] = intervalle[0]
            validated_data['annee_fin_pmt'] = intervalle[0] + 4
            print(f"[DEBUG] Cas 2: debut={intervalle[0]}, fin={intervalle[0] + 4}")
        
        # Cas 3: L'utilisateur envoie directement annee_debut_pmt
        elif annee_debut:
            validated_data['annee_debut_pmt'] = annee_debut
            validated_data['annee_fin_pmt'] = annee_debut + 4
            print(f"[DEBUG] Cas 3: debut={annee_debut}, fin={annee_debut + 4}")
        
        # Cas 4: annee_debut_pmt est déjà dans validated_data
        elif validated_data.get('annee_debut_pmt'):
            debut = validated_data['annee_debut_pmt']
            validated_data['annee_fin_pmt'] = debut + 4
            print(f"[DEBUG] Cas 4: debut={debut}, fin={debut + 4}")
        
        else:
            print(f"[DEBUG] Aucun cas détecté pour intervalle")
        
        return validated_data

    def create(self, validated_data):
        print(f"[DEBUG CREATE] initial_data: {self.initial_data}")
        print(f"[DEBUG CREATE] validated_data avant processing: {validated_data}")
        
        validated_data = self._process_intervalle(validated_data)
        
        print(f"[DEBUG CREATE] validated_data après processing: annee_debut_pmt={validated_data.get('annee_debut_pmt')}, annee_fin_pmt={validated_data.get('annee_fin_pmt')}")
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        print(f"[DEBUG UPDATE] initial_data: {self.initial_data}")
        
        validated_data = self._process_intervalle(validated_data)
        
        print(f"[DEBUG UPDATE] après processing: annee_debut_pmt={validated_data.get('annee_debut_pmt')}, annee_fin_pmt={validated_data.get('annee_fin_pmt')}")
        
        return super().update(instance, validated_data)
    
class ExcelUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcelUpload
        fields = ['id', 'file_name', 'uploaded_at', 'status']

class ExcelFileSerializer(serializers.Serializer):
     file = serializers.FileField()

    # def get_activite_nom(self, obj):
    #         """Récupère le nom de l'activité depuis le service param"""
    #         try:
    #             request = self.context.get('request')
    #             token = request.headers.get('Authorization', '') if request else ''
                
    #             service_url = get_service_param_url()
                
    #             # Adaptez l'endpoint selon votre API
    #             response = requests.get(
    #                 f"{service_url}/params/activites/code/{obj.activite}",
    #                 headers={'Authorization': token},
    #                 timeout=3
    #             )
                
    #             if response.status_code == 200:
    #                 activite_data = response.json().get('data', {})
    #                 return activite_data.get('nom')
    #             else:
    #                 return obj.activie
                    
    #         except Exception as e:
    #             print(f"Erreur récupération nom activité: {e}")
    #             return obj.activite

    # def get_famille_nom(self, obj):
    #         """Récupère le nom de la famille depuis le service param"""
    #         try:
    #             request = self.context.get('request')
    #             token = request.headers.get('Authorization', '') if request else ''
                
    #             service_url = get_service_param_url()
                
    #             # Adaptez l'endpoint selon votre API
    #             response = requests.get(
    #                 f"{service_url}/params/familles/by-code/{obj.famille}",
    #                 headers={'Authorization': token},
    #                 timeout=3
    #             )
                
    #             if response.status_code == 200:
    #                 famille_data = response.json().get('data', {})
    #                 return famille_data.get('nom_famille')
    #             else:
    #                 return obj.famille
                    
    #         except Exception as e:
    #             print(f"Erreur récupération nom famille: {e}")
    #             return obj.famille