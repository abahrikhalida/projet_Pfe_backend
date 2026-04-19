
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.db.models import Sum
from .models import ExcelUpload, BudgetRecord
from .serializers import ExcelUploadSerializer, BudgetRecordSerializer, ExcelFileSerializer
from .utils import auto_correct_records, parse_excel
from .mappings import REGION_MAPPING, ACTIVITE_MAPPING, FAMILLE_ORDER, get_famille_nom
from .discovery import discover_service
from django.utils import timezone
# External service URLs
SERVICE1_APP = 'AUTHENTICATION-SERVICE'
import requests
import xml.etree.ElementTree as ET

# ─────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────
def get_service1_url():
    try:
        res = requests.get("http://registry:8761/eureka/apps/AUTHENTICATION-SERVICE", headers={'Accept': 'application/json'})
        instances = res.json()['application']['instance']
        instance = instances[0] if isinstance(instances, list) else instances
        host = instance['hostName']
        port = instance['port']['$']
        return f"http://{host}:{port}"
    except Exception as e:
        print("Error resolving service1 from Eureka:", e)
        return "http://localhost:8001"


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

NUMERIC_FIELDS = [
    'cout_initial_total', 'cout_initial_dont_dex',
    'realisation_cumul_n_mins1_total', 'realisation_cumul_n_mins1_dont_dex',
    'real_s1_n_total', 'real_s1_n_dont_dex',
    'prev_s2_n_total', 'prev_s2_n_dont_dex',
    'prev_cloture_n_total', 'prev_cloture_n_dont_dex',
    'prev_n_plus1_total', 'prev_n_plus1_dont_dex',
    'reste_a_realiser_total', 'reste_a_realiser_dont_dex',
    'prev_n_plus2_total', 'prev_n_plus2_dont_dex',
    'prev_n_plus3_total', 'prev_n_plus3_dont_dex',
    'prev_n_plus4_total', 'prev_n_plus4_dont_dex',
    'prev_n_plus5_total', 'prev_n_plus5_dont_dex',
    'janvier_total', 'fevrier_total', 'mars_total',
    'avril_total', 'mai_total', 'juin_total',
    'juillet_total', 'aout_total', 'septembre_total',
    'octobre_total', 'novembre_total', 'decembre_total',
]

PREVISION_FIELDS = [
    'prev_s2_n_total', 'prev_s2_n_dont_dex',
    'prev_cloture_n_total', 'prev_cloture_n_dont_dex',
    'prev_n_plus1_total', 'prev_n_plus1_dont_dex',
    'reste_a_realiser_total', 'reste_a_realiser_dont_dex',
    'prev_n_plus2_total', 'prev_n_plus2_dont_dex',
    'prev_n_plus3_total', 'prev_n_plus3_dont_dex',
    'prev_n_plus4_total', 'prev_n_plus4_dont_dex',
    'prev_n_plus5_total', 'prev_n_plus5_dont_dex',
]

SAISIE_FIELDS = [
    'cout_initial_total', 'cout_initial_dont_dex',
    'realisation_cumul_n_mins1_total', 'realisation_cumul_n_mins1_dont_dex',
    'real_s1_n_total', 'real_s1_n_dont_dex',
    'janvier_total', 'janvier_dont_dex',
    'fevrier_total', 'fevrier_dont_dex',
    'mars_total', 'mars_dont_dex',
    'avril_total', 'avril_dont_dex',
    'mai_total', 'mai_dont_dex',
    'juin_total', 'juin_dont_dex',
    'juillet_total', 'juillet_dont_dex',
    'aout_total', 'aout_dont_dex',
    'septembre_total', 'septembre_dont_dex',
    'octobre_total', 'octobre_dont_dex',
    'novembre_total', 'novembre_dont_dex',
    'decembre_total', 'decembre_dont_dex',
]

TOTAL_DONT_DEX_PAIRS = [
    ('cout_initial_total',              'cout_initial_dont_dex'),
    ('realisation_cumul_n_mins1_total', 'realisation_cumul_n_mins1_dont_dex'),
    ('real_s1_n_total',                 'real_s1_n_dont_dex'),
    ('janvier_total',                   'janvier_dont_dex'),
    ('fevrier_total',                   'fevrier_dont_dex'),
    ('mars_total',                      'mars_dont_dex'),
    ('avril_total',                     'avril_dont_dex'),
    ('mai_total',                       'mai_dont_dex'),
    ('juin_total',                      'juin_dont_dex'),
    ('juillet_total',                   'juillet_dont_dex'),
    ('aout_total',                      'aout_dont_dex'),
    ('septembre_total',                 'septembre_dont_dex'),
    ('octobre_total',                   'octobre_dont_dex'),
    ('novembre_total',                  'novembre_dont_dex'),
    ('decembre_total',                  'decembre_dont_dex'),
]

REGION_EXCLUSIONS   = [None, '', 'Région', 'REGION', 'region', 'Total', 'TOTAL']
FAMILLE_EXCLUSIONS  = [None, '', 'Famille', 'FAMILLE', 'famille', 'Total', 'TOTAL']
ACTIVITE_EXCLUSIONS = [None, '', 'Activité', 'ACTIVITE', 'activite', 'Total', 'TOTAL']


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def build_aggregation():
    return {f: Sum(f) for f in NUMERIC_FIELDS}


def apply_mapping(data, key_field, mapping):
    result = []
    for row in data:
        code = str(row.get(key_field, '') or '').strip()
        row[key_field + '_code'] = code
        row[key_field + '_nom'] = mapping.get(code, code)
        result.append(row)
    return result


def clean_queryset(qs):
    return qs.exclude(activite__isnull=True)\
             .exclude(activite__in=ACTIVITE_EXCLUSIONS)\
             .exclude(region__isnull=True)\
             .exclude(region__in=REGION_EXCLUSIONS)\
             .exclude(famille__isnull=True)\
             .exclude(famille__in=FAMILLE_EXCLUSIONS)


def group_by_famille(data):
    grouped = {}

    for row in data:
        code = str(row.get('famille', '') or '').strip()
        if not code:
            continue

        nom = get_famille_nom(code)

        if nom not in grouped:
            grouped[nom] = {field: 0 for field in NUMERIC_FIELDS}
            grouped[nom]['famille_nom'] = nom

        for field in NUMERIC_FIELDS:
            val = row.get(field) or 0
            grouped[nom][field] += float(val)

    return sorted(
        grouped.values(),
        key=lambda x: FAMILLE_ORDER.index(x['famille_nom'])
        if x['famille_nom'] in FAMILLE_ORDER else 99
    )


# ─────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from .remote_auth import RemoteJWTAuthentication


class ExcelUploadView(APIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAgent]

    def post(self, request):
        serializer = ExcelFileSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        file = serializer.validated_data['file']

        if not file.name.endswith(('.xlsx', '.xls')):
            return Response({'error': 'Only Excel files allowed'}, status=400)

        upload = ExcelUpload.objects.create(file_name=file.name, status='pending')

        try:
            count = parse_excel(file, upload)
            qs = clean_queryset(BudgetRecord.objects.filter(upload=upload))
            corrected_count = auto_correct_records(qs)

            upload.status = 'processed'
            upload.save()

            return Response({
                'message': f'{count} records importés',
                'upload_id': upload.id,
                'corrections': {
                    'records_corrigés': corrected_count,
                    'message': (
                        f'{corrected_count} record(s) corrigé(s) automatiquement'
                        if corrected_count
                        else 'Aucune correction nécessaire'
                    )
                }
            }, status=201)

        except Exception as e:
            upload.status = 'failed'
            upload.save()
            return Response({'error': str(e)}, status=500)


class UploadListView(generics.ListAPIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAgent]

    queryset = ExcelUpload.objects.all().order_by('-uploaded_at')
    serializer_class = ExcelUploadSerializer


