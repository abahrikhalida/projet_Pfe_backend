
# from rest_framework.decorators import api_view, permission_classes, parser_classes
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.parsers import MultiPartParser
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.utils.crypto import get_random_string
# from django.core.mail import send_mail
# from django.conf import settings
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str
# from datetime import datetime, date, timedelta
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# import openpyxl
# from .models import User, Agent


# # Helper pour nom complet
# def nom_complet(obj):
#     return f"{obj.prenom} {obj.nom}"


# # ==========================
# # LOGIN API (JWT)
# # ==========================

# @api_view(['POST'])
# def api_login(request):
#     data = request.data
#     email = data.get('email')
#     password = data.get('password')

#     try:
#         user = User.objects.get(email=email)
#     except User.DoesNotExist:
#         return Response(
#             {"status": "error", "message": "Email ou mot de passe incorrect."},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     if not user.check_password(password):
#         return Response(
#             {"status": "error", "message": "Email ou mot de passe incorrect."},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     refresh = RefreshToken.for_user(user)
#     #code ajouter
    
#     # ✅ Ajouter region_id et structure_id dans le token
#     refresh['region_id']    = str(user.region_id)    if user.region_id    else None
#     refresh['structure_id'] = str(user.structure_id) if user.structure_id else None
#     refresh['role']         = user.role
#     refresh['user_id']      = str(user.id)


#     return Response({
#         "status": "success",
#         "role": getattr(user, 'role', None),
#         "refresh": str(refresh),
#         "access": str(refresh.access_token),
#         "message": f"Logged in as {nom_complet(user)}",
#         "nom_complet": nom_complet(user),
#         "photo_profil": user.photo_profil.url if user.photo_profil else None,   # ✅
#         "region_id":    str(user.region_id)    if user.region_id    else None,   # ✅
#         "structure_id": str(user.structure_id) if user.structure_id else None,   # ✅
#     })


# # ==========================
# # LOGOUT
# # ==========================

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def api_logout(request):
#     try:
#         refresh_token = request.data.get("refresh")
#         token = RefreshToken(refresh_token)
#         token.blacklist()
#         return Response({"status": "success", "message": "Logged out successfully"})
#     except Exception as e:
#         return Response({"status": "error", "message": str(e)}, status=400)


# # ==========================
# # CHANGE PASSWORD
# # ==========================

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def api_change_password(request):
#     user = request.user
#     old_password = request.data.get("old_password")
#     new_password = request.data.get("new_password")

#     if not user.check_password(old_password):
#         return Response({"status": "error", "message": "Old password incorrect"}, status=400)

#     user.set_password(new_password)
#     user.save()
#     return Response({"status": "success", "message": "Password changed successfully"})


# # ==========================
# # RESET PASSWORD
# # ==========================

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def api_reset_password(request):
#     email = request.data.get("email")
#     try:
#         user = User.objects.get(email=email)
#     except User.DoesNotExist:
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

#     token = PasswordResetTokenGenerator().make_token(user)
#     uid = urlsafe_base64_encode(force_bytes(user.pk))

#     reset_url = f"http://localhost:3000/reset-confirm/{uid}/{token}"
#     subject = "Réinitialisation de mot de passe"
#     message = f"Bonjour {user.prenom},\n\nPour réinitialiser votre mot de passe, cliquez sur ce lien :\n{reset_url}\n\nSi vous n'avez pas demandé cette réinitialisation, ignorez cet email."

#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

#     return Response({"status": "success", "message": "Email de réinitialisation envoyé."})


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def api_reset_password_confirm(request):
#     uid = request.data.get("uid")
#     token = request.data.get("token")
#     new_password = request.data.get("new_password")

#     if not all([uid, token, new_password]):
#         return Response({"status": "error", "message": "uid, token et new_password sont requis"}, status=400)

#     try:
#         user_id = force_str(urlsafe_base64_decode(uid))
#         user = User.objects.get(pk=user_id)
#     except (User.DoesNotExist, ValueError):
#         return Response({"status": "error", "message": "Lien invalide"}, status=400)

#     if PasswordResetTokenGenerator().check_token(user, token):
#         user.set_password(new_password)
#         user.save()
#         return Response({"status": "success", "message": "Mot de passe réinitialisé avec succès"})
#     else:
#         return Response({"status": "error", "message": "Token invalide ou expiré"}, status=400)


# # ==========================
# # CREATE USER
# # ==========================


# from .serializers import UserSerializer
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# @api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser, JSONParser])
# def api_create_user(request):
#     serializer = UserSerializer(data=request.data)

#     if serializer.is_valid():
#         user = serializer.save()

#         return Response({
#             "status": "success",
#             "user": serializer.data,
#             "generated_password": getattr(user, "generated_password", None)
#         })

#     return Response(serializer.errors, status=400)

# # ==========================
# # LIST USERS
# # ==========================

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def api_list_users(request):
#     users = User.objects.all()
#     data = [{
#         "id": u.id,
#         "email": u.email,
#         "nom_complet": nom_complet(u),
#         "role": u.role,
#         "photo_profil": u.photo_profil.url if u.photo_profil else None,
#         "is_staff": u.is_staff,
#         "is_superuser": u.is_superuser
#     } for u in users]

#     return Response({"status": "success", "users": data})


# # ==========================
# # GET USER
# # ==========================

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def api_get_user(request, user_id):
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({"status": "error", "message": "User non trouvé"}, status=404)

#     return Response({
#         "id": user.id,
#         "email": user.email,
#         "nom_complet": nom_complet(user),
#         "role": user.role,
#         "photo_profil": user.photo_profil.url if user.photo_profil else None,
#         "is_staff": user.is_staff,
#         "is_superuser": user.is_superuser
#     })


# # ==========================
# # UPDATE USER
# # ==========================

# @api_view(['PUT', 'PATCH'])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser, FormParser, JSONParser])
# def api_update_user(request, user_id):
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({"status": "error", "message": "User non trouvé"}, status=404)

#     data = request.data
#     user.nom = data.get('nom', user.nom)
#     user.prenom = data.get('prenom', user.prenom)
#     user.email = data.get('email', user.email)
#     user.role = data.get('role', user.role)

#     if 'photo_profil' in request.FILES:
#         user.photo_profil = request.FILES['photo_profil']

#     user.save()

#     return Response({
#         "status": "success",
#         "message": f"User {nom_complet(user)} mis à jour",
#         "user": {
#             "id": user.id,
#             "email": user.email,
#             "nom_complet": nom_complet(user),
#             "role": user.role,
#             "photo_profil": user.photo_profil.url if user.photo_profil else None,
#         }
#     })


# # ==========================
# # DELETE USER
# # ==========================

# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def api_delete_user(request, user_id):
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({"status": "error", "message": "User non trouvé"}, status=404)

#     user.delete()
#     return Response({"status": "success", "message": f"User {nom_complet(user)} supprimé"})


# # ==========================
# # CREATE AGENT
# # ==========================

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser])
# def api_create_agent(request):
#     if getattr(request.user, 'role', None) != 'chef':
#         return Response({"status": "error", "message": "Accès refusé"}, status=403)

#     data = request.data
#     photo = request.FILES.get('photo_profil')
#     password_temp = get_random_string(8)