class BudgetRecordListView(generics.ListAPIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BudgetRecordSerializer

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        structure_id = getattr(user, 'structure_id', None)
        region_id = getattr(user, 'region_id', None)
        
        qs = BudgetRecord.objects.all()
        
        if role == 'responsable_structure':
            # Responsable structure → voit sa structure
            if structure_id:
                qs = qs.filter(structure_id=structure_id)
            else:
                return BudgetRecord.objects.none()
        elif role == 'directeur_region':
            # Directeur région → voit sa région
            if region_id:
                qs = qs.filter(region_id=region_id)
            else:
                return BudgetRecord.objects.none()
        elif role == 'agent':
            # Agent → voit ses projets
            qs = qs.filter(created_by=user.id)
        # Chef, directeur, divisionnaire → voient tout
        
        uid = self.request.query_params.get('upload_id')
        if uid:
            qs = qs.filter(upload_id=uid)
        
        return qs.order_by('-id')

# ─────────────────────────────────────────
# RECAPS
# ─────────────────────────────────────────
class RecapParRegionView(APIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = BudgetRecord.objects.all()

        uid = request.query_params.get('upload_id')
        if uid:
            qs = qs.filter(upload_id=uid)

        qs = clean_queryset(qs)

        data = list(
            qs.values('region')
            .annotate(**build_aggregation())
            .order_by('region')
        )

        total = qs.aggregate(**build_aggregation())

        service_url = get_service_param_url()
        token = request.headers.get('Authorization', '')
        
        result = []
        for row in data:
            code = str(row.get('region', '') or '').strip()
            
            # Récupérer le nom de la région
            region_name = code  # fallback
            if code and code not in ['', '-', 'None']:
                try:
                    url = f"{service_url}/params/regions/{code}"
                    response = requests.get(url, headers={'Authorization': token}, timeout=5)
                    if response.status_code == 200:
                        region_data = response.json().get('data', {})
                        region_name = region_data.get('nom_region', code)
                        print(f"[DEBUG] Region {code} -> {region_name}")
                except Exception as e:
                    print(f"[DEBUG] Error: {e}")
            
            # Remplacer la clé 'region' par le nom
            row['region'] = region_name
            
            result.append(row)

        return Response({
            "regions": result,
            "total_division": total
        })

class RecapParFamilleView(APIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("=" * 80)
        print("[DEBUG] === Début RecapParFamilleView ===")
        print("=" * 80)
        
        qs = BudgetRecord.objects.all()

        uid = request.query_params.get('upload_id')
        if uid:
            qs = qs.filter(upload_id=uid)

        qs = clean_queryset(qs)

        data = list(
            qs.values('famille')
            .annotate(**build_aggregation())
            .order_by('famille')
        )

        total = qs.aggregate(**build_aggregation())

        service_url = get_service_param_url()
        print(f"[DEBUG] Service URL: {service_url}")
        
        # Récupérer le token de l'utilisateur actuel
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
        print(f"[DEBUG] Token present: {bool(token)}")
        
        # Récupérer TOUTES les familles en UNE SEULE requête avec le token
        famille_mapping = {}
        try:
            print("[DEBUG] Fetching all families from service with token...")
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            response = requests.get(f"{service_url}/params/familles", headers=headers, timeout=5)
            print(f"[DEBUG] Response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"[DEBUG] Response keys: {response_data.keys() if isinstance(response_data, dict) else 'list'}")
                
                # Gérer différentes structures de réponse
                if isinstance(response_data, dict):
                    if 'data' in response_data:
                        familles_list = response_data['data']
                    else:
                        familles_list = [response_data] if response_data else []
                elif isinstance(response_data, list):
                    familles_list = response_data
                else:
                    familles_list = []
                
                print(f"[DEBUG] Number of families found: {len(familles_list)}")
                
                for famille in familles_list:
                    if isinstance(famille, dict):
                        code = famille.get('code_famille') or famille.get('code') or famille.get('id')
                        nom = famille.get('nom_famille') or famille.get('name') or famille.get('libelle') or famille.get('nom')
                        if code:
                            famille_mapping[str(code)] = nom
                            print(f"[DEBUG] Mapped {code} -> {nom}")
                
                print(f"[DEBUG] Total mapped families: {len(famille_mapping)}")
            else:
                print(f"[DEBUG] Failed to fetch families: {response.status_code}")
                if response.text:
                    print(f"[DEBUG] Response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"[DEBUG] Error fetching families: {e}")
            import traceback
            traceback.print_exc()
        
        # Appliquer le mapping
        result = []
        for row in data:
            code = str(row.get('famille', '') or '').strip()
            if code and code not in ['', '-', 'None']:
                row['famille'] = famille_mapping.get(code, code)
            else:
                row['famille'] = '-'
            print(f"[DEBUG] Mapped: {code} -> {row['famille']}")
            result.append(row)

        print("=" * 80)
        print("[DEBUG] === Fin RecapParFamilleView ===")
        print("=" * 80)

        return Response({
            "familles": result,
            "total_division_production": total
        })
class RecapParActiviteView(APIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAgent]

    def get(self, request):
        qs = BudgetRecord.objects.all()

        uid = request.query_params.get('upload_id')
        if uid:
            qs = qs.filter(upload_id=uid)

        qs = clean_queryset(qs)

        data = list(
            qs.values('activite')
            .annotate(**build_aggregation())
            .order_by('activite')
        )

        total_qs = qs.aggregate(**build_aggregation())

        return Response({
            "activites": apply_mapping(data, 'activite', ACTIVITE_MAPPING),
            "total_division": total_qs,
        })


class RecapGlobalView(APIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAgent]

    def get(self, request):
        qs = BudgetRecord.objects.all()

        uid = request.query_params.get('upload_id')
        if uid:
            qs = qs.filter(upload_id=uid)

        qs = clean_queryset(qs)
        agg = build_aggregation()
        
        # Récupérer le token
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
        service_url = get_service_param_url()
        
        # Récupérer toutes les régions
        region_mapping = {}
        try:
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            response = requests.get(f"{service_url}/params/regions", headers=headers, timeout=5)
            
            if response.status_code == 200:
                response_data = response.json()
                regions_list = response_data.get('data', [])
                for region in regions_list:
                    code = region.get('code_region')
                    nom = region.get('nom_region')
                    if code:
                        region_mapping[str(code)] = nom
        except Exception:
            pass
        
        # Récupérer toutes les familles
        famille_mapping = {}
        try:
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            response = requests.get(f"{service_url}/params/familles", headers=headers, timeout=5)
            
            if response.status_code == 200:
                response_data = response.json()
                familles_list = response_data.get('data', [])
                for famille in familles_list:
                    code = famille.get('code_famille')
                    nom = famille.get('nom_famille')
                    if code:
                        famille_mapping[str(code)] = nom
        except Exception:
            pass
        
        # Traiter les régions
        regions_data = list(qs.values('region').annotate(**agg))
        regions_result = []
        for row in regions_data:
            code = str(row.get('region', '') or '').strip()
            region_nom = region_mapping.get(code, code) if code and code not in ['', '-', 'None'] else '-'
            regions_result.append({
                'region_code': code,
                'region_nom': region_nom,
                **{k: v for k, v in row.items() if k != 'region'}
            })
        
        # Traiter les familles
        familles_data = list(qs.values('famille').annotate(**agg))
        familles_result = []
        for row in familles_data:
            code = str(row.get('famille', '') or '').strip()
            famille_nom = famille_mapping.get(code, code) if code and code not in ['', '-', 'None'] else '-'
            familles_result.append({
                'famille_code': code,
                'famille_nom': famille_nom,
                **{k: v for k, v in row.items() if k != 'famille'}
            })
        
        # Traiter les activités
        activites_data = list(qs.values('activite').annotate(**agg))
        activites_result = []
        for row in activites_data:
            code = str(row.get('activite', '') or '').strip()
            activite_nom = ACTIVITE_MAPPING.get(code, code)
            activites_result.append({
                'activite_code': code,
                'activite_nom': activite_nom,
                **{k: v for k, v in row.items() if k != 'activite'}
            })

        return Response({
            'par_region': regions_result,
            'par_famille': familles_result,
            'par_activite': activites_result,
        })
    


class RecapFamilleParActiviteView(APIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = BudgetRecord.objects.all()

        uid = request.query_params.get('upload_id')
        if uid:
            qs = qs.filter(upload_id=uid)

        qs = clean_queryset(qs)

        data = list(
            qs.values('activite', 'famille')
            .annotate(**build_aggregation())
            .order_by('activite', 'famille')
        )

        # Récupérer le token
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
        service_url = get_service_param_url()
        
        # Récupérer toutes les familles
        famille_mapping = {}
        try:
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            response = requests.get(f"{service_url}/params/familles", headers=headers, timeout=5)
            
            if response.status_code == 200:
                response_data = response.json()
                familles_list = response_data.get('data', [])
                for famille in familles_list:
                    code = famille.get('code_famille')
                    nom = famille.get('nom_famille')
                    if code:
                        famille_mapping[str(code)] = nom
        except Exception:
            pass

        activites = {}

        for row in data:
            act_code = str(row.get('activite') or '').strip()
            act_nom = ACTIVITE_MAPPING.get(act_code, act_code)
            fam_code = str(row.get('famille') or '').strip()
            fam_nom = famille_mapping.get(fam_code, fam_code) if fam_code and fam_code not in ['', '-', 'None'] else '-'

            if act_code not in activites:
                activites[act_code] = {
                    'activite_code': act_code,
                    'activite_nom': act_nom,
                    'familles': {},
                    'total': {f: 0 for f in NUMERIC_FIELDS},
                }

            if fam_code not in activites[act_code]['familles']:
                activites[act_code]['familles'][fam_code] = {
                    'famille_code': fam_code,
                    'famille_nom': fam_nom,
                    **{f: 0 for f in NUMERIC_FIELDS}
                }

            for field in NUMERIC_FIELDS:
                val = float(row.get(field) or 0)
                activites[act_code]['familles'][fam_code][field] += val
                activites[act_code]['total'][field] += val

        result = []
        total_global = {f: 0 for f in NUMERIC_FIELDS}

        for act in activites.values():
            familles = sorted(
                act['familles'].values(),
                key=lambda x: FAMILLE_ORDER.index(x['famille_nom'])
                if x['famille_nom'] in FAMILLE_ORDER else 99
            )

            result.append({
                'activite_code': act['activite_code'],
                'activite_nom': act['activite_nom'],
                'familles': familles,
                'total_activite': act['total'],
            })

            for f in NUMERIC_FIELDS:
                total_global[f] += act['total'][f]

        return Response({
            'detail': result,
            'total_global': total_global,
        })

class RecapRegionFamilleView(APIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAgent]
    """
    GET /api/recap/region-famille/?upload_id=1
    Retourne chaque région avec ses familles + total par région
    """

    def get(self, request):
        qs = BudgetRecord.objects.all()

        uid = request.query_params.get('upload_id')
        if uid:
            qs = qs.filter(upload_id=uid)

        qs = clean_queryset(qs)

        data = list(
            qs.values('region', 'famille')
            .annotate(**build_aggregation())
            .order_by('region', 'famille')
        )

        # Récupérer le token
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
        service_url = get_service_param_url()
        
        # Récupérer toutes les régions
        region_mapping = {}
        try:
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            response = requests.get(f"{service_url}/params/regions", headers=headers, timeout=5)
            
            if response.status_code == 200:
                response_data = response.json()
                regions_list = response_data.get('data', [])
                for region in regions_list:
                    code = region.get('code_region')
                    nom = region.get('nom_region')
                    if code:
                        region_mapping[str(code)] = nom
        except Exception:
            pass
        
        # Récupérer toutes les familles
        famille_mapping = {}
        try:
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            response = requests.get(f"{service_url}/params/familles", headers=headers, timeout=5)
            
            if response.status_code == 200:
                response_data = response.json()
                familles_list = response_data.get('data', [])
                for famille in familles_list:
                    code = famille.get('code_famille')
                    nom = famille.get('nom_famille')
                    if code:
                        famille_mapping[str(code)] = nom
        except Exception:
            pass

        regions = {}

        for row in data:
            reg_code = str(row.get('region') or '').strip()
            reg_nom = region_mapping.get(reg_code, reg_code) if reg_code and reg_code not in ['', '-', 'None'] else '-'
            fam_code = str(row.get('famille') or '').strip()
            fam_nom = famille_mapping.get(fam_code, fam_code) if fam_code and fam_code not in ['', '-', 'None'] else '-'

            if reg_code not in regions:
                regions[reg_code] = {
                    'region_code': reg_code,
                    'region_nom': reg_nom,
                    'familles': {},
                    'total': {f: 0 for f in NUMERIC_FIELDS},
                }

            if fam_code not in regions[reg_code]['familles']:
                regions[reg_code]['familles'][fam_code] = {
                    'famille_code': fam_code,
                    'famille_nom': fam_nom,
                    **{f: 0 for f in NUMERIC_FIELDS}
                }

            for field in NUMERIC_FIELDS:
                val = float(row.get(field) or 0)
                regions[reg_code]['familles'][fam_code][field] += val
                regions[reg_code]['total'][field] += val

        result = []
        total_global = {f: 0 for f in NUMERIC_FIELDS}

        for reg_code, reg_data in sorted(regions.items()):
            familles_triees = sorted(
                reg_data['familles'].values(),
                key=lambda x: FAMILLE_ORDER.index(x['famille_nom'])
                if x['famille_nom'] in FAMILLE_ORDER else 99
            )

            result.append({
                'region_code': reg_data['region_code'],
                'region_nom': reg_data['region_nom'],
                'familles': familles_triees,
                'total_region': reg_data['total'],
            })

            for f in NUMERIC_FIELDS:
                total_global[f] += reg_data['total'][f]

        return Response({
            'detail': result,
            'total_global': total_global,
        })

# ─────────────────────────────────────────
# PDF
# ─────────────────────────────────────────
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime

class BudgetRecordPDFView(APIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        record = get_object_or_404(BudgetRecord, pk=pk)

        # Récupérer l'année de début PMT
        annee_debut = record.annee_debut_pmt
        
        # Si l'année n'est pas définie, utiliser l'année courante + 1 comme fallback
        current_year = datetime.now().year
        if not annee_debut:
            annee_debut = current_year + 1
            
        # N = année de début PMT - 1
        N = annee_debut - 1
        N_plus_1 = N + 1
        N_plus_2 = N + 2
        N_plus_3 = N + 3
        N_plus_4 = N + 4
        N_plus_5 = N + 5
        
        # Les années de la période PMT
        annee_fin = record.annee_fin_pmt if record.annee_fin_pmt else N_plus_5

        activite = ACTIVITE_MAPPING.get(record.activite, record.activite or '-')
        region   = REGION_MAPPING.get(record.region, record.region or '-')
        famille  = get_famille_nom(record.famille or '-')

        buffer = BytesIO()
        doc    = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("RAPPORT BUDGET", styles['Title']))
        elements.append(Spacer(1, 10))

        info_data = [
            ["Activité",  activite],
            ["Région",    region],
            ["Famille",   famille],
            ["Libellé",   record.libelle or '-'],
            ["Période PMT", f"{annee_debut} - {annee_fin}"]
        ]

        info_table = Table(info_data, colWidths=[120, 350])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME',   (0, 0), (-1, -1), 'Helvetica'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 15))

        def v(val):
            return val if val is not None else 0

        main_data = [
            ["Désignation", "Total", "Dont DEX"],
            [f"Coût Global Initial PMT {annee_debut}/{annee_fin}", v(record.cout_initial_total), v(record.cout_initial_dont_dex)],
            [f"Réalisations Cumulées à fin {N} au coût réel", v(record.realisation_cumul_n_mins1_total), v(record.realisation_cumul_n_mins1_dont_dex)],
            [f"Prévisions de Clôture {N}", v(record.prev_cloture_n_total), v(record.prev_cloture_n_dont_dex)],
            [f"Prévisions {N_plus_1}", v(record.prev_n_plus1_total), v(record.prev_n_plus1_dont_dex)],
            [f"Reste à Réaliser {N_plus_2}/{annee_fin}", v(record.reste_a_realiser_total), v(record.reste_a_realiser_dont_dex)],
            [f"Prévisions {N_plus_2}", v(record.prev_n_plus2_total), v(record.prev_n_plus2_dont_dex)],
            [f"Prévisions {N_plus_3}", v(record.prev_n_plus3_total), v(record.prev_n_plus3_dont_dex)],
            [f"Prévisions {N_plus_4}", v(record.prev_n_plus4_total), v(record.prev_n_plus4_dont_dex)],
            [f"Prévisions {N_plus_5}", v(record.prev_n_plus5_total), v(record.prev_n_plus5_dont_dex)],
        ]

        main_table = Table(main_data, colWidths=[280, 100, 100])
        main_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
            ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.whitesmoke),
            ('BACKGROUND', (0, 3), (-1, 3), colors.whitesmoke),
            ('BACKGROUND', (0, 5), (-1, 5), colors.whitesmoke),
            ('BACKGROUND', (0, 7), (-1, 7), colors.whitesmoke),
            ('BACKGROUND', (0, 9), (-1, 9), colors.whitesmoke),
            ('ALIGN',  (1, 0), (-1, -1), 'CENTER'),
            ('GRID',   (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ]))

        elements.append(Paragraph("<b>Données budgétaires</b>", styles['Heading2']))
        elements.append(main_table)
        elements.append(Spacer(1, 15))

        mensuel_data = [
            ["Mois", f"Prévisions {N_plus_2} - Total", f"Prévisions {N_plus_2} - Dont DEX"],
            ["Janvier",   v(record.janvier_total),   v(record.janvier_dont_dex)],
            ["Février",   v(record.fevrier_total),   v(record.fevrier_dont_dex)],
            ["Mars",      v(record.mars_total),      v(record.mars_dont_dex)],
            ["Avril",     v(record.avril_total),     v(record.avril_dont_dex)],
            ["Mai",       v(record.mai_total),       v(record.mai_dont_dex)],
            ["Juin",      v(record.juin_total),      v(record.juin_dont_dex)],
            ["Juillet",   v(record.juillet_total),   v(record.juillet_dont_dex)],
            ["Août",      v(record.aout_total),      v(record.aout_dont_dex)],
            ["Septembre", v(record.septembre_total), v(record.septembre_dont_dex)],
            ["Octobre",   v(record.octobre_total),   v(record.octobre_dont_dex)],
            ["Novembre",  v(record.novembre_total),  v(record.novembre_dont_dex)],
            ["Décembre",  v(record.decembre_total),  v(record.decembre_dont_dex)],
        ]

        mensuel_table = Table(mensuel_data, colWidths=[180, 150, 150])
        mensuel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
            ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN',  (1, 0), (-1, -1), 'CENTER'),
            ('GRID',   (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ]))

        elements.append(Paragraph(f"<b>Répartition mensuelle — Prévisions {N_plus_2}</b>", styles['Heading2']))
        elements.append(mensuel_table)

        doc.build(elements)
        buffer.seek(0)

        return HttpResponse(
            buffer,
            content_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="budget_{record.id}.pdf"'
            },
        )

# ─────────────────────────────────────────
# VÉRIFICATION CALCULS
# ─────────────────────────────────────────


class VerificationCalculsView(APIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAgent]
    """
    GET /verification/?upload_id=1
    Vérifie la cohérence des calculs pour chaque record
    """

    def get(self, request):
        print("[DEBUG] === Début VerificationCalculsView ===")
        qs = BudgetRecord.objects.all()

        uid = request.query_params.get('upload_id')
        print(f"[DEBUG] upload_id param: {uid}")
        if uid:
            qs = qs.filter(upload_id=uid)
            print(f"[DEBUG] Filtered by upload_id={uid}, count={qs.count()}")

        qs = clean_queryset(qs)

        errors   = []
        warnings = []
        total    = qs.count()
        ok_count = 0
        print(f"[DEBUG] Total records after clean_queryset: {total}")

        TOLERANCE = 1

        def val(x):
            return float(x or 0)

        def check(record, label, gauche, droite):
            diff = abs(gauche - droite)
            if diff > TOLERANCE:
                print(f"[DEBUG] Check failed - Record ID: {record.id}, Label: {label}, Diff: {diff}")
                return {
                    'record_id':  record.id,
                    'libelle':    record.libelle or '-',
                    'region':     REGION_MAPPING.get(record.region, record.region or '-'),
                    'famille':    get_famille_nom(record.famille or '-'),
                    'activite':   ACTIVITE_MAPPING.get(record.activite, record.activite or '-'),
                    'regle':      label,
                    'gauche':     round(gauche, 2),
                    'droite':     round(droite, 2),
                    'difference': round(diff, 2),
                }
            return None

        for idx, record in enumerate(qs):
            print(f"[DEBUG] --- Processing record {idx+1}/{total} (ID: {record.id}) ---")
            record_errors = []

            # Check 1
            gauche1 = val(record.real_s1_n_total) + val(record.prev_s2_n_total)
            droite1 = val(record.prev_cloture_n_total)
            print(f"[DEBUG] Record {record.id} - Check1: gauche={gauche1}, droite={droite1}")
            e = check(record, "Réal.S1 (total) + Prév.S2 (total) = Prév.Clôture N (total)", gauche1, droite1)
            if e: 
                record_errors.append(e)
                print(f"[DEBUG] Record {record.id} - Check1 FAILED")

            # Check 2
            gauche2 = val(record.real_s1_n_dont_dex) + val(record.prev_s2_n_dont_dex)
            droite2 = val(record.prev_cloture_n_dont_dex)
            print(f"[DEBUG] Record {record.id} - Check2: gauche={gauche2}, droite={droite2}")
            e = check(record, "Réal.S1 (DEX) + Prév.S2 (DEX) = Prév.Clôture N (DEX)", gauche2, droite2)
            if e: 
                record_errors.append(e)
                print(f"[DEBUG] Record {record.id} - Check2 FAILED")

            # Check 3
            gauche3 = (val(record.prev_n_plus2_total) + val(record.prev_n_plus3_total)
                      + val(record.prev_n_plus4_total) + val(record.prev_n_plus5_total))
            droite3 = val(record.reste_a_realiser_total)
            print(f"[DEBUG] Record {record.id} - Check3: gauche={gauche3}, droite={droite3}")
            e = check(record, "Reste à Réaliser (total) = Prév.N+2 + N+3 + N+4 + N+5 (total)", gauche3, droite3)
            if e: 
                record_errors.append(e)
                print(f"[DEBUG] Record {record.id} - Check3 FAILED")

            # Check 4
            gauche4 = (val(record.prev_n_plus2_dont_dex) + val(record.prev_n_plus3_dont_dex)
                      + val(record.prev_n_plus4_dont_dex) + val(record.prev_n_plus5_dont_dex))
            droite4 = val(record.reste_a_realiser_dont_dex)
            print(f"[DEBUG] Record {record.id} - Check4: gauche={gauche4}, droite={droite4}")
            e = check(record, "Reste à Réaliser (DEX) = Prév.N+2 + N+3 + N+4 + N+5 (DEX)", gauche4, droite4)
            if e: 
                record_errors.append(e)
                print(f"[DEBUG] Record {record.id} - Check4 FAILED")

            # Check 5
            somme_mois = (
                val(record.janvier_total)   + val(record.fevrier_total)  +
                val(record.mars_total)      + val(record.avril_total)    +
                val(record.mai_total)       + val(record.juin_total)     +
                val(record.juillet_total)   + val(record.aout_total)     +
                val(record.septembre_total) + val(record.octobre_total)  +
                val(record.novembre_total)  + val(record.decembre_total)
            )
            print(f"[DEBUG] Record {record.id} - Check5: somme_mois={somme_mois}, prev_n_plus1={val(record.prev_n_plus1_total)}")
            e = check(record, "Prév.N+1 (total) = Somme des 12 mois (total)", somme_mois, val(record.prev_n_plus1_total))
            if e: 
                record_errors.append(e)
                print(f"[DEBUG] Record {record.id} - Check5 FAILED")

            # Check 6
            gauche6 = (val(record.realisation_cumul_n_mins1_total) + val(record.prev_cloture_n_total)
                      + val(record.prev_n_plus1_total) + val(record.reste_a_realiser_total))
            droite6 = val(record.cout_initial_total)
            print(f"[DEBUG] Record {record.id} - Check6: gauche={gauche6}, droite={droite6}")
            e = check(record, "Coût Global (total) = Réal.Cumul N-1 + Prév.Clôture N + Prév.N+1 + Reste à Réaliser (total)", gauche6, droite6)
            if e: 
                record_errors.append(e)
                print(f"[DEBUG] Record {record.id} - Check6 FAILED")

            # Check 7
            gauche7 = (val(record.realisation_cumul_n_mins1_dont_dex) + val(record.prev_cloture_n_dont_dex)
                      + val(record.prev_n_plus1_dont_dex) + val(record.reste_a_realiser_dont_dex))
            droite7 = val(record.cout_initial_dont_dex)
            print(f"[DEBUG] Record {record.id} - Check7: gauche={gauche7}, droite={droite7}")
            e = check(record, "Coût Global (DEX) = Réal.Cumul N-1 + Prév.Clôture N + Prév.N+1 + Reste à Réaliser (DEX)", gauche7, droite7)
            if e: 
                record_errors.append(e)
                print(f"[DEBUG] Record {record.id} - Check7 FAILED")

            if record_errors:
                errors.extend(record_errors)
                print(f"[DEBUG] Record {record.id} has {len(record_errors)} error(s)")
            else:
                ok_count += 1
                print(f"[DEBUG] Record {record.id} OK")

        print(f"[DEBUG] === Verification Summary: total={total}, ok={ok_count}, errors={len(errors)} ===")
        
        response_data = {
            'resume': {
                'total_records':  total,
                'records_ok':     ok_count,
                'records_errors': total - ok_count,
                'total_erreurs':  len(errors),
            },
            'erreurs': errors,
        }
        
        print(f"[DEBUG] Response prepared, sending {len(errors)} errors")
        return Response(response_data)


# ─────────────────────────────────────────
# SAISIE MANUELLE — NOUVEAU PROJET
# ─────────────────────────────────────────

from rest_framework import status as drf_status


class NouveauProjetView(APIView):
    """
    POST /api/budget/nouveau-projet/
    
    Crée la première version d'un projet (sans historique)
    Tous les champs de réalisation sont NULL
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsResponsableStructure]

    @staticmethod
    def _to_float_or_none(val):
        if val in (None, '', 'null', 'None'):
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_sum(values):
        filtered = [v for v in values if v is not None]
        return round(sum(filtered), 2) if filtered else None

    def post(self, request):
        data = request.data
        
        # 1. Informations depuis le token
        region_id = getattr(request.user, 'region_id', None)
        structure_id = getattr(request.user, 'structure_id', None)
        created_by = request.user.id

        if not region_id or not structure_id:
            return Response({'error': 'region_id ou structure_id manquant'}, status=400)

        # 2. Champs obligatoires
        activite = data.get('activite')
        perimetre_code = data.get('perimetre')
        famille_code = data.get('famille')
        code_division = data.get('code_division')
        libelle = data.get('libelle')

        missing = [f for f, v in {
            'activite': activite, 'perimetre': perimetre_code,
            'famille': famille_code, 'code_division': code_division, 'libelle': libelle
        }.items() if not v]

        if missing:
            return Response({'error': f"Champs manquants: {', '.join(missing)}"}, status=400)

        # 3. Vérifier que le code_division n'existe pas déjà
        if BudgetRecord.objects.filter(code_division=code_division).exists():
            return Response({
                'error': f"Le code_division '{code_division}' existe déjà. Utilisez l'API de modification."
            }, status=400)

        # 4. Intervalle PMT
        intervalle_pmt = data.get('intervalle_pmt')
        if intervalle_pmt and isinstance(intervalle_pmt, list) and len(intervalle_pmt) == 2:
            annee_debut_pmt = int(intervalle_pmt[0])
            annee_fin_pmt = int(intervalle_pmt[1])
        else:
            annee_debut_pmt = data.get('annee_debut_pmt')
            annee_fin_pmt = data.get('annee_fin_pmt')

        # 5. Résolution région via service param
        service_url = get_service_param_url()
        token = request.headers.get('Authorization', '')

        try:
            region_resp = requests.get(
                f"{service_url}/params/regions/id/{region_id}",
                headers={'Authorization': token},
                timeout=5
            )
            if region_resp.status_code != 200:
                return Response({'error': 'Erreur région'}, status=400)
            region_data = region_resp.json().get('data', {})
            code_region = region_data.get('code_region')
        except Exception as e:
            return Response({'error': f'Erreur service région: {e}'}, status=503)

        # 6. Lecture des champs financiers
        PREVISIONS_KEYS = ['prev_n_plus2', 'prev_n_plus3', 'prev_n_plus4', 'prev_n_plus5']
        MOIS_KEYS = ['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin',
                     'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre']

        v = {}
        for key in PREVISIONS_KEYS:
            v[f'{key}_total'] = self._to_float_or_none(data.get(f'{key}_total'))
            v[f'{key}_dont_dex'] = self._to_float_or_none(data.get(f'{key}_dont_dex'))
        for mois in MOIS_KEYS:
            v[f'{mois}_total'] = self._to_float_or_none(data.get(f'{mois}_total'))
            v[f'{mois}_dont_dex'] = self._to_float_or_none(data.get(f'{mois}_dont_dex'))

        # 7. Calculs pour nouveau projet
        prev_n_plus1_total = self._safe_sum([v[f'{m}_total'] for m in MOIS_KEYS])
        prev_n_plus1_dex = self._safe_sum([v[f'{m}_dont_dex'] for m in MOIS_KEYS])
        rar_total = self._safe_sum([v[f'{k}_total'] for k in PREVISIONS_KEYS])
        rar_dex = self._safe_sum([v[f'{k}_dont_dex'] for k in PREVISIONS_KEYS])
        cout_total = self._safe_sum([prev_n_plus1_total, rar_total])
        cout_dex = self._safe_sum([prev_n_plus1_dex, rar_dex])

        # 8. Création
        upload = ExcelUpload.objects.create(
            file_name=f"nouveau_projet_{code_division}",
            status='processed'
        )

        record = BudgetRecord.objects.create(
            upload=upload,
            activite=activite,
            region=code_region,
            perm=perimetre_code,
            famille=famille_code,
            code_division=code_division,
            libelle=libelle,
            annee_debut_pmt=annee_debut_pmt,
            annee_fin_pmt=annee_fin_pmt,
            region_id=region_id,
            structure_id=structure_id,
            created_by=created_by,
            type_projet='nouveau',
            description_technique=data.get('description_technique'),
            opportunite_projet=data.get('opportunite_projet'),
            
            # Versionnement
            parent_id=None,
            version=1,
            is_active=True,
            version_comment="Création initiale",
            
            # Champs de réalisation (NULL pour nouveau projet)
            realisation_cumul_n_mins1_total=None,
            realisation_cumul_n_mins1_dont_dex=None,
            real_s1_n_total=None,
            real_s1_n_dont_dex=None,
            prev_s2_n_total=None,
            prev_s2_n_dont_dex=None,
            prev_cloture_n_total=None,
            prev_cloture_n_dont_dex=None,
            
            # Champs calculés
            prev_n_plus1_total=prev_n_plus1_total,
            prev_n_plus1_dont_dex=prev_n_plus1_dex,
            reste_a_realiser_total=rar_total,
            reste_a_realiser_dont_dex=rar_dex,
            cout_initial_total=cout_total,
            cout_initial_dont_dex=cout_dex,
            
            # Prévisions
            **{k: v[k] for k in [f'{key}_total' for key in PREVISIONS_KEYS] + 
               [f'{key}_dont_dex' for key in PREVISIONS_KEYS] +
               [f'{mois}_total' for mois in MOIS_KEYS] +
               [f'{mois}_dont_dex' for mois in MOIS_KEYS]}
        )

        serializer = BudgetRecordSerializer(record)
        return Response({
            'success': True,
            'message': 'Projet créé avec succès (version 1)',
            'data': serializer.data
        }, status=201)

        
from decimal import Decimal










from django.db import transaction
from django.db.models import Max
from django.core.cache import cache
from decimal import Decimal
import time
from rest_framework.views import APIView
from rest_framework.response import Response


class ModifierProjetView(APIView):
    """
    POST /api/budget/modifier-projet/{code_division}/
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAgent]

    PREVISIONS_KEYS = [
        'prev_n_plus2', 'prev_n_plus3', 'prev_n_plus4', 'prev_n_plus5'
    ]
    MOIS_KEYS = [
        'janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre',
    ]

    LOCK_TIMEOUT  = 10   # secondes max que le verrou est tenu
    LOCK_WAIT     = 8    # secondes max à attendre pour obtenir le verrou
    LOCK_INTERVAL = 0.1  # intervalle de polling

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _to_decimal_or_none(val):
        if val in (None, '', 'null', 'None'):
            return None
        try:
            return Decimal(str(val))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_sum(values):
        filtered = [v for v in values if v is not None]
        if not filtered:
            return None
        return sum(
            v if isinstance(v, Decimal) else Decimal(str(v))
            for v in filtered
        )

    def _is_admin(self, request):
        return getattr(request.user, 'role', '') in ('admin', 'superadmin')

    @staticmethod
    def _all_financial_keys(previsions_keys, mois_keys):
        keys = []
        for k in previsions_keys:
            keys += [f'{k}_total', f'{k}_dont_dex']
        for m in mois_keys:
            keys += [f'{m}_total', f'{m}_dont_dex']
        return keys

    def _parse_financial_fields(self, data, previsions_keys, mois_keys):
        v = {}
        for k in previsions_keys:
            v[f'{k}_total']    = self._to_decimal_or_none(data.get(f'{k}_total'))
            v[f'{k}_dont_dex'] = self._to_decimal_or_none(data.get(f'{k}_dont_dex'))
        for m in mois_keys:
            v[f'{m}_total']    = self._to_decimal_or_none(data.get(f'{m}_total'))
            v[f'{m}_dont_dex'] = self._to_decimal_or_none(data.get(f'{m}_dont_dex'))
        return v

    def _acquire_lock(self, code_division):
        """
        Tente d'acquérir un verrou sur code_division.
        Retourne True si obtenu, False si timeout.
        """
        lock_key     = f'budget_lock_{code_division}'
        deadline     = time.time() + self.LOCK_WAIT

        while time.time() < deadline:
            # add() est atomique : échoue si la clé existe déjà
            acquired = cache.add(lock_key, '1', timeout=self.LOCK_TIMEOUT)
            if acquired:
                return True
            time.sleep(self.LOCK_INTERVAL)

        return False

    def _release_lock(self, code_division):
        cache.delete(f'budget_lock_{code_division}')

    # ------------------------------------------------------------------ #
    # Point d'entrée principal
    # ------------------------------------------------------------------ #
    def post(self, request, code_division):
        data     = request.data
        is_admin = self._is_admin(request)

        projet_exists = BudgetRecord.objects.filter(
            code_division=code_division
        ).exists()

        if not projet_exists:
            return self._create_first_version(request, code_division)

        # ── Acquérir le verrou applicatif ────────────────────────────────
        if not self._acquire_lock(code_division):
            return Response(
                {
                    'error': (
                        'Une modification est déjà en cours sur ce projet. '
                        'Veuillez réessayer dans quelques secondes.'
                    )
                },
                status=409
            )

        try:
            return self._do_modification(
                request, data, code_division, is_admin
            )
        finally:
            # Toujours libérer le verrou, même en cas d'exception
            self._release_lock(code_division)

    # ------------------------------------------------------------------ #
    # Logique de modification
    # ------------------------------------------------------------------ #
    def _do_modification(self, request, data, code_division, is_admin):
        with transaction.atomic():

            old_version = (
                BudgetRecord.objects.filter(
                    code_division=code_division, is_active=True
                ).first()
                or BudgetRecord.objects.filter(
                    code_division=code_division
                ).order_by('-version').first()
            )

            if not old_version:
                return Response(
                    {'error': f'Projet {code_division} non trouvé'},
                    status=404
                )

            # ── Champs interdits ────────────────────────────────────────
            if not is_admin:
                forbidden = [
                    field
                    for field, attr, key in [
                        ('region',    'region',   'region'),
                        ('perimetre', 'perm',     'perimetre'),
                        ('famille',   'famille',  'famille'),
                        ('activite',  'activite', 'activite'),
                    ]
                    if key in data
                    and data[key] != getattr(old_version, attr)
                ]
                if forbidden:
                    return Response(
                        {
                            'error': (
                                f"Modification interdite : "
                                f"{', '.join(forbidden)}"
                            )
                        },
                        status=403
                    )

            # ── Code final ──────────────────────────────────────────────
            new_code_division = data.get('code_division', code_division)

            # ── Numéro de version — calculé sous verrou applicatif ──────
            # Le verrou cache garantit qu'une seule requête à la fois
            # arrive ici pour ce code_division.
            result = BudgetRecord.objects.filter(
                code_division=new_code_division
            ).aggregate(max_version=Max('version'))

            new_version_number = (result['max_version'] or 0) + 1

            # ── Désactiver l'ancienne version ───────────────────────────
            if old_version.is_active:
                old_version.is_active = False
                old_version.save(update_fields=['is_active'])

            # ── Créer la nouvelle version ───────────────────────────────
            new_version = self._create_new_version(
                old_version, data, request,
                new_code_division, new_version_number
            )

        serializer = BudgetRecordSerializer(new_version)
        return Response(
            {
                'success':          True,
                'message':          (
                    f'Projet modifié — '
                    f'Version {old_version.version} '
                    f'→ {new_version_number}'
                ),
                'ancienne_version': old_version.version,
                'nouvelle_version': new_version_number,
                'data':             serializer.data,
            },
            status=201,
        )

    # ------------------------------------------------------------------ #
    # Création version 1
    # ------------------------------------------------------------------ #
    def _create_first_version(self, request, code_division):
        data       = request.data
        final_code = data.get('code_division', code_division)

        if BudgetRecord.objects.filter(code_division=final_code).exists():
            return Response(
                {'error': f'Le projet {final_code} existe déjà.'},
                status=400,
            )

        v = self._parse_financial_fields(
            data, self.PREVISIONS_KEYS, self.MOIS_KEYS
        )

        prev_n_plus1_total = self._safe_sum(
            [v[f'{m}_total']    for m in self.MOIS_KEYS]
        )
        prev_n_plus1_dex   = self._safe_sum(
            [v[f'{m}_dont_dex'] for m in self.MOIS_KEYS]
        )
        rar_total  = self._safe_sum(
            [v[f'{k}_total']    for k in self.PREVISIONS_KEYS]
        )
        rar_dex    = self._safe_sum(
            [v[f'{k}_dont_dex'] for k in self.PREVISIONS_KEYS]
        )
        cout_total = self._safe_sum([prev_n_plus1_total, rar_total])
        cout_dex   = self._safe_sum([prev_n_plus1_dex,   rar_dex])

        upload = ExcelUpload.objects.create(
            file_name=f'projet_{final_code}_v1',
            status='processed'
        )

        record = BudgetRecord.objects.create(
            upload=upload,
            activite=data.get('activite'),
            region=data.get('region'),
            perm=data.get('perimetre'),
            famille=data.get('famille'),
            code_division=final_code,
            libelle=data.get('libelle'),
            annee_debut_pmt=data.get('annee_debut_pmt'),
            annee_fin_pmt=data.get('annee_fin_pmt'),
            region_id=getattr(request.user, 'region_id', None),
            structure_id=getattr(request.user, 'structure_id', None),
            created_by=request.user.id,
            type_projet=data.get('type_projet', 'nouveau'),
            description_technique=data.get('description_technique'),
            opportunite_projet=data.get('opportunite_projet'),
            parent_id=None,
            version=1,
            is_active=True,
            version_comment=data.get('version_comment', 'Création initiale'),
            realisation_cumul_n_mins1_total=None,
            realisation_cumul_n_mins1_dont_dex=None,
            real_s1_n_total=None,
            real_s1_n_dont_dex=None,
            prev_s2_n_total=None,
            prev_s2_n_dont_dex=None,
            prev_cloture_n_total=None,
            prev_cloture_n_dont_dex=None,
            prev_n_plus1_total=prev_n_plus1_total,
            prev_n_plus1_dont_dex=prev_n_plus1_dex,
            reste_a_realiser_total=rar_total,
            reste_a_realiser_dont_dex=rar_dex,
            cout_initial_total=cout_total,
            cout_initial_dont_dex=cout_dex,
            **{
                k: v[k]
                for k in self._all_financial_keys(
                    self.PREVISIONS_KEYS, self.MOIS_KEYS
                )
            },
        )

        return Response(
            {
                'success': True,
                'message': 'Projet créé (version 1)',
                'data':    BudgetRecordSerializer(record).data,
            },
            status=201,
        )

    # ------------------------------------------------------------------ #
    # Création d'une nouvelle version
    # ------------------------------------------------------------------ #
    def _create_new_version(
        self, old_version, new_data, request,
        new_code_division, new_version_number
    ):
        v = {}
        for key in self.PREVISIONS_KEYS:
            for suffix in ('_total', '_dont_dex'):
                k    = f'{key}{suffix}'
                v[k] = (
                    self._to_decimal_or_none(new_data.get(k))
                    or getattr(old_version, k)
                )
        for mois in self.MOIS_KEYS:
            for suffix in ('_total', '_dont_dex'):
                k    = f'{mois}{suffix}'
                v[k] = (
                    self._to_decimal_or_none(new_data.get(k))
                    or getattr(old_version, k)
                )

        def nd(key):
            raw = self._to_decimal_or_none(new_data.get(key))
            return raw if raw is not None else getattr(old_version, key)

        real_cumul_total = nd('realisation_cumul_n_mins1_total')
        real_cumul_dex   = nd('realisation_cumul_n_mins1_dont_dex')
        real_s1_total    = nd('real_s1_n_total')
        real_s1_dex      = nd('real_s1_n_dont_dex')
        prev_s2_total    = nd('prev_s2_n_total')
        prev_s2_dex      = nd('prev_s2_n_dont_dex')

        prev_n_plus1_total = self._safe_sum(
            [v[f'{m}_total']    for m in self.MOIS_KEYS]
        )
        prev_n_plus1_dex   = self._safe_sum(
            [v[f'{m}_dont_dex'] for m in self.MOIS_KEYS]
        )
        rar_total = self._safe_sum(
            [v[f'{k}_total']    for k in self.PREVISIONS_KEYS]
        )
        rar_dex   = self._safe_sum(
            [v[f'{k}_dont_dex'] for k in self.PREVISIONS_KEYS]
        )

        projet_type = new_data.get('type_projet', old_version.type_projet)

        if projet_type == 'en_cours' and (
            real_s1_total is not None or prev_s2_total is not None
        ):
            prev_cloture_total = self._safe_sum([real_s1_total, prev_s2_total])
            prev_cloture_dex   = self._safe_sum([real_s1_dex,   prev_s2_dex])
            cout_total = self._safe_sum([
                real_cumul_total, prev_cloture_total,
                prev_n_plus1_total, rar_total
            ])
            cout_dex = self._safe_sum([
                real_cumul_dex, prev_cloture_dex,
                prev_n_plus1_dex, rar_dex
            ])
        else:
            prev_cloture_total = None
            prev_cloture_dex   = None
            cout_total = self._safe_sum([prev_n_plus1_total, rar_total])
            cout_dex   = self._safe_sum([prev_n_plus1_dex,   rar_dex])

        parent_id = old_version.parent_id or old_version.id

        upload = ExcelUpload.objects.create(
            file_name=f'projet_{new_code_division}_v{new_version_number}',
            status='processed',
        )

        return BudgetRecord.objects.create(
            upload=upload,
            activite=new_data.get('activite', old_version.activite),
            region=new_data.get('region', old_version.region),
            perm=new_data.get('perimetre', old_version.perm),
            famille=new_data.get('famille', old_version.famille),
            code_division=new_code_division,
            libelle=new_data.get('libelle', old_version.libelle),
            annee_debut_pmt=new_data.get(
                'annee_debut_pmt', old_version.annee_debut_pmt
            ),
            annee_fin_pmt=new_data.get(
                'annee_fin_pmt', old_version.annee_fin_pmt
            ),
            region_id=getattr(request.user, 'region_id', None),
            structure_id=getattr(request.user, 'structure_id', None),
            created_by=request.user.id,
            type_projet=projet_type,
            description_technique=new_data.get(
                'description_technique', old_version.description_technique
            ),
            opportunite_projet=new_data.get(
                'opportunite_projet', old_version.opportunite_projet
            ),
            parent_id=parent_id,
            version=new_version_number,
            is_active=True,
            version_comment=new_data.get(
                'version_comment', f'Version {new_version_number}'
            ),
            realisation_cumul_n_mins1_total=real_cumul_total,
            realisation_cumul_n_mins1_dont_dex=real_cumul_dex,
            real_s1_n_total=real_s1_total,
            real_s1_n_dont_dex=real_s1_dex,
            prev_s2_n_total=prev_s2_total,
            prev_s2_n_dont_dex=prev_s2_dex,
            prev_cloture_n_total=prev_cloture_total,
            prev_cloture_n_dont_dex=prev_cloture_dex,
            prev_n_plus1_total=prev_n_plus1_total,
            prev_n_plus1_dont_dex=prev_n_plus1_dex,
            reste_a_realiser_total=rar_total,
            reste_a_realiser_dont_dex=rar_dex,
            cout_initial_total=cout_total,
            cout_initial_dont_dex=cout_dex,
            **{
                k: v[k]
                for k in self._all_financial_keys(
                    self.PREVISIONS_KEYS, self.MOIS_KEYS
                )
            },
        )
class HistoriqueProjetView(APIView):
    """
    GET /api/budget/historique/{code_division}/        → tout l'historique
    GET /api/budget/historique/{code_division}/actif/  → version active uniquement
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsUser]

    def get(self, request, code_division, mode=None):

        qs = BudgetRecord.objects.filter(
            code_division=code_division
        ).order_by('-version')

        if not qs.exists():
            return Response(
                {'error': f'Projet {code_division} introuvable.'},
                status=404
            )

        # ── /actif/ → version active uniquement ─────────────────────────
        if mode == 'actif':
            actif = qs.filter(is_active=True).first() or qs.first()
            return Response({
                'code_division': code_division,
                'version_active': BudgetRecordSerializer(actif).data,
            })

        # ── Historique complet ───────────────────────────────────────────
        total     = qs.count()
        actif     = qs.filter(is_active=True).first() or qs.first()
        derniere  = qs.first()          # version la plus haute (ordering=-version)
        premiere  = qs.last()           # version 1

        return Response({
            'code_division':    code_division,
            'total_versions':   total,
            'version_active':   actif.version,
            'derniere_version': derniere.version,
            'premiere_version': premiere.version,
            'historique': BudgetRecordSerializer(qs, many=True).data,
        })

# ─────────────────────────────────────────
# HELPER — récupérer record par id
# ─────────────────────────────────────────

def get_record_or_404(record_id):
    try:
        return BudgetRecord.objects.get(id=record_id)
    except BudgetRecord.DoesNotExist:
        return None


# ─────────────────────────────────────────
# WORKFLOW DE VALIDATION
# ─────────────────────────────────────────

# class SoumettreProjetView(APIView):
#     """
#     POST /recap/budget/soumettre/<id>/
#     Responsable structure soumet le projet pour validation
#     Condition : statut = brouillon
#     """
#     authentication_classes = [RemoteJWTAuthentication]
#     permission_classes = [IsResponsableStructure]

#     def post(self, request, record_id):
#         record = get_record_or_404(record_id)
#         if not record:
#             return Response({'error': 'Projet introuvable'}, status=404)

#         if record.statut != 'brouillon':
#             return Response({
#                 'error': f"Impossible de soumettre — statut actuel : '{record.statut}'"
#             }, status=400)

#         record.statut = 'soumis'
#         record.save()

#         return Response({
#             'success': True,
#             'message': 'Projet soumis pour validation',
#             'statut': record.statut
#         })


# class ValiderDirecteurRegionView(APIView):
#     """
#     POST /recap/budget/valider/directeur-region/<id>/
#     Condition : statut = soumis
#     """
#     authentication_classes = [RemoteJWTAuthentication]
#     permission_classes = [IsDirecteurRegion]

#     def post(self, request, record_id):
#         record = get_record_or_404(record_id)
#         if not record:
#             return Response({'error': 'Projet introuvable'}, status=404)

#         action      = request.data.get('action')
#         commentaire = request.data.get('commentaire', '')

#         if action not in ['valider', 'rejeter']:
#             return Response({'error': "action doit être 'valider' ou 'rejeter'"}, status=400)

#         if record.statut != 'soumis':
#             return Response({
#                 'error': f"Le projet doit être 'soumis' — statut actuel : '{record.statut}'"
#             }, status=400)

#         if action == 'valider':
#             record.statut                            = 'valide_directeur_region'
#             record.valide_par_directeur_region       = request.user.nom_complet
#             record.date_validation_directeur_region  = timezone.now()
#             record.commentaire_directeur_region      = commentaire
#             message = 'Projet validé par le directeur région'
#         else:
#             record.statut       = 'rejete'
#             record.rejete_par   = request.user.nom_complet
#             record.date_rejet   = timezone.now()
#             record.motif_rejet  = commentaire
#             message = 'Projet rejeté par le directeur région'

#         record.save()

#         return Response({'success': True, 'message': message, 'statut': record.statut})


# class ValiderChefView(APIView):
#     """
#     POST /recap/budget/valider/chef/<id>/
#     Condition : statut = valide_directeur_region
#     """
#     authentication_classes = [RemoteJWTAuthentication]
#     permission_classes = [IsChef]

#     def post(self, request, record_id):
#         record = get_record_or_404(record_id)
#         if not record:
#             return Response({'error': 'Projet introuvable'}, status=404)

#         action      = request.data.get('action')
#         commentaire = request.data.get('commentaire', '')

#         if action not in ['valider', 'rejeter']:
#             return Response({'error': "action doit être 'valider' ou 'rejeter'"}, status=400)

#         if record.statut != 'valide_directeur_region':
#             return Response({
#                 'error': f"Le projet doit être 'valide_directeur_region' — statut actuel : '{record.statut}'"
#             }, status=400)

#         if action == 'valider':
#             record.statut               = 'valide_chef'
#             record.valide_par_chef      = request.user.nom_complet
#             record.date_validation_chef = timezone.now()
#             record.commentaire_chef     = commentaire
#             message = 'Projet validé par le chef'
#         else:
#             record.statut      = 'rejete'
#             record.rejete_par  = request.user.nom_complet
#             record.date_rejet  = timezone.now()
#             record.motif_rejet = commentaire
#             message = 'Projet rejeté par le chef'

#         record.save()

#         return Response({'success': True, 'message': message, 'statut': record.statut})


# class ValiderDirecteurView(APIView):
#     """
#     POST /recap/budget/valider/directeur/<id>/
#     Condition : statut = valide_chef
#     """
#     authentication_classes = [RemoteJWTAuthentication]
#     permission_classes = [IsDirecteur]

#     def post(self, request, record_id):
#         record = get_record_or_404(record_id)
#         if not record:
#             return Response({'error': 'Projet introuvable'}, status=404)

#         action      = request.data.get('action')
#         commentaire = request.data.get('commentaire', '')

#         if action not in ['valider', 'rejeter']:
#             return Response({'error': "action doit être 'valider' ou 'rejeter'"}, status=400)

#         if record.statut != 'valide_chef':
#             return Response({
#                 'error': f"Le projet doit être 'valide_chef' — statut actuel : '{record.statut}'"
#             }, status=400)

#         if action == 'valider':
#             record.statut                    = 'valide_directeur'
#             record.valide_par_directeur      = request.user.nom_complet
#             record.date_validation_directeur = timezone.now()
#             record.commentaire_directeur     = commentaire
#             message = 'Projet validé par le directeur'
#         else:
#             record.statut      = 'rejete'
#             record.rejete_par  = request.user.nom_complet
#             record.date_rejet  = timezone.now()
#             record.motif_rejet = commentaire
#             message = 'Projet rejeté par le directeur'

#         record.save()

#         return Response({'success': True, 'message': message, 'statut': record.statut})


# class ValiderDivisionnnaireView(APIView):
#     """
#     POST /recap/budget/valider/divisionnaire/<id>/
#     Condition : statut = valide_directeur
#     """
#     authentication_classes = [RemoteJWTAuthentication]
#     permission_classes = [IsDivisionnaire]

#     def post(self, request, record_id):
#         record = get_record_or_404(record_id)
#         if not record:
#             return Response({'error': 'Projet introuvable'}, status=404)

#         action      = request.data.get('action')
#         commentaire = request.data.get('commentaire', '')

#         if action not in ['valider', 'rejeter']:
#             return Response({'error': "action doit être 'valider' ou 'rejeter'"}, status=400)

#         if record.statut != 'valide_directeur':
#             return Response({
#                 'error': f"Le projet doit être 'valide_directeur' — statut actuel : '{record.statut}'"
#             }, status=400)

#         if action == 'valider':
#             record.statut                        = 'valide_divisionnaire'
#             record.valide_par_divisionnaire      = request.user.nom_complet
#             record.date_validation_divisionnaire = timezone.now()
#             record.commentaire_divisionnaire     = commentaire
#             message = 'Projet validé par le divisionnaire — validation complète ✅'
#         else:
#             record.statut      = 'rejete'
#             record.rejete_par  = request.user.nom_complet
#             record.date_rejet  = timezone.now()
#             record.motif_rejet = commentaire
#             message = 'Projet rejeté par le divisionnaire'

#         record.save()

#         return Response({'success': True, 'message': message, 'statut': record.statut})



from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response


def get_record_or_404(record_id):
    try:
        return BudgetRecord.objects.get(id=record_id)
    except BudgetRecord.DoesNotExist:
        return None


# ================================================================== #
#  1. SOUMETTRE  (ResponsableStructure)
# ================================================================== #
class SoumettreProjetView(APIView):
    """
    POST /recap/budget/soumettre/<id>/
    Condition : statut = brouillon
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsResponsableStructure]

    def post(self, request, record_id):
        record = get_record_or_404(record_id)
        if not record:
            return Response({'error': 'Projet introuvable'}, status=404)

        if record.statut != 'brouillon':
            return Response({
                'error': f"Impossible de soumettre — statut actuel : '{record.statut}'"
            }, status=400)

        record.statut = 'soumis'
        record.save(update_fields=['statut'])

        return Response({
            'success': True,
            'message': 'Projet soumis pour validation',
            'statut':  record.statut,
        })


# ================================================================== #
#  2. DIRECTEUR RÉGION  (valider / rejeter)
# ================================================================== #
class ValiderDirecteurRegionView(APIView):
    """
    POST /recap/budget/valider/directeur-region/<id>/
    Condition : statut = soumis
                OU reserve_agent / reserve_chef / reserve_directeur
                   (retour de réserve vers DR)
    Actions   : valider | rejeter
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsDirecteurRegion]

    STATUTS_AUTORISÉS = {
        'soumis',
        'reserve_agent',
        'reserve_chef',
        'reserve_directeur',
    }

    def post(self, request, record_id):
        record = get_record_or_404(record_id)
        if not record:
            return Response({'error': 'Projet introuvable'}, status=404)

        action      = request.data.get('action')
        commentaire = request.data.get('commentaire', '')

        if action not in ('valider', 'rejeter'):
            return Response(
                {'error': "action doit être 'valider' ou 'rejeter'"},
                status=400
            )

        if record.statut not in self.STATUTS_AUTORISÉS:
            return Response({
                'error': (
                    f"Statut '{record.statut}' non autorisé pour cette action. "
                    f"Statuts acceptés : {', '.join(self.STATUTS_AUTORISÉS)}"
                )
            }, status=400)

        if action == 'valider':
            record.statut                           = 'valide_directeur_region'
            record.valide_par_directeur_region      = request.user.nom_complet
            record.date_validation_directeur_region = timezone.now()
            record.commentaire_directeur_region     = commentaire
            message = 'Projet validé par le directeur région'
        else:
            record.statut      = 'rejete'
            record.rejete_par  = request.user.nom_complet
            record.date_rejet  = timezone.now()
            record.motif_rejet = commentaire
            message = 'Projet rejeté par le directeur région'

        record.save()
        return Response({
            'success': True,
            'message': message,
            'statut':  record.statut,
        })