#     agent = Agent(
#         chef=request.user,
#         nom=data.get('nom'),
#         prenom=data.get('prenom'),
#         email=data.get('email'),
#         adresse=data.get('adresse'),
#         date_naissance=data.get('date_naissance'),
#         sexe=data.get('sexe'),
#         telephone=data.get('telephone'),
#         matricule=data.get('matricule'),
#         poste=data.get('poste'),
#         password_temp=password_temp,
#         is_activated=True
#     )
#     agent.save()

#     if not agent.user:
#         agent.user = User.objects.create_user(
#             email=agent.email,
#             nom=agent.nom,
#             prenom=agent.prenom,
#             role='agent',
#             password=password_temp
#         )

#     if photo:
#         agent.user.photo_profil = photo
#         agent.user.save()

#     agent.save()

#     return Response({
#         "status": "success",
#         "message": f"Agent {nom_complet(agent)} créé",
#         "agent": {
#             "id": agent.id,
#             "nom_complet": nom_complet(agent),
#             "email": agent.email,
#             "adresse": agent.adresse,
#             "date_naissance": agent.date_naissance,
#             "sexe": agent.sexe,
#             "telephone": agent.telephone,
#             "matricule": agent.matricule,
#             "poste": agent.poste,
#             "is_activated": agent.is_activated,
#             "password_temp": password_temp,
#             "user": {
#                 "id": agent.user.id,
#                 "role": agent.user.role,
#                 "photo_profil": agent.user.photo_profil.url if agent.user.photo_profil else None
#             },
#             "chef": {
#                 "id": agent.chef.id,
#                 "nom_complet": nom_complet(agent.chef),
#                 "email": agent.chef.email,
#                 "role": agent.chef.role,
#                 "photo_profil": agent.chef.photo_profil.url if agent.chef.photo_profil else None
#             }
#         }
#     })


# # ==========================
# # LIST AGENTS
# # ==========================

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def api_list_agents(request):
#     user = request.user
#     agents = Agent.objects.filter(chef=user) if getattr(user, 'role', None) == 'chef' else Agent.objects.all()

#     data = [{
#         "id": a.id,
#         "nom_complet": nom_complet(a),
#         "email": a.email,
#         "matricule": a.matricule,
#         "poste": a.poste,
#         "adresse": a.adresse,
#         "date_naissance": a.date_naissance.strftime('%Y-%m-%d') if a.date_naissance else None,
#         "sexe": a.sexe,
#         "telephone": a.telephone,
#         "is_activated": a.is_activated,
#         "photo_profil": a.user.photo_profil.url if a.user and a.user.photo_profil else None,
#         "chef": {
#             "id": a.chef.id if a.chef else None,
#             "nom_complet": nom_complet(a.chef) if a.chef else None,
#             "email": a.chef.email if a.chef else None,
#             "role": a.chef.role if a.chef else None,
#             "photo_profil": a.chef.photo_profil.url if a.chef and a.chef.photo_profil else None
#         }
#     } for a in agents]

#     return Response({"status": "success", "agents": data})


# # ==========================
# # UPDATE AGENT
# # ==========================





# # le chef modifier profil de agent  +agent modifier son profil
# @api_view(['PUT', 'PATCH'])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser])
# def api_update_agent(request, agent_id):
#     try:
#         agent = Agent.objects.get(id=agent_id)
#     except Agent.DoesNotExist:
#         return Response({"status": "error", "message": "Agent non trouvé"}, status=404)

#     user_request = request.user

#     # Chef ne peut modifier que ses propres agents
#     if getattr(user_request, 'role', None) == 'chef' and agent.chef != user_request:
#         return Response({"status": "error", "message": "Accès refusé"}, status=403)

#     # Agent ne peut modifier que son propre profil
#     if getattr(user_request, 'role', None) == 'agent' and agent.user != user_request:
#         return Response({"status": "error", "message": "Accès refusé"}, status=403)

#     data = request.data

#     # Agent ne peut pas modifier ces champs sensibles
#     if getattr(user_request, 'role', None) == 'agent':
#         agent.nom = data.get('nom', agent.nom)
#         agent.prenom = data.get('prenom', agent.prenom)
#         agent.adresse = data.get('adresse', agent.adresse)
#         agent.telephone = data.get('telephone', agent.telephone)
#     else:
#         # Chef/admin peut tout modifier
#         agent.nom = data.get('nom', agent.nom)
#         agent.prenom = data.get('prenom', agent.prenom)
#         agent.email = data.get('email', agent.email)
#         agent.adresse = data.get('adresse', agent.adresse)
#         agent.date_naissance = data.get('date_naissance', agent.date_naissance)
#         agent.sexe = data.get('sexe', agent.sexe)
#         agent.telephone = data.get('telephone', agent.telephone)
#         agent.matricule = data.get('matricule', agent.matricule)
#         agent.poste = data.get('poste', agent.poste)

#     agent.save()

#     photo = request.FILES.get('photo_profil')
#     if agent.user:
#         agent.user.nom = agent.nom
#         agent.user.prenom = agent.prenom
#         agent.user.email = agent.email
#         if photo:
#             agent.user.photo_profil = photo
#         agent.user.save()

#     return Response({
#         "status": "success",
#         "message": f"Agent {nom_complet(agent)} mis à jour",
#         "agent": {
#             "id": agent.id,
#             "nom_complet": nom_complet(agent),
#             "email": agent.email,
#             "adresse": agent.adresse,
#             "date_naissance": agent.date_naissance,
#             "sexe": agent.sexe,
#             "telephone": agent.telephone,
#             "matricule": agent.matricule,
#             "poste": agent.poste,
#             "password_temp": agent.password_temp,
#             "activation_code": agent.activation_code,
#             "is_activated": agent.is_activated,
#             "role": agent.user.role if agent.user else None,
#             "photo_profil": agent.user.photo_profil.url if agent.user and agent.user.photo_profil else None,
#             "chef": {
#                 "id": agent.chef.id,
#                 "nom_complet": nom_complet(agent.chef),
#                 "email": agent.chef.email,
#                 "role": agent.chef.role,
#                 "photo_profil": agent.chef.photo_profil.url if agent.chef.photo_profil else None
#             }
#         }
#     })

# # ==========================
# # DELETE AGENT
# # ==========================

# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def api_delete_agent(request, agent_id):
#     try:
#         agent = Agent.objects.get(id=agent_id)
#     except Agent.DoesNotExist:
#         return Response({"status": "error", "message": "Agent non trouvé"}, status=404)

#     user = request.user
#     if getattr(user, 'role', None) == 'chef' and agent.chef != user:
#         return Response({"status": "error", "message": "Accès refusé"}, status=403)

#     agent.delete()
#     return Response({"status": "success", "message": f"Agent {nom_complet(agent)} supprimé"})


# # ==========================
# # CREATE AGENTS FROM EXCEL
# # ==========================

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser])
# def api_create_agents_excel(request):
#     if getattr(request.user, 'role', None) != 'chef':
#         return Response({"status": "error", "message": "Accès refusé"}, status=403)

#     file_obj = request.FILES.get('file')
#     if not file_obj:
#         return Response({"status": "error", "message": "Fichier Excel requis"}, status=400)

#     try:
#         wb = openpyxl.load_workbook(file_obj, data_only=True)
#         sheet = wb.active
#     except Exception as e:
#         return Response({"status": "error", "message": f"Impossible de lire le fichier : {str(e)}"}, status=400)

#     created_agents = []
#     skipped_agents = []

#     for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
#         if not any(row):
#             continue
#         if len(row) < 9:
#             skipped_agents.append({"row": row_idx, "reason": "Colonnes manquantes"})
#             continue

#         nom, prenom, email, adresse, date_naissance, sexe, telephone, matricule, poste = row
#         email = str(email).strip() if email else None
#         if not email:
#             skipped_agents.append({"row": row_idx, "reason": "Email manquant"})
#             continue
#         if Agent.objects.filter(email=email).exists():
#             skipped_agents.append({"email": email, "reason": "Email déjà existant"})
#             continue

#         dn = None
#         if isinstance(date_naissance, (datetime, date)):
#             dn = date_naissance if isinstance(date_naissance, date) else date_naissance.date()
#         elif isinstance(date_naissance, str):
#             for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
#                 try:
#                     dn = datetime.strptime(date_naissance.strip(), fmt).date()
#                     break
#                 except ValueError:
#                     continue
#         elif isinstance(date_naissance, (int, float)):
#             dn = (date(1899, 12, 30) + timedelta(days=int(date_naissance)))

#         if dn is None:
#             skipped_agents.append({"email": email, "reason": f"Format date invalide: {date_naissance}"})
#             continue

#         try:
#             agent = Agent(
#                 chef=request.user,
#                 nom=str(nom).strip() if nom else "",
#                 prenom=str(prenom).strip() if prenom else "",
#                 email=email,
#                 adresse=str(adresse).strip() if adresse else "",
#                 date_naissance=dn,
#                 sexe=str(sexe).strip().upper() if sexe else "",
#                 telephone=str(telephone).strip() if telephone else "",
#                 matricule=str(matricule).strip() if matricule else "",
#                 poste=str(poste).strip() if poste else "",
#             )
#             agent.save()

#             created_agents.append({
#                 "id": agent.id,
#                 "nom_complet": nom_complet(agent),
#                 "email": agent.email,
#                 "adresse": agent.adresse,
#                 "date_naissance": agent.date_naissance.strftime('%Y-%m-%d') if agent.date_naissance else None,
#                 "sexe": agent.sexe,
#                 "telephone": agent.telephone,
#                 "matricule": agent.matricule,
#                 "poste": agent.poste,
#                 "password_temp": agent.password_temp,
#                 "activation_code": agent.activation_code,
#                 "is_activated": agent.is_activated,
#                 "user": {
#                     "id": agent.user.id if agent.user else None,
#                     "role": agent.user.role if agent.user else None,
#                     "photo_profil": agent.user.photo_profil.url if agent.user and agent.user.photo_profil else None
#                 },
#                 "chef": {
#                     "id": agent.chef.id if agent.chef else None,
#                     "nom_complet": nom_complet(agent.chef) if agent.chef else None,
#                     "email": agent.chef.email if agent.chef else None,
#                     "role": agent.chef.role if agent.chef else None,
#                     "photo_profil": agent.chef.photo_profil.url if agent.chef and agent.chef.photo_profil else None
#                 }
#             })

#         except Exception as e:
#             skipped_agents.append({"email": email, "reason": str(e)})

#     return Response({
#         "status": "success",
#         "total_created": len(created_agents),
#         "created": created_agents,
#         "skipped": skipped_agents
#     })
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from datetime import datetime

from .models import User, Agent


# ==========================
# UTILS
# ==========================
def nom_complet(obj):
    return f"{obj.prenom} {obj.nom}"



# ==========================
# LOGIN API (JWT)
# ==========================