# ================================================================== #
#  3. AGENT  (valider / réserver)
#     Voit : valide_directeur_region
#     Ne peut PAS rejeter
# ================================================================== #
class ValiderAgentView(APIView):
    """
    POST /recap/budget/valider/agent/<id>/
    Condition : statut = valide_directeur_region
    Actions   : valider | reserver (avec commentaire obligatoire)
    Réserver  → retourne au DR (statut = reserve_agent)
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsAgent]

    def post(self, request, record_id):
        record = get_record_or_404(record_id)
        if not record:
            return Response({'error': 'Projet introuvable'}, status=404)

        action      = request.data.get('action')
        commentaire = request.data.get('commentaire', '')

        if action not in ('valider', 'reserver'):
            return Response(
                {'error': "action doit être 'valider' ou 'reserver'"},
                status=400
            )

        if record.statut != 'valide_directeur_region':
            return Response({
                'error': (
                    f"Le projet doit être 'valide_directeur_region' "
                    f"— statut actuel : '{record.statut}'"
                )
            }, status=400)

        if action == 'reserver' and not commentaire:
            return Response(
                {'error': "Un commentaire est obligatoire pour réserver."},
                status=400
            )

        if action == 'valider':
            record.statut = 'valide_agent'
            message       = 'Projet validé par l\'agent'
        else:
            # Réserver → retourne au DR avec commentaire
            record.statut                           = 'reserve_agent'
            record.commentaire_directeur_region     = (
                f"[Réservé par agent] {commentaire}"
            )
            message = 'Projet réservé — retourné au directeur région'

        record.save()
        return Response({
            'success': True,
            'message': message,
            'statut':  record.statut,
        })


# ================================================================== #
#  4. CHEF  (valider / réserver)
#     Voit : valide_agent + reserve_agent
#     Ne peut PAS rejeter
# ================================================================== #
class ValiderChefView(APIView):
    """
    POST /recap/budget/valider/chef/<id>/
    Condition : statut = valide_agent OU reserve_agent
    Actions   : valider | reserver (avec commentaire obligatoire)
    Réserver  → retourne au DR (statut = reserve_chef)
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsChef]

    STATUTS_AUTORISÉS = {'valide_agent', 'reserve_agent'}

    def post(self, request, record_id):
        record = get_record_or_404(record_id)
        if not record:
            return Response({'error': 'Projet introuvable'}, status=404)

        action      = request.data.get('action')
        commentaire = request.data.get('commentaire', '')

        if action not in ('valider', 'reserver'):
            return Response(
                {'error': "action doit être 'valider' ou 'reserver'"},
                status=400
            )

        if record.statut not in self.STATUTS_AUTORISÉS:
            return Response({
                'error': (
                    f"Statut '{record.statut}' non autorisé. "
                    f"Acceptés : {', '.join(self.STATUTS_AUTORISÉS)}"
                )
            }, status=400)

        if action == 'reserver' and not commentaire:
            return Response(
                {'error': "Un commentaire est obligatoire pour réserver."},
                status=400
            )

        if action == 'valider':
            record.statut               = 'valide_chef'
            record.valide_par_chef      = request.user.nom_complet
            record.date_validation_chef = timezone.now()
            record.commentaire_chef     = commentaire
            message = 'Projet validé par le chef'
        else:
            record.statut           = 'reserve_chef'
            record.commentaire_chef = f"[Réservé par chef] {commentaire}"
            message = 'Projet réservé — retourné au directeur région'

        record.save()
        return Response({
            'success': True,
            'message': message,
            'statut':  record.statut,
        })



# ================================================================== #
#  5. DIRECTEUR  (valider / réserver)
#     Condition : valide_chef
#     Ne peut PAS rejeter
# ================================================================== #
class ValiderDirecteurView(APIView):
    """
    POST /recap/budget/valider/directeur/<id>/
    Condition : statut = valide_chef
    Actions   : valider | reserver (avec commentaire obligatoire)
    Réserver  → retourne au DR (statut = reserve_directeur)
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsDirecteur]

    def post(self, request, record_id):
        record = get_record_or_404(record_id)
        if not record:
            return Response({'error': 'Projet introuvable'}, status=404)

        action      = request.data.get('action')
        commentaire = request.data.get('commentaire', '')

        if action not in ('valider', 'reserver'):
            return Response(
                {'error': "action doit être 'valider' ou 'reserver'"},
                status=400
            )

        if record.statut != 'valide_chef':
            return Response({
                'error': (
                    f"Le projet doit être 'valide_chef' "
                    f"— statut actuel : '{record.statut}'"
                )
            }, status=400)

        if action == 'reserver' and not commentaire:
            return Response(
                {'error': "Un commentaire est obligatoire pour réserver."},
                status=400
            )

        if action == 'valider':
            record.statut                    = 'valide_directeur'
            record.valide_par_directeur      = request.user.nom_complet
            record.date_validation_directeur = timezone.now()
            record.commentaire_directeur     = commentaire
            message = 'Projet validé par le directeur'
        else:
            record.statut                = 'reserve_directeur'
            record.commentaire_directeur = f"[Réservé par directeur] {commentaire}"
            message = 'Projet réservé — retourné au directeur région'

        record.save()
        return Response({
            'success': True,
            'message': message,
            'statut':  record.statut,
        })


# ================================================================== #
#  6. DIVISIONNAIRE  (valider / rejeter)
#     Condition : valide_directeur
#     Seul à pouvoir rejeter après le DR
# ================================================================== #
class ValiderDivisionnnaireView(APIView):
    """
    POST /recap/budget/valider/divisionnaire/<id>/
    Condition : statut = valide_directeur
    Actions   : valider | rejeter
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsDivisionnaire]

    def post(self, request, record_id):
        record = get_record_or_404(record_id)
        if not record:
            return Response({'error': 'Projet introuvable'}, status=404)

        action      = request.data.get('action')
        commentaire = request.data.get('commentaire', '')

        if action not in ('valider', 'rejeter'):
            return Response(
                {'error': "action doit être 'valider' ou 'rejeter'"},
                status=400
            )

        if record.statut != 'valide_directeur':
            return Response({
                'error': (
                    f"Le projet doit être 'valide_directeur' "
                    f"— statut actuel : '{record.statut}'"
                )
            }, status=400)

        if action == 'valider':
            record.statut                        = 'valide_divisionnaire'
            record.valide_par_divisionnaire      = request.user.nom_complet
            record.date_validation_divisionnaire = timezone.now()
            record.commentaire_divisionnaire     = commentaire
            message = 'Projet validé par le divisionnaire — validation complète ✅'
        else:
            record.statut      = 'rejete'
            record.rejete_par  = request.user.nom_complet
            record.date_rejet  = timezone.now()
            record.motif_rejet = commentaire
            message = 'Projet rejeté par le divisionnaire'

        record.save()
        return Response({
            'success': True,
            'message': message,
            'statut':  record.statut,
        })