@api_view(['POST'])
def api_login(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"status": "error", "message": "Email ou mot de passe incorrect."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.check_password(password):
        return Response(
            {"status": "error", "message": "Email ou mot de passe incorrect."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    #code ajouter
    
    # ✅ Ajouter region_id et structure_id dans le token
    refresh['region_id']    = str(user.region_id)    if user.region_id    else None
    refresh['structure_id'] = str(user.structure_id) if user.structure_id else None
    refresh['role']         = user.role
    refresh['user_id']      = str(user.id)


    return Response({
        "status": "success",
        "role": getattr(user, 'role', None),
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "message": f"Logged in as {nom_complet(user)}",
        "nom_complet": nom_complet(user),
        "photo_profil": user.photo_profil.url if user.photo_profil else None,   # ✅
        "region_id":    str(user.region_id)    if user.region_id    else None,   # ✅
        "structure_id": str(user.structure_id) if user.structure_id else None,   # ✅
    })


# ==========================
# LOGOUT
# ==========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"status": "success", "message": "Logged out successfully"})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=400)


# ==========================
# CHANGE PASSWORD
# ==========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_change_password(request):
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not user.check_password(old_password):
        return Response({"status": "error", "message": "Old password incorrect"}, status=400)

    user.set_password(new_password)
    user.save()
    return Response({"status": "success", "message": "Password changed successfully"})


# ==========================
# RESET PASSWORD
# ==========================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_reset_password(request):
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

    token = PasswordResetTokenGenerator().make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    reset_url = f"http://localhost:3000/reset-confirm/{uid}/{token}"
    subject = "Réinitialisation de mot de passe"
    message = f"Bonjour {user.prenom},\n\nPour réinitialiser votre mot de passe, cliquez sur ce lien :\n{reset_url}\n\nSi vous n'avez pas demandé cette réinitialisation, ignorez cet email."

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

    return Response({"status": "success", "message": "Email de réinitialisation envoyé."})


@api_view(['POST'])
@permission_classes([AllowAny])
def api_reset_password_confirm(request):
    uid = request.data.get("uid")
    token = request.data.get("token")
    new_password = request.data.get("new_password")

    if not all([uid, token, new_password]):
        return Response({"status": "error", "message": "uid, token et new_password sont requis"}, status=400)

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError):
        return Response({"status": "error", "message": "Lien invalide"}, status=400)

    if PasswordResetTokenGenerator().check_token(user, token):
        user.set_password(new_password)
        user.save()
        return Response({"status": "success", "message": "Mot de passe réinitialisé avec succès"})
    else:
        return Response({"status": "error", "message": "Token invalide ou expiré"}, status=400)




# ==========================
# CREATE USER SIMPLE
# ==========================

from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_create_user(request):
    if request.user.role != 'admin':
        return Response(
            {"status": "error", "message": "Accès admin uniquement"},
            status=403
        )

    data = request.data

    required = ['email', 'nom', 'prenom']
    missing = [f for f in required if not data.get(f)]

    if missing:
        return Response(
            {"status": "error", "message": f"Champs manquants : {', '.join(missing)}"},
            status=400
        )

    email = data.get('email').strip().lower()

    if User.objects.filter(email=email).exists():
        return Response(
            {"status": "error", "message": "Email déjà utilisé"},
            status=400
        )

    # 🔐 password auto
    temp_password = get_random_string(10)

    user = User(
        email=email,
        nom=data.get('nom').strip(),
        prenom=data.get('prenom').strip(),
        role=data.get('role'),
        adresse=data.get('adresse'),
        telephone=data.get('telephone'),
        date_naissance=data.get('date_naissance'),
        sexe=data.get('sexe'),
        matricule=data.get('matricule'),
        poste=data.get('poste'),
        region_id=data.get('region_id'),
        structure_id=data.get('structure_id'),
    )

    if 'photo_profil' in request.FILES:
        user.photo_profil = request.FILES['photo_profil']

    user.set_password(temp_password)
    user.save()

    # ✅ ENVOYER L'EMAIL DIRECTEMENT ICI
    try:
        send_mail(
            subject="Votre compte a été créé",
            message=(
                f"Bonjour {user.prenom} {user.nom},\n\n"
                f"Votre compte a été créé avec succès.\n\n"
                f"📧 Email: {user.email}\n"
                f"🔑 Mot de passe temporaire: {temp_password}\n\n"
                f"⚠️  Veuillez changer votre mot de passe lors de votre première connexion.\n\n"
                f"Cordialement,\nL'équipe administrative"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,  # Mettre False pour voir les erreurs en développement
        )
        print(f"✅ Email envoyé à {user.email}")
    except Exception as e:
        print(f"❌ ERREUR ENVOI EMAIL: {e}")
        # Vous pouvez logger l'erreur mais continuer quand même
        import traceback
        traceback.print_exc()

    # Reste de votre réponse...
    return Response({
        "status": "success",
        "message": "Utilisateur créé avec succès",
        "credentials": {
            "email": user.email,
            "generated_password": temp_password
        },
        "user": {
            "id": user.id,
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom,
            "role": user.role,
            "adresse": user.adresse,
            "telephone": user.telephone,
            "date_naissance": user.date_naissance,
            "sexe": user.sexe,
            "matricule": user.matricule,
            "poste": user.poste,
            "region_id": user.region_id,
            "structure_id": user.structure_id,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "photo_profil": user.photo_profil.url if user.photo_profil else None,
            "groups": list(user.groups.values_list("name", flat=True)),
        }
    }, status=201)

# ==========================
# ASSIGN ROLE
# ==========================
#//////////////////////////////////ancien view affectation///////////////////////////////////////
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def api_assign_role(request):
#     if request.user.role != 'admin':
#         return Response({"status": "error", "message": "Accès admin uniquement"}, status=403)

#     user_id = request.data.get('user_id')
#     role = request.data.get('role')

#     if not user_id or not role:
#         return Response({"status": "error", "message": "user_id et role obligatoires"}, status=400)

#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

#     # validation rôle
#     if role not in ['admin', 'chef', 'agent']:
#         return Response({"status": "error", "message": "Rôle invalide"}, status=400)

#     user.role = role
#     user.save()

#     # 🔥 si agent → création Agent auto
#     if role == 'agent':
#         try:
#             chef = User.objects.get(role='chef')  # 1 seul chef
#         except User.DoesNotExist:
#             return Response({"status": "error", "message": "Aucun chef trouvé"}, status=400)

#         Agent.objects.update_or_create(
#             user=user,
#             defaults={'chef': chef}
#         )

#         return Response({
#             "status": "success",
#             "message": f"{nom_complet(user)} est maintenant agent",
#             "chef": {
#                 "id": chef.id,
#                 "nom_complet": nom_complet(chef)
#             }
#         })

#     return Response({
#         "status": "success",
#         "message": f"Rôle {role} attribué à {nom_complet(user)}"
#     })
#//////////////////////////////////new view affectation///////////////////////////////////////

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def api_assign_role(request):
#     # Cas 1: Non admin
#     if request.user.role != 'admin':
#         return Response({
#             "status": "error",
#             "code": "FORBIDDEN",
#             "message": "Accès admin uniquement",
#             "error_details": "Votre rôle actuel ne vous permet pas d'assigner des rôles"
#         }, status=403)

#     user_id = request.data.get('user_id')
#     role = request.data.get('role')

#     # Cas 2: Champs manquants
#     if not user_id or not role:
#         missing_fields = []
#         if not user_id: missing_fields.append('user_id')
#         if not role: missing_fields.append('role')
        
#         return Response({
#             "status": "error",
#             "code": "MISSING_FIELDS",
#             "message": "Champs obligatoires manquants",
#             "missing_fields": missing_fields,
#             "required_fields": ["user_id", "role"]
#         }, status=400)

#     # Cas 3: Utilisateur non trouvé
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({
#             "status": "error",
#             "code": "USER_NOT_FOUND",
#             "message": "Utilisateur non trouvé",
#             "error_details": f"Aucun utilisateur avec l'ID {user_id} n'existe"
#         }, status=404)

#     # Cas 4: Rôle invalide
#     valid_roles = ['admin', 'chef', 'agent']
#     if role not in valid_roles:
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": "Rôle invalide",
#             "error_details": f"Le rôle '{role}' n'est pas reconnu",
#             "valid_roles": valid_roles,
#             "suggestion": f"Choisissez parmi: {', '.join(valid_roles)}"
#         }, status=400)

#     # Sauvegarder l'ancien rôle pour référence
#     old_role = user.role
    
#     # Assigner le nouveau rôle
#     user.role = role
#     user.save()

#     # Fonction utilitaire pour formater les infos utilisateur
#     def format_user_info(user_obj):
#         return {
#             "id": user_obj.id,
#             "nom": user_obj.nom,
#             "prenom": user_obj.prenom,
#             "nom_complet": nom_complet(user_obj),
#             "email": user_obj.email,
#             "role": user_obj.role,
#             "matricule": user_obj.matricule,
#             "telephone": user_obj.telephone,
#             "adresse": user_obj.adresse,
#             "poste": user_obj.poste,
#             "date_naissance": user_obj.date_naissance,
#             "sexe": user_obj.sexe,
#             "region_id": user_obj.region_id,
#             "structure_id": user_obj.structure_id,
#             "is_active": user_obj.is_active,
#             "photo_profil": user_obj.photo_profil.url if user_obj.photo_profil else None,
#             "date_joined": user_obj.date_joined.isoformat() if hasattr(user_obj, 'date_joined') else None,
#             "last_login": user_obj.last_login.isoformat() if user_obj.last_login else None
#         }

#     # Cas 5: Assignation agent (avec création automatique)
#     if role == 'agent':
#         try:
#             chef = User.objects.get(role='chef')
#         except User.DoesNotExist:
#             return Response({
#                 "status": "error",
#                 "code": "NO_CHEF_AVAILABLE",
#                 "message": "Aucun chef trouvé dans le système",
#                 "error_details": "Vous devez d'abord assigner un utilisateur comme chef avant de créer des agents",
#                 "suggestion": "Assignez d'abord un rôle 'chef' à un utilisateur existant"
#             }, status=400)

#         # Créer ou mettre à jour l'agent
#         agent, created = Agent.objects.update_or_create(
#             user=user,
#             defaults={'chef': chef}
#         )

#         # Réponse complète pour agent
#         return Response({
#             "status": "success",
#             "code": "AGENT_ASSIGNED",
#             "message": f"{nom_complet(user)} est maintenant agent",
#             "data": {
#                 "user": format_user_info(user),
#                 "agent": {
#                     "id": agent.id,
#                     "created": created,
#                     "chef": format_user_info(chef)
#                 },
#                 "previous_role": old_role,
#                 "new_role": role,
#                 "assignee": format_user_info(request.user),
#                 "timestamp": datetime.now().isoformat()
#             }
#         })

#     # Cas 6: Assignation admin ou chef (succès standard)
#     return Response({
#         "status": "success",
#         "code": "ROLE_ASSIGNED",
#         "message": f"Rôle {role} attribué à {nom_complet(user)}",
#         "data": {
#             "user": format_user_info(user),
#             "previous_role": old_role,
#             "new_role": role,
#             "assignee": format_user_info(request.user),
#             "timestamp": datetime.now().isoformat()
#         }
#     })
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_assign_role(request):
    # Cas 1: Non admin
    if request.user.role != 'admin':
        return Response({
            "status": "error",
            "code": "FORBIDDEN",
            "message": "Accès admin uniquement",
            "error_details": "Votre rôle actuel ne vous permet pas d'assigner des rôles"
        }, status=403)

    user_id = request.data.get('user_id')
    role = request.data.get('role')

    # Cas 2: Champs manquants
    if not user_id or not role:
        missing_fields = []
        if not user_id: missing_fields.append('user_id')
        if not role: missing_fields.append('role')
        
        return Response({
            "status": "error",
            "code": "MISSING_FIELDS",
            "message": "Champs obligatoires manquants",
            "missing_fields": missing_fields,
            "required_fields": ["user_id", "role"]
        }, status=400)

    # Cas 3: Utilisateur non trouvé
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": "Utilisateur non trouvé",
            "error_details": f"Aucun utilisateur avec l'ID {user_id} n'existe"
        }, status=404)

    # ✅ CORRECTION: Liste complète des rôles depuis le modèle
    valid_roles = [role_code for role_code, _ in User.ROLE_CHOICES]
    
    if role not in valid_roles:
        return Response({
            "status": "error",
            "code": "INVALID_ROLE",
            "message": "Rôle invalide",
            "error_details": f"Le rôle '{role}' n'est pas reconnu",
            "valid_roles": valid_roles,
            "valid_roles_display": [display for _, display in User.ROLE_CHOICES],
            "suggestion": f"Choisissez parmi: {', '.join(valid_roles)}"
        }, status=400)

    # Sauvegarder l'ancien rôle pour référence
    old_role = user.role
    
    # Assigner le nouveau rôle
    user.role = role
    user.save()

    # Fonction utilitaire pour formater les infos utilisateur
    def format_user_info(user_obj):
        return {
            "id": user_obj.id,
            "nom": user_obj.nom,
            "prenom": user_obj.prenom,
            "nom_complet": nom_complet(user_obj),
            "email": user_obj.email,
            "role": user_obj.role,
            "role_display": dict(User.ROLE_CHOICES).get(user_obj.role, user_obj.role),
            "matricule": user_obj.matricule,
            "telephone": user_obj.telephone,
            "adresse": user_obj.adresse,
            "poste": user_obj.poste,
            "date_naissance": user_obj.date_naissance,
            "sexe": user_obj.sexe,
            "region_id": user_obj.region_id,
            "structure_id": user_obj.structure_id,
            "is_active": user_obj.is_active,
            "photo_profil": user_obj.photo_profil.url if user_obj.photo_profil else None,
            "date_joined": user_obj.date_joined.isoformat() if hasattr(user_obj, 'date_joined') else None,
            "last_login": user_obj.last_login.isoformat() if user_obj.last_login else None
        }

    # 🔥 Cas spécial: Assignation agent (avec création automatique dans Agent)
    if role == 'agent':
        try:
            # Chercher un chef (peut être n'importe quel utilisateur avec rôle 'chef')
            chef = User.objects.filter(role='chef').first()
            if not chef:
                return Response({
                    "status": "error",
                    "code": "NO_CHEF_AVAILABLE",
                    "message": "Aucun chef trouvé dans le système",
                    "error_details": "Vous devez d'abord assigner un utilisateur comme chef avant de créer des agents",
                    "suggestion": "Assignez d'abord un rôle 'chef' à un utilisateur existant"
                }, status=400)
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "code": "NO_CHEF_AVAILABLE",
                "message": "Aucun chef trouvé dans le système",
                "error_details": "Vous devez d'abord assigner un utilisateur comme chef avant de créer des agents",
                "suggestion": "Assignez d'abord un rôle 'chef' à un utilisateur existant"
            }, status=400)

        # Créer ou mettre à jour l'agent
        agent, created = Agent.objects.update_or_create(
            user=user,
            defaults={'chef': chef}
        )

        # Réponse complète pour agent
        return Response({
            "status": "success",
            "code": "AGENT_ASSIGNED",
            "message": f"{nom_complet(user)} est maintenant agent",
            "data": {
                "user": format_user_info(user),
                "agent": {
                    "id": agent.id,
                    "created": created,
                    "chef": format_user_info(chef)
                },
                "previous_role": old_role,
                "new_role": role,
                "assignee": format_user_info(request.user),
                "timestamp": datetime.now().isoformat()
            }
        })

    # 🔥 Cas spécial: Si on enlève le rôle agent, supprimer de la table Agent
    if old_role == 'agent' and role != 'agent':
        try:
            agent = Agent.objects.get(user=user)
            agent.delete()
        except Agent.DoesNotExist:
            pass

    # Cas 6: Assignation des autres rôles (admin, chef, directeur, etc.)
    return Response({
        "status": "success",
        "code": "ROLE_ASSIGNED",
        "message": f"Rôle {dict(User.ROLE_CHOICES).get(role, role)} attribué à {nom_complet(user)}",
        "data": {
            "user": format_user_info(user),
            "previous_role": old_role,
            "new_role": role,
            "new_role_display": dict(User.ROLE_CHOICES).get(role, role),
            "assignee": format_user_info(request.user),
            "timestamp": datetime.now().isoformat()
        }
    })

# @api_view(['PUT', 'PATCH'])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser, FormParser, JSONParser])
# def api_update_user(request, user_id):
#     if request.user.role != 'admin':
#         return Response({"status": "error", "message": "Accès admin uniquement"}, status=403)

#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

#     data = request.data

#     # 🔥 Tous les champs modifiables directement
#     fields = [
#         'nom', 'prenom', 'email', 'role',
#         'adresse', 'telephone', 'poste',
#         'matricule', 'sexe',
#         'region_id', 'structure_id'
#     ]

#     for field in fields:
#         if field in data:
#             setattr(user, field, data[field])

#     # date_naissance
#     if 'date_naissance' in data and data['date_naissance']:
#         try:
#             user.date_naissance = datetime.strptime(
#                 str(data['date_naissance']).strip(), "%Y-%m-%d"
#             ).date()
#         except ValueError:
#             return Response({
#                 "status": "error",
#                 "message": "Format date invalide (YYYY-MM-DD)"
#             }, status=400)

#     # photo
#     if 'photo_profil' in request.FILES:
#         user.photo_profil = request.FILES['photo_profil']

#     user.save()

#     return Response({
#         "status": "success",
#         "message": "Utilisateur mis à jour",
#         "user": {
#             "id": user.id,
#             "email": user.email,
#             "nom_complet": nom_complet(user),
#             "role": user.role
#         }
#     })
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_update_user(request, user_id):
    # Vérification admin
    if request.user.role != 'admin':
        return Response({
            "status": "error",
            "code": "FORBIDDEN",
            "message": "Accès admin uniquement"
        }, status=403)

    # Récupération de l'utilisateur
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": "Utilisateur non trouvé"
        }, status=404)

    # Fonction pour formater les infos utilisateur
    def format_user_info(user_obj):
        return {
            "id": user_obj.id,
            "nom": user_obj.nom,
            "prenom": user_obj.prenom,
            "nom_complet": nom_complet(user_obj),
            "email": user_obj.email,
            "role": user_obj.role,
            "adresse": user_obj.adresse,
            "telephone": user_obj.telephone,
            "poste": user_obj.poste,
            "matricule": user_obj.matricule,
            "sexe": user_obj.sexe,
            "date_naissance": user_obj.date_naissance.isoformat() if user_obj.date_naissance else None,
            "region_id": user_obj.region_id,
            "structure_id": user_obj.structure_id,
            "is_active": user_obj.is_active,
            "photo_profil": user_obj.photo_profil.url if user_obj.photo_profil else None,
            "date_joined": user_obj.date_joined.isoformat() if hasattr(user_obj, 'date_joined') and user_obj.date_joined else None,
            "last_login": user_obj.last_login.isoformat() if user_obj.last_login else None
        }

    # 📊 AVANT MODIFICATION - Sauvegarder l'état original
    user_before = format_user_info(user)
    
    data = request.data
    
    # Liste des modifications effectuées
    modifications = []
    
    # 🔥 TRAITEMENT DU RÔLE (avec possibilité de null)
    if 'role' in data:
        role_value = data['role']
        
        # Autoriser null, None, ou chaîne vide
        if role_value is None or role_value == '' or (isinstance(role_value, str) and role_value.lower() == 'null'):
            user.role = None
            modifications.append(f"role: {user_before['role']} → null")
        elif role_value in ['admin', 'chef', 'agent']:
            user.role = role_value
            modifications.append(f"role: {user_before['role']} → {role_value}")
        else:
            return Response({
                "status": "error",
                "code": "INVALID_ROLE",
                "message": f"Rôle invalide: {role_value}",
                "valid_roles": ['admin', 'chef', 'agent', 'null'],
                "suggestion": "Choisissez parmi: admin, chef, agent, ou null"
            }, status=400)

    # 🔥 TRAITEMENT DES AUTRES CHAMPS
    fields = ['nom', 'prenom', 'email', 'adresse', 'telephone', 'poste', 'matricule', 'sexe', 'region_id', 'structure_id']
    
    for field in fields:
        if field in data:
            old_value = getattr(user, field)
            new_value = data[field]
            
            # Nettoyer les valeurs vides
            if new_value == '' or new_value == 'null':
                new_value = None
            
            setattr(user, field, new_value)
            modifications.append(f"{field}: {old_value} → {new_value}")

    # 🔥 TRAITEMENT DE LA DATE DE NAISSANCE
    if 'date_naissance' in data:
        date_value = data['date_naissance']
        old_date = user.date_naissance
        
        if date_value is None or date_value == '' or date_value == 'null':
            user.date_naissance = None
            modifications.append(f"date_naissance: {old_date} → null")
        elif date_value:
            try:
                user.date_naissance = datetime.strptime(str(date_value).strip(), "%Y-%m-%d").date()
                modifications.append(f"date_naissance: {old_date} → {user.date_naissance}")
            except ValueError:
                return Response({
                    "status": "error",
                    "code": "INVALID_DATE_FORMAT",
                    "message": "Format date invalide. Utilisez YYYY-MM-DD"
                }, status=400)

    # 🔥 TRAITEMENT DE LA PHOTO
    photo_updated = False
    if 'photo_profil' in request.FILES:
        old_photo = user.photo_profil.url if user.photo_profil else None
        user.photo_profil = request.FILES['photo_profil']
        photo_updated = True
        modifications.append(f"photo_profil: {old_photo} → {user.photo_profil.url if user.photo_profil else 'nouvelle photo'}")

    # Sauvegarder l'utilisateur
    user.save()
    
    # 📊 APRÈS MODIFICATION - État après mise à jour
    user_after = format_user_info(user)

    # Réponse complète
    return Response({
        "status": "success",
        "code": "USER_UPDATED",
        "message": "Utilisateur mis à jour avec succès",
        "summary": {
            "modified_fields_count": len(modifications),
            "modifications": modifications,
            "photo_updated": photo_updated
        },
        "before": user_before,
        "after": user_after,
        "metadata": {
            "updated_by": {
                "id": request.user.id,
                "nom_complet": nom_complet(request.user),
                "role": request.user.role
            },
            "timestamp": datetime.now().isoformat(),
            "method": request.method
        }
    })