# ─────────────────────────────────────────
# STATUT COMPLET DU WORKFLOW
# ─────────────────────────────────────────

class StatutValidationView(APIView):
    """
    GET /recap/budget/statut/<record_id>/
    Retourne le statut complet du workflow de validation
    Accessible par tous les rôles
    """
    authentication_classes = [RemoteJWTAuthentication]
    # permission_classes = [IsAgent]

    def get(self, request, record_id):
        record = get_record_or_404(record_id)
        if not record:
            return Response({'error': 'Projet introuvable'}, status=404)

        WORKFLOW = [
            'brouillon',
            'soumis',
            'valide_directeur_region',
            'valide_chef',
            'valide_directeur',
            'valide_divisionnaire',
        ]

        statut_actuel = record.statut
        est_rejete    = statut_actuel == 'rejete'

        if est_rejete:
            progression = 0
        else:
            try:
                etape_actuelle = WORKFLOW.index(statut_actuel)
                progression    = round((etape_actuelle / (len(WORKFLOW) - 1)) * 100)
            except ValueError:
                progression = 0

        etapes = [
            {
                'etape': 0, 'label': 'Création', 'role': 'responsable_structure',
                'statut_cible': 'brouillon', 'fait': True,
                'date': None, 'par': None, 'commentaire': None,
            },
            {
                'etape': 1, 'label': 'Soumission', 'role': 'responsable_structure',
                'statut_cible': 'soumis',
                'fait': statut_actuel in (
                    'soumis', 'valide_directeur_region', 'valide_chef',
                    'valide_directeur', 'valide_divisionnaire'
                ),
                'date': None, 'par': None, 'commentaire': None,
            },
            {
                'etape': 2, 'label': 'Validation Directeur Région', 'role': 'directeur_region',
                'statut_cible': 'valide_directeur_region',
                'fait': statut_actuel in (
                    'valide_directeur_region', 'valide_chef',
                    'valide_directeur', 'valide_divisionnaire'
                ),
                'date':        record.date_validation_directeur_region,
                'par':         record.valide_par_directeur_region,
                'commentaire': record.commentaire_directeur_region,
            },
            {
                'etape': 3, 'label': 'Validation Chef', 'role': 'chef',
                'statut_cible': 'valide_chef',
                'fait': statut_actuel in ('valide_chef', 'valide_directeur', 'valide_divisionnaire'),
                'date':        record.date_validation_chef,
                'par':         record.valide_par_chef,
                'commentaire': record.commentaire_chef,
            },
            {
                'etape': 4, 'label': 'Validation Directeur', 'role': 'directeur',
                'statut_cible': 'valide_directeur',
                'fait': statut_actuel in ('valide_directeur', 'valide_divisionnaire'),
                'date':        record.date_validation_directeur,
                'par':         record.valide_par_directeur,
                'commentaire': record.commentaire_directeur,
            },
            {
                'etape': 5, 'label': 'Validation Divisionnaire', 'role': 'divisionnaire',
                'statut_cible': 'valide_divisionnaire',
                'fait': statut_actuel == 'valide_divisionnaire',
                'date':        record.date_validation_divisionnaire,
                'par':         record.valide_par_divisionnaire,
                'commentaire': record.commentaire_divisionnaire,
            },
        ]

        prochaine_etape = None
        if not est_rejete and statut_actuel != 'valide_divisionnaire':
            mapping_prochaine = {
                'brouillon':               {'action': 'Soumettre',                  'role': 'responsable_structure', 'url': f'/recap/budget/soumettre/{record_id}/'},
                'soumis':                  {'action': 'Valider (Directeur Région)', 'role': 'directeur_region',      'url': f'/recap/budget/valider/directeur-region/{record_id}/'},
                'valide_directeur_region': {'action': 'Valider (Chef)',             'role': 'chef',                  'url': f'/recap/budget/valider/chef/{record_id}/'},
                'valide_chef':             {'action': 'Valider (Directeur)',        'role': 'directeur',             'url': f'/recap/budget/valider/directeur/{record_id}/'},
                'valide_directeur':        {'action': 'Valider (Divisionnaire)',    'role': 'divisionnaire',         'url': f'/recap/budget/valider/divisionnaire/{record_id}/'},
            }
            prochaine_etape = mapping_prochaine.get(statut_actuel)

        return Response({
            'success': True,
            'projet': {
                'id':            record.id,
                'code_division': record.code_division,
                'libelle':       record.libelle,
                'region':        record.region,
                'annee':         getattr(record, 'annee', None),
            },
            'validation': {
                'statut_actuel':   statut_actuel,
                'est_valide':      statut_actuel == 'valide_divisionnaire',
                'est_rejete':      est_rejete,
                'progression':     f"{progression}%",
                'prochaine_etape': prochaine_etape,
                'rejet': {
                    'rejete_par': record.rejete_par,
                    'date_rejet': record.date_rejet,
                    'motif':      record.motif_rejet,
                } if est_rejete else None,
                'etapes': etapes,
            }
        })


# ─────────────────────────────────────────
# LISTES DES PROJETS PAR STATUT ET RÔLE
# ─────────────────────────────────────────

class MesProjetsBrouillonView(APIView):
    """
    GET /recap/mes-projets/brouillon/
    Responsable structure → voit tous ses projets en brouillon
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsResponsableStructure]

    def get(self, request):
        structure_id = getattr(request.user, 'structure_id', None)

        if not structure_id:
            return Response({'error': 'structure_id introuvable dans le token'}, status=400)

        qs = BudgetRecord.objects.filter(
            statut='brouillon',
            structure_id=structure_id
        ).order_by('-id')

        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({'success': True, 'total': qs.count(), 'data': serializer.data})


class ProjetsSoumisParRegionView(APIView):
    """
    GET /recap/projets/soumis/region/
    Directeur région → voit tous les projets soumis dans sa région
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsDirecteurRegion]

    def get(self, request):
        region_id = getattr(request.user, 'region_id', None)

        if not region_id:
            return Response({'error': 'region_id introuvable dans le token'}, status=400)

        service_url = get_service_param_url()
        token = request.headers.get('Authorization', '')

        try:
            region_resp = requests.get(
                f"{service_url}/params/regions/id/{region_id}",
                headers={'Authorization': token},
                timeout=5
            )
            if region_resp.status_code != 200:
                code_region = region_id
                nom_region  = region_id
            else:
                region_data = region_resp.json().get('data', {})
                code_region = region_data.get('code_region', region_id)
                nom_region  = region_data.get('nom_region', region_id)
        except Exception:
            code_region = region_id
            nom_region  = region_id

        qs = BudgetRecord.objects.filter(
            statut='soumis',
            region_id=region_id
        ).order_by('-id')

        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({
            'success': True,
            'region': {'id': region_id, 'code': code_region, 'nom': nom_region},
            'total':  qs.count(),
            'data':   serializer.data
        })