# ==========================
# LIST USERS
# ==========================
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def api_list_users(request):
#     if request.user.role != 'admin':
#         return Response({"status": "error", "message": "Accès admin uniquement"}, status=403)

#     users = User.objects.all().order_by('nom')

#     data = []
#     for u in users:
#         entry = {
#             "id": u.id,
#             "email": u.email,
#             "nom_complet": nom_complet(u),
#             "role": u.role,
#         }

#         if u.role == 'agent':
#             try:
#                 ag = u.agent_profile
#                 entry["chef"] = nom_complet(ag.chef)
#             except:
#                 entry["chef"] = None

#         data.append(entry)

#     return Response({"status": "success", "users": data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_list_users(request):
    if request.user.role != 'admin':
        return Response({"status": "error", "message": "Accès admin uniquement"}, status=403)

    # Exclure les admins de la liste
    users = User.objects.exclude(role='admin').order_by('nom')

    data = []
    for u in users:
        # Toutes les infos de l'utilisateur
        entry = {
            "id": u.id,
            "email": u.email,
            "nom": u.nom,
            "prenom": u.prenom,
            "nom_complet": f"{u.prenom} {u.nom}",
            "role": u.role,
            "role_display": dict(User.ROLE_CHOICES).get(u.role, u.role),
            "matricule": u.matricule,
            "telephone": u.telephone,
            "adresse": u.adresse,
            "poste": u.poste,
            "sexe": u.sexe,
            "sexe_display": dict(User.SEXE_CHOICES).get(u.sexe, u.sexe),
            "date_naissance": u.date_naissance,
            "region_id": u.region_id,
            "structure_id": u.structure_id,
            "is_active": u.is_active,
            "is_staff": u.is_staff,
            "is_superuser": u.is_superuser,
            "photo_profil": u.photo_profil.url if u.photo_profil else None,
            "last_login": u.last_login,
        }

        # Si c'est un chef, afficher tous ses agents
        if u.role == 'chef':
            agents_list = Agent.objects.filter(chef=u).select_related('user')
            entry["members"] = [
                {
                    "id": agent.user.id,
                    "nom": agent.user.nom,
                    "prenom": agent.user.prenom,
                    "nom_complet": f"{agent.user.prenom} {agent.user.nom}",
                    "email": agent.user.email,
                    "matricule": agent.user.matricule,
                    "telephone": agent.user.telephone,
                    "poste": agent.user.poste,
                    "role": agent.user.role,
                    "role_display": dict(User.ROLE_CHOICES).get(agent.user.role, agent.user.role),
                    "sexe": agent.user.sexe,
                    "date_naissance": agent.user.date_naissance,
                    "photo_profil": agent.user.photo_profil.url if agent.user.photo_profil else None,
                    "date_affectation": agent.date_affectation,
                    "is_active": agent.user.is_active,
                }
                for agent in agents_list
            ]
            entry["members_count"] = len(agents_list)

        # Si c'est un agent, afficher son chef
        if u.role == 'agent':
            try:
                agent = u.agent_profile
                if agent.chef:
                    entry["chef"] = {
                        "id": agent.chef.id,
                        "nom": agent.chef.nom,
                        "prenom": agent.chef.prenom,
                        "nom_complet": f"{agent.chef.prenom} {agent.chef.nom}",
                        "email": agent.chef.email,
                        "role": agent.chef.role,
                        "role_display": dict(User.ROLE_CHOICES).get(agent.chef.role, agent.chef.role),
                        "matricule": agent.chef.matricule,
                        "telephone": agent.chef.telephone,
                        "poste": agent.chef.poste,
                        "photo_profil": agent.chef.photo_profil.url if agent.chef.photo_profil else None,
                    }
                    entry["date_affectation"] = agent.date_affectation
                else:
                    entry["chef"] = None
                    entry["date_affectation"] = None
            except:
                entry["chef"] = None
                entry["date_affectation"] = None

        data.append(entry)

    return Response({
        "status": "success",
        "count": len(data),
        "total_users": User.objects.exclude(role='admin').count(),
        "users": data
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_list_all_users(request):
    
    # 🔐 You can control access here
    if request.user.role != 'admin':
        return Response({
            "status": "error",
            "message": "Accès admin uniquement"
        }, status=403)

    users = User.objects.all().order_by('nom')  # ✅ includes admin

    data = []
    for u in users:
        entry = {
            "id": u.id,
            "email": u.email,
            "nom": u.nom,
            "prenom": u.prenom,
            "nom_complet": f"{u.prenom} {u.nom}",
            "role": u.role,
            "role_display": dict(User.ROLE_CHOICES).get(u.role, u.role),
            "matricule": u.matricule,
            "telephone": u.telephone,
            "poste": u.poste,
            "region_id": u.region_id,
            "structure_id": u.structure_id,
            "is_active": u.is_active,
            "is_superuser": u.is_superuser,
            "photo_profil": u.photo_profil.url if u.photo_profil else None,
        }

        # 🔹 Chef → agents
        if u.role == 'chef':
            agents = Agent.objects.filter(chef=u).select_related('user')
            entry["members_count"] = agents.count()

        # 🔹 Agent → chef
        if u.role == 'agent':
            agent = getattr(u, "agent_profile", None)
            entry["chef_id"] = agent.chef.id if agent and agent.chef else None

        data.append(entry)

    return Response({
        "status": "success",
        "count": len(data),
        "users": data
    })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_user_by_id(request, user_id):

    try:
        user = User.objects.get(id=user_id)

        return Response({
            "id": user.id,
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom,
            "nom_complet": f"{user.prenom} {user.nom}",
            "role": user.role,
            "role_display": dict(User.ROLE_CHOICES).get(user.role, user.role),

            "region_id": user.region_id,
            "structure_id": user.structure_id,

            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,

            "photo_profil": user.photo_profil.url if user.photo_profil else None,
        })

    except User.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Utilisateur introuvable"
        }, status=404)