class ProjetsValidesDirecteurRegionView(APIView):
    """
    GET /recap/projets/valides/directeur-region/
    Chef → voit tous les projets validés par les directeurs région
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsChef]

    def get(self, request):
        qs = BudgetRecord.objects.filter(statut='valide_directeur_region').order_by('-id')

        region_id = request.query_params.get('region_id')
        if region_id:
            qs = qs.filter(region_id=region_id)

        upload_id = request.query_params.get('upload_id')
        if upload_id:
            qs = qs.filter(upload_id=upload_id)

        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({'success': True, 'total': qs.count(), 'data': serializer.data})


class ProjetsValidesChefView(APIView):
    """
    GET /recap/projets/valides/chef/
    Directeur → voit tous les projets validés par les chefs
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsDirecteur]

    def get(self, request):
        qs = BudgetRecord.objects.filter(statut='valide_chef').order_by('-id')

        region_id = request.query_params.get('region_id')
        if region_id:
            qs = qs.filter(region_id=region_id)

        upload_id = request.query_params.get('upload_id')
        if upload_id:
            qs = qs.filter(upload_id=upload_id)

        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({'success': True, 'total': qs.count(), 'data': serializer.data})


class ProjetsValidesDirecteurView(APIView):
    """
    GET /recap/projets/valides/directeur/
    Divisionnaire → voit tous les projets validés par les directeurs
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsDivisionnaire]

    def get(self, request):
        qs = BudgetRecord.objects.filter(statut='valide_directeur').order_by('-id')

        region_id = request.query_params.get('region_id')
        if region_id:
            qs = qs.filter(region_id=region_id)

        upload_id = request.query_params.get('upload_id')
        if upload_id:
            qs = qs.filter(upload_id=upload_id)

        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({'success': True, 'total': qs.count(), 'data': serializer.data})


class ProjetsSoumisParRegionFiltreView(APIView):
    """
    GET /recap/projets/soumis/region/filtre/?upload_id=1&annee=2026
    Directeur région → version avec filtres optionnels
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsDirecteurRegion]

    def get(self, request):
        region_id = getattr(request.user, 'region_id', None)

        if not region_id:
            return Response({'error': 'region_id introuvable dans le token'}, status=400)

        service_url = get_service_param_url()
        token = request.headers.get('Authorization', '')

        try:
            region_resp = requests.get(
                f"{service_url}/params/regions/id/{region_id}",
                headers={'Authorization': token},
                timeout=5
            )
            if region_resp.status_code != 200:
                code_region = region_id
                nom_region  = region_id
            else:
                region_data = region_resp.json().get('data', {})
                code_region = region_data.get('code_region', region_id)
                nom_region  = region_data.get('nom_region', region_id)
        except Exception:
            code_region = region_id
            nom_region  = region_id

        qs = BudgetRecord.objects.filter(statut='soumis', region_id=region_id)

        upload_id = request.query_params.get('upload_id')
        if upload_id:
            qs = qs.filter(upload_id=upload_id)

        annee = request.query_params.get('annee')
        if annee:
            qs = qs.filter(annee=annee)

        activite = request.query_params.get('activite')
        if activite:
            qs = qs.filter(activite=activite)

        famille = request.query_params.get('famille')
        if famille:
            qs = qs.filter(famille=famille)

        qs = qs.order_by('-id')

        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({
            'success': True,
            'region': {'id': region_id, 'code': code_region, 'nom': nom_region},
            'filtres': {
                'upload_id': upload_id,
                'annee':     annee,
                'activite':  activite,
                'famille':   famille,
            },
            'total': qs.count(),
            'data':  serializer.data
        })

# ─────────────────────────────────────────
# LISTES DES PROJETS PAR STATUT ET RÔLE (CORRIGÉ AVEC NOUVEAUX CHAMPS)
# ─────────────────────────────────────────

class MesProjetsBrouillonView(APIView):
    """
    GET /recap/mes-projets/brouillon/
    Responsable structure → voit tous ses projets en brouillon
    Filtre par structure_id depuis le token
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsResponsableStructure]

    def get(self, request):
        # Récupérer l'ID de la structure depuis le token
        structure_id = getattr(request.user, 'structure_id', None)
        
        if not structure_id:
            return Response({'error': 'structure_id introuvable dans le token'}, status=400)

        # Filtrer par structure_id (champ direct dans BudgetRecord)
        qs = BudgetRecord.objects.filter(
            statut='brouillon',
            structure_id=structure_id
        ).order_by('-id')
        
        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({
            'success': True,
            'total': qs.count(),
            'data': serializer.data
        })


class ProjetsSoumisParRegionView(APIView):
    """
    GET /recap/projets/soumis/region/
    Directeur région → voit tous les projets soumis dans sa région
    Filtre par region_id depuis le token
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsDirecteurRegion]

    def get(self, request):
        # Récupérer region_id depuis le token (c'est l'ObjectId MongoDB)
        region_id = getattr(request.user, 'region_id', None)
        
        if not region_id:
            return Response({'error': 'region_id introuvable dans le token'}, status=400)

        # Résoudre le code_region depuis region_id (ObjectId) via le service param
        service_url = get_service_param_url()
        token = request.headers.get('Authorization', '')
        
        try:
            region_resp = requests.get(
                f"{service_url}/params/regions/id/{region_id}",
                headers={'Authorization': token},
                timeout=5
            )
            
            if region_resp.status_code != 200:
                # Fallback: utiliser region_id directement comme code_region
                code_region = region_id
                nom_region = region_id
            else:
                region_data = region_resp.json().get('data', {})
                code_region = region_data.get('code_region', region_id)
                nom_region = region_data.get('nom_region', region_id)
            
        except Exception as e:
            # Fallback en cas d'erreur
            code_region = region_id
            nom_region = region_id

        # Filtrer les projets soumis dans cette région
        # Utiliser region_id (ObjectId) OU region (code_region)
        qs = BudgetRecord.objects.filter(statut='soumis').order_by('-id')
        
        # Filtrer par region_id si disponible
        qs = qs.filter(region_id=region_id)
        
        # Alternative: filtrer aussi par code_region si nécessaire
        # qs = qs.filter(models.Q(region_id=region_id) | models.Q(region=code_region))

        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({
            'success': True,
            'region': {
                'id': region_id,
                'code': code_region,
                'nom': nom_region
            },
            'total': qs.count(),
            'data': serializer.data
        })