# ==========================
# GET USER
# ==========================
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def api_get_user(request, user_id):
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

#     return Response({
#         "status": "success",
#         "user": {
#             "id": user.id,
#             "email": user.email,
#             "nom_complet": nom_complet(user),
#             "role": user.role,
#         }
#     })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "error", 
            "code": "USER_NOT_FOUND",
            "message": f"Utilisateur avec l'ID {user_id} non trouvé"
        }, status=404)

    # Vérification des droits (admin ou l'utilisateur lui-même)
    if request.user.role != 'admin' and request.user.id != user.id:
        return Response({
            "status": "error",
            "code": "FORBIDDEN",
            "message": "Vous n'avez pas accès à ces informations",
            "details": "Seul l'admin ou l'utilisateur lui-même peut voir ce profil"
        }, status=403)

    # Fonction pour formater la date
    def format_date(date_obj):
        return date_obj.isoformat() if date_obj else None

    # Construction de la réponse complète
    user_data = {
        # === INFORMATIONS DE BASE ===
        "id": user.id,
        "email": user.email,
        "nom": user.nom,
        "prenom": user.prenom,
        "nom_complet": f"{user.prenom} {user.nom}",
        
        # === RÔLE ET PERMISSIONS ===
        "role": user.role,
        "role_display": dict(User.ROLE_CHOICES).get(user.role, "Non défini"),
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        
        # === INFORMATIONS PROFESSIONNELLES ===
        "matricule": user.matricule,
        "poste": user.poste,
        "telephone": user.telephone,
        "adresse": user.adresse,
        
        # === INFORMATIONS PERSONNELLES ===
        "sexe": user.sexe,
        "sexe_display": dict(User.SEXE_CHOICES).get(user.sexe, "Non spécifié"),
        "date_naissance": format_date(user.date_naissance),
        "age": None,
        
        # === LOCALISATION ===
        "region_id": user.region_id,
        "structure_id": user.structure_id,
        
        # === MÉDIAS ===
        "photo_profil": user.photo_profil.url if user.photo_profil else None,
        
        # === DATES SYSTÈME ===
        "last_login": format_date(user.last_login),
        "date_joined": format_date(getattr(user, 'date_joined', None)),
        
        # === GROUPES ET PERMISSIONS ===
        "groups": list(user.groups.values('id', 'name')),
        "user_permissions": list(user.user_permissions.values('id', 'codename', 'name')),
        
        # === STATISTIQUES DU COMPTE ===
        "account_stats": {
            "has_photo": user.photo_profil is not None,
            "has_matricule": user.matricule is not None,
            "has_telephone": user.telephone is not None,
            "has_adresse": user.adresse is not None,
            "profile_complete": all([
                user.nom, user.prenom, user.email,
                user.telephone, user.adresse, user.matricule
            ])
        }
    }
    
    # Calcul de l'âge
    if user.date_naissance:
        from datetime import date
        today = date.today()
        age = today.year - user.date_naissance.year
        if (today.month, today.day) < (user.date_naissance.month, user.date_naissance.day):
            age -= 1
        user_data["age"] = age
    
    # === SI L'UTILISATEUR EST UN CHEF ===
    if user.role == 'chef':
        agents_list = Agent.objects.filter(chef=user).select_related('user')
        
        user_data["chef_info"] = {
            "is_chef": True,
            "total_agents": agents_list.count(),
            "agents": [
                {
                    "id": agent.user.id,
                    "nom": agent.user.nom,
                    "prenom": agent.user.prenom,
                    "nom_complet": f"{agent.user.prenom} {agent.user.nom}",
                    "email": agent.user.email,
                    "matricule": agent.user.matricule,
                    "telephone": agent.user.telephone,
                    "poste": agent.user.poste,
                    "role": agent.user.role,
                    "role_display": dict(User.ROLE_CHOICES).get(agent.user.role, agent.user.role),
                    "photo_profil": agent.user.photo_profil.url if agent.user.photo_profil else None,
                    "date_affectation": format_date(agent.date_affectation),
                    "is_active": agent.user.is_active,
                    "last_login": format_date(agent.user.last_login),
                }
                for agent in agents_list
            ]
        }
    
    # === SI L'UTILISATEUR EST UN AGENT ===
    elif user.role == 'agent':
        try:
            agent = user.agent_profile
            user_data["agent_info"] = {
                "is_agent": True,
                "date_affectation": format_date(agent.date_affectation),
                "chef": {
                    "id": agent.chef.id if agent.chef else None,
                    "nom": agent.chef.nom if agent.chef else None,
                    "prenom": agent.chef.prenom if agent.chef else None,
                    "nom_complet": f"{agent.chef.prenom} {agent.chef.nom}" if agent.chef else None,
                    "email": agent.chef.email if agent.chef else None,
                    "role": agent.chef.role if agent.chef else None,
                    "role_display": dict(User.ROLE_CHOICES).get(agent.chef.role, "Non défini") if agent.chef else None,
                    "matricule": agent.chef.matricule if agent.chef else None,
                    "telephone": agent.chef.telephone if agent.chef else None,
                    "poste": agent.chef.poste if agent.chef else None,
                    "photo_profil": agent.chef.photo_profil.url if agent.chef and agent.chef.photo_profil else None,
                }
            }
        except:
            user_data["agent_info"] = {
                "is_agent": True,
                "error": "Profil agent incomplet",
                "date_affectation": None,
                "chef": None
            }
    
    # === SI L'UTILISATEUR EST UN ADMIN ===
    elif user.role == 'admin':
        user_data["admin_info"] = {
            "is_admin": True,
            "has_full_access": user.is_superuser,
            "can_manage_users": True,
            "can_manage_roles": True
        }
    
    # === AUTRES RÔLES ===
    else:
        user_data["other_info"] = {
            "role_type": user.role or "Non assigné",
            "needs_role_assignment": user.role is None
        }

    return Response({
        "status": "success",
        "code": "USER_FOUND",
        "message": f"Profil de {user_data['nom_complet']} récupéré avec succès",
        "user": user_data,
        "request_metadata": {
            "requested_by": {
                "id": request.user.id,
                "nom_complet": f"{request.user.prenom} {request.user.nom}",
                "role": request.user.role
            },
            "timestamp": datetime.now().isoformat(),
            "user_id_requested": user_id
        }
    })
# ==========================
# DELETE USER
# ==========================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_user(request, user_id):
    if request.user.role != 'admin':
        return Response({"status": "error", "message": "Accès admin uniquement"}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

    name = nom_complet(user)
    user.delete()

    return Response({
        "status": "success",
        "message": f"{name} supprimé"
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_me(request):
    user = request.user
    return Response({
        'id': user.id,
        'email': user.email,
        'role': getattr(user, 'role', None),
        'nom_complet': f"{user.prenom} {user.nom}",
        'region_id':    str(user.region_id)    if user.region_id    else None,
        'structure_id': str(user.structure_id) if user.structure_id else None,
        'is_active': user.is_active,
    })

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
import requests
from .discovery import discover_service
discover_service.cache_clear()

SERVICE_NAME = "SERVICE-NODE-PARAM"

def get_auth_headers(request):
    token = request.headers.get('Authorization')
    if not token:
        return None
    return {"Authorization": token}

@api_view(['PATCH'])
def api_affecter_region(request, user_id):

    # 🔒 Vérifier rôle
    #doit etre chef
    if request.user.role != 'admin':
        return Response({"error": "Seul un admin peut affecter une région."}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Utilisateur introuvable."}, status=404)

    if user.role != 'directeur_region':
        return Response({"error": "Cible doit être directeur_region."}, status=400)

    # 🔒 empêcher double affectation
    if user.region_id:
        return Response({"error": "Ce directeur a déjà une région."}, status=400)

    region_id = request.data.get('region_id')
    if not region_id:
        return Response({"error": "region_id obligatoire."}, status=400)

    # 🔐 récupérer token
    headers = get_auth_headers(request)
    if not headers:
        return Response({"error": "Token manquant."}, status=401)

    try:
        base_url = discover_service(SERVICE_NAME)
        url = f"{base_url}/params/regions/id/{region_id}"

        resp = requests.get(url, headers=headers, timeout=3)

        print("URL =", url)
        print("STATUS =", resp.status_code)
        print("BODY =", resp.text)

        if resp.status_code == 404:
            return Response({"error": "Région introuvable."}, status=404)

        if resp.status_code != 200:
            return Response({
                "error": "Erreur service région",
                "details": resp.text
            }, status=502)

        region = resp.json().get('data', {})

        if not region.get('is_active', True):
            return Response({"error": "Région inactive."}, status=400)

    except requests.exceptions.RequestException:
        return Response({"error": "Service région indisponible."}, status=503)

    # ✅ Affectation
    user.region_id = region_id
    user.structure_id = None
    user.save()

    return Response({
        "status": "success",
        "message": f"Directeur affecté à la région {region.get('nom_region')}",
        "user": UserSerializer(user).data
    })
@api_view(['PATCH'])
def api_affecter_structure(request, user_id):

    # 🔒 seul directeur peut affecter
    if request.user.role != 'directeur_region':
        return Response({"error": "Seul un directeur_region peut affecter une structure."}, status=403)

    # 🔒 directeur doit avoir une région
    if not request.user.region_id:
        return Response({"error": "Vous devez être affecté à une région d'abord."}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Utilisateur introuvable."}, status=404)

    if user.role != 'responsable_structure':
        return Response({"error": "Cible doit être responsable_structure."}, status=400)

    # 🔒 empêcher double affectation
    if user.structure_id:
        return Response({"error": "Ce responsable a déjà une structure."}, status=400)

    structure_id = request.data.get('structure_id')
    if not structure_id:
        return Response({"error": "structure_id obligatoire."}, status=400)

    region_id = request.user.region_id  # 🔥 IMPORTANT (hérité du directeur)

    # 🔐 récupérer token
    headers = get_auth_headers(request)
    if not headers:
        return Response({"error": "Token manquant."}, status=401)

    try:
        base_url = discover_service(SERVICE_NAME)

        # 🔎 Vérifier structure
        url_structure = f"{base_url}/params/structures/{structure_id}"
        resp_s = requests.get(url_structure, headers=headers, timeout=3)

        print("STRUCTURE URL =", url_structure)
        print("STATUS =", resp_s.status_code)
        print("BODY =", resp_s.text)

        if resp_s.status_code == 404:
            return Response({"error": "Structure introuvable."}, status=404)

        if resp_s.status_code != 200:
            return Response({
                "error": "Erreur service structure",
                "details": resp_s.text
            }, status=502)

        structure = resp_s.json().get('data', {})

        # 🔥 Vérifier région correspondante
        structure_region_id = structure.get('region', {}).get('_id')

        if str(structure_region_id) != str(region_id):
            return Response({
                "error": "Structure hors de votre région.",
                "directeur_region": region_id,
                "structure_region": structure_region_id
            }, status=400)
            

        if not structure.get('is_active', True):
            return Response({"error": "Structure inactive."}, status=400)

    except requests.exceptions.RequestException:
        return Response({"error": "Service structure indisponible."}, status=503)

    # ✅ Affectation
    user.region_id = region_id
    user.structure_id = structure_id
    user.save()

    return Response({
        "status": "success",
        "message": "Responsable affecté avec succès.",
        "user": UserSerializer(user).data
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_list_responsables_structure(request):
    users = User.objects.filter(role='responsable_structure')
    data = [{
        "id": u.id,
        "email": u.email,
        "nom_complet": nom_complet(u),
        "role": u.role,
        "region_id": str(u.region_id) if u.region_id else None,
        "structure_id": str(u.structure_id) if u.structure_id else None,
        "photo_profil": u.photo_profil.url if u.photo_profil else None,
        "is_active": u.is_active,
    } for u in users]

    return Response({"status": "success", "count": len(data), "users": data})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_list_responsables_structure_affectes(request):
    users = User.objects.filter(role='responsable_structure', structure_id__isnull=False)
    data = [{
        "id": u.id,
        "email": u.email,
        "nom_complet": nom_complet(u),
        "role": u.role,
        "region_id": str(u.region_id) if u.region_id else None,
        "structure_id": str(u.structure_id) if u.structure_id else None,
        "photo_profil": u.photo_profil.url if u.photo_profil else None,
        "is_active": u.is_active,
    } for u in users]

    return Response({"status": "success", "count": len(data), "users": data})