class ProjetsValidesDirecteurRegionView(APIView):
    """
    GET /recap/projets/valides/directeur-region/
    Chef → voit tous les projets validés par les directeurs région
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsChef]

    def get(self, request):
        qs = BudgetRecord.objects.filter(
            statut='valide_directeur_region'
        ).order_by('-id')
        
        # Filtre optionnel par région
        region_id = request.query_params.get('region_id')
        if region_id:
            qs = qs.filter(region_id=region_id)
        
        # Filtre optionnel par upload
        upload_id = request.query_params.get('upload_id')
        if upload_id:
            qs = qs.filter(upload_id=upload_id)

        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({
            'success': True,
            'total': qs.count(),
            'data': serializer.data
        })


class ProjetsValidesChefView(APIView):
    """
    GET /recap/projets/valides/chef/
    Directeur → voit tous les projets validés par les chefs
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsDirecteur]

    def get(self, request):
        qs = BudgetRecord.objects.filter(
            statut='valide_chef'
        ).order_by('-id')
        
        # Filtre optionnel par région
        region_id = request.query_params.get('region_id')
        if region_id:
            qs = qs.filter(region_id=region_id)
        
        # Filtre optionnel par upload
        upload_id = request.query_params.get('upload_id')
        if upload_id:
            qs = qs.filter(upload_id=upload_id)

        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({
            'success': True,
            'total': qs.count(),
            'data': serializer.data
        })


class ProjetsValidesDirecteurView(APIView):
    """
    GET /recap/projets/valides/directeur/
    Divisionnaire → voit tous les projets validés par les directeurs
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsDivisionnaire]

    def get(self, request):
        qs = BudgetRecord.objects.filter(
            statut='valide_directeur'
        ).order_by('-id')
        
        # Filtre optionnel par région
        region_id = request.query_params.get('region_id')
        if region_id:
            qs = qs.filter(region_id=region_id)
        
        # Filtre optionnel par upload
        upload_id = request.query_params.get('upload_id')
        if upload_id:
            qs = qs.filter(upload_id=upload_id)

        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({
            'success': True,
            'total': qs.count(),
            'data': serializer.data
        })


# Version alternative avec filtres supplémentaires
class ProjetsSoumisParRegionFiltreView(APIView):
    """
    GET /recap/projets/soumis/region/filtre/?upload_id=1&annee=2026
    Directeur région → version avec filtres optionnels
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsDirecteurRegion]

    def get(self, request):
        region_id = getattr(request.user, 'region_id', None)
        
        if not region_id:
            return Response({'error': 'region_id introuvable dans le token'}, status=400)

        # Résoudre le code_region depuis region_id
        service_url = get_service_param_url()
        token = request.headers.get('Authorization', '')
        
        try:
            region_resp = requests.get(
                f"{service_url}/params/regions/id/{region_id}",
                headers={'Authorization': token},
                timeout=5
            )
            
            if region_resp.status_code != 200:
                code_region = region_id
                nom_region = region_id
            else:
                region_data = region_resp.json().get('data', {})
                code_region = region_data.get('code_region', region_id)
                nom_region = region_data.get('nom_region', region_id)
        except Exception as e:
            code_region = region_id
            nom_region = region_id

        # Base queryset filtrée par region_id
        qs = BudgetRecord.objects.filter(
            statut='soumis',
            region_id=region_id
        )

        # Filtres optionnels
        upload_id = request.query_params.get('upload_id')
        if upload_id:
            qs = qs.filter(upload_id=upload_id)

        annee = request.query_params.get('annee')
        if annee:
            qs = qs.filter(annee=annee)

        activite = request.query_params.get('activite')
        if activite:
            qs = qs.filter(activite=activite)

        famille = request.query_params.get('famille')
        if famille:
            qs = qs.filter(famille=famille)

        qs = qs.order_by('-id')

        serializer = BudgetRecordSerializer(qs, many=True)
        return Response({
            'success': True,
            'region': {
                'id': region_id,
                'code': code_region,
                'nom': nom_region
            },
            'filtres': {
                'upload_id': upload_id,
                'annee': annee,
                'activite': activite,
                'famille': famille,
            },
            'total': qs.count(),
            'data': serializer.data
        })
    

# ================================================================== #
#  Listes les projets
# ================================================================== #
# ================================================================== #
#  RESPONSABLE STRUCTURE
#  Filtre auto : structure_id du token
# ================================================================== #
class ListeProjetsResponsableView(APIView):
    """
    GET /recap/budget/projets/responsable/
    ?statut=brouillon|soumis|...
    ?type_projet=nouveau|en_cours
    ?code_division=PROJ001
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsResponsableStructure]

    def get(self, request):
        structure_id = getattr(request.user, 'structure_id', None)

        if not structure_id:
            return Response(
                {'error': "Votre token ne contient pas de structure_id."},
                status=403
            )

        qs = BudgetRecord.objects.filter(
            structure_id=structure_id,
            # is_active=True,
        )

        statut        = request.query_params.get('statut')
        type_projet   = request.query_params.get('type_projet')
        code_division = request.query_params.get('code_division')

        if statut:
            qs = qs.filter(statut=statut)
        if type_projet:
            qs = qs.filter(type_projet=type_projet)
        if code_division:
            qs = qs.filter(code_division__icontains=code_division)

        qs = qs.order_by('-id')

        from django.db.models import Count
        compteurs = {
            item['statut']: item['total']
            for item in qs.values('statut').annotate(total=Count('id'))
        }

        return Response({
            'count':                qs.count(),
            'compteurs_par_statut': compteurs,
            'projets':              BudgetRecordSerializer(qs, many=True).data,
        })


# ================================================================== #
#  DIRECTEUR RÉGION
#  Filtre auto : region_id du token
# ================================================================== #
class ListeProjetsDirecteurRegionView(APIView):
    """
    GET /recap/budget/projets/directeur-region/
    ?statut=soumis|reserve_agent|reserve_chef|reserve_directeur|tous
    ?type_projet=nouveau|en_cours
    ?code_division=PROJ001
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsDirecteurRegion]

    STATUTS_PAR_DEFAUT = [
        'soumis',
        'reserve_agent',
        'reserve_chef',
        'reserve_directeur',
    ]

    def get(self, request):
        region_id = getattr(request.user, 'region_id', None)

        if not region_id:
            return Response(
                {'error': "Votre token ne contient pas de region_id."},
                status=403
            )

        qs = BudgetRecord.objects.filter(
            region_id=region_id,
            is_active=True,
        )

        statut        = request.query_params.get('statut')
        type_projet   = request.query_params.get('type_projet')
        code_division = request.query_params.get('code_division')

        if statut and statut != 'tous':
            qs = qs.filter(statut=statut)
        else:
            qs = qs.filter(statut__in=self.STATUTS_PAR_DEFAUT)

        if type_projet:
            qs = qs.filter(type_projet=type_projet)
        if code_division:
            qs = qs.filter(code_division__icontains=code_division)

        qs = qs.order_by('-id')

        from django.db.models import Count
        compteurs = {
            item['statut']: item['total']
            for item in qs.values('statut').annotate(total=Count('id'))
        }

        return Response({
            'count':                qs.count(),
            'compteurs_par_statut': compteurs,
            'projets':              BudgetRecordSerializer(qs, many=True).data,
        })


# ================================================================== #
#  AGENT
#  Pas de filtre auto par structure/région
#  Voit tous les projets valide_directeur_region
# ================================================================== #
class ListeProjetsAgentView(APIView):
    """
    GET /recap/budget/projets/agent/
    ?type_projet=nouveau|en_cours
    ?code_division=PROJ001
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsAgent]

    def get(self, request):
        qs = BudgetRecord.objects.filter(
            statut='valide_directeur_region',
            is_active=True,
        )

        type_projet   = request.query_params.get('type_projet')
        code_division = request.query_params.get('code_division')

        if type_projet:
            qs = qs.filter(type_projet=type_projet)
        if code_division:
            qs = qs.filter(code_division__icontains=code_division)

        qs = qs.order_by('-id')

        return Response({
            'count':   qs.count(),
            'projets': BudgetRecordSerializer(qs, many=True).data,
        })


# ================================================================== #
#  CHEF
#  Pas de filtre auto par structure/région
#  Voit valide_agent + reserve_agent
# ================================================================== #
class ListeProjetsChefView(APIView):
    """
    GET /recap/budget/projets/chef/
    ?statut=valide_agent|reserve_agent|tous
    ?type_projet=nouveau|en_cours
    ?code_division=PROJ001
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsChef]

    STATUTS_PAR_DEFAUT = ['valide_agent', 'reserve_agent']

    def get(self, request):
        qs = BudgetRecord.objects.filter(
            is_active=True,
        )

        statut        = request.query_params.get('statut')
        type_projet   = request.query_params.get('type_projet')
        code_division = request.query_params.get('code_division')

        if statut and statut != 'tous':
            if statut not in self.STATUTS_PAR_DEFAUT:
                return Response(
                    {
                        'error': (
                            f"Statut '{statut}' non autorisé. "
                            f"Acceptés : {', '.join(self.STATUTS_PAR_DEFAUT)}"
                        )
                    },
                    status=400
                )
            qs = qs.filter(statut=statut)
        else:
            qs = qs.filter(statut__in=self.STATUTS_PAR_DEFAUT)

        if type_projet:
            qs = qs.filter(type_projet=type_projet)
        if code_division:
            qs = qs.filter(code_division__icontains=code_division)

        qs = qs.order_by('-id')

        from django.db.models import Count
        compteurs = {
            item['statut']: item['total']
            for item in qs.values('statut').annotate(total=Count('id'))
        }

        return Response({
            'count':                qs.count(),
            'compteurs_par_statut': compteurs,
            'projets':              BudgetRecordSerializer(qs, many=True).data,
        })


# ================================================================== #
#  DIRECTEUR
#  Pas de filtre auto par structure/région
#  Voit valide_chef
# ================================================================== #
class ListeProjetsDirecteurView(APIView):
    """
    GET /recap/budget/projets/directeur/
    ?type_projet=nouveau|en_cours
    ?code_division=PROJ001
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsDirecteur]

    def get(self, request):
        qs = BudgetRecord.objects.filter(
            statut='valide_chef',
            is_active=True,
        )

        type_projet   = request.query_params.get('type_projet')
        code_division = request.query_params.get('code_division')

        if type_projet:
            qs = qs.filter(type_projet=type_projet)
        if code_division:
            qs = qs.filter(code_division__icontains=code_division)

        qs = qs.order_by('-id')

        return Response({
            'count':   qs.count(),
            'projets': BudgetRecordSerializer(qs, many=True).data,
        })


# ================================================================== #
#  DIVISIONNAIRE
#  Pas de filtre auto
#  Voit valide_directeur — toutes régions
# ================================================================== #
class ListeProjetsDivisionnnaireView(APIView):
    """
    GET /recap/budget/projets/divisionnaire/
    ?type_projet=nouveau|en_cours
    ?code_division=PROJ001
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsDivisionnaire]

    def get(self, request):
        qs = BudgetRecord.objects.filter(
            statut='valide_directeur',
            is_active=True,
        )

        type_projet   = request.query_params.get('type_projet')
        code_division = request.query_params.get('code_division')

        if type_projet:
            qs = qs.filter(type_projet=type_projet)
        if code_division:
            qs = qs.filter(code_division__icontains=code_division)

        qs = qs.order_by('-id')

        from django.db.models import Count
        par_region = {
            item['region_id']: item['total']
            for item in qs.values('region_id').annotate(total=Count('id'))
        }

        return Response({
            'count':      qs.count(),
            'par_region': par_region,
            'projets':    BudgetRecordSerializer(qs, many=True).data,
        })


# ================================================================== #
#  HISTORIQUE PAR CODE_DIVISION
#  Accessible par tous les rôles
# ================================================================== #
class HistoriqueProjetView(APIView):
    """
    GET /recap/budget/historique/<code_division>/
    GET /recap/budget/historique/<code_division>/actif/
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes     = [IsAgent]

    def get(self, request, code_division, mode=None):
        qs = BudgetRecord.objects.filter(
            code_division=code_division
        ).order_by('-version')

        if not qs.exists():
            return Response(
                {'error': f'Projet {code_division} introuvable.'},
                status=404
            )

        if mode == 'actif':
            actif = qs.filter(is_active=True).first() or qs.first()
            return Response({
                'code_division':  code_division,
                'version_active': BudgetRecordSerializer(actif).data,
            })

        actif    = qs.filter(is_active=True).first() or qs.first()
        derniere = qs.first()
        premiere = qs.last()

        return Response({
            'code_division':    code_division,
            'total_versions':   qs.count(),
            'version_active':   actif.version,
            'derniere_version': derniere.version,
            'premiere_version': premiere.version,
            'historique':       BudgetRecordSerializer(qs, many=True).data,
        })
    