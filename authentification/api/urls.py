
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Auth / Users
    path('login/', views.api_login, name='api_login'),
    path('logout/', views.api_logout, name='api_logout'),
    path('me/', views.api_me, name='api_me'),
    
    # User password management
    path('password/change/', views.api_change_password, name='api_change_password'),
    path('reset-password/', views.api_reset_password, name='reset-password'),
    path('reset-password-confirm/', views.api_reset_password_confirm, name='reset-password-confirm'),

    
    path('users/create/', views.api_create_user, name='api_create_user'),
    path('users/<int:user_id>/', views.api_get_user, name='api_get_user'),
    path('users/<int:user_id>/desactive-user/', views.api_toggle_user_active, name='toggle_user_active'),
    path('users/', views.api_list_users, name='api_list_users'),  
    path('all_users/', views.api_list_all_users, name='api_list_all_users'),
    path('all_users/<int:user_id>/', views.api_get_user_by_id, name='api_get_user_by_id'),     
    path('users/<int:user_id>/', views.api_get_user, name='api_get_user'), 
    path('users/<int:user_id>/update/', views.api_update_user, name='api_update_user'),
    path('users/<int:user_id>/delete/', views.api_delete_user, name='api_delete_user'),  
    path('users/<int:user_id>/affecter-region/',    views.api_affecter_region,    name='affecter-region'),
    path('users/<int:user_id>/affecter-direction/',    views.api_affecter_direction,    name='affecter-direction'),
    
    path('users/<int:user_id>/affecter-structure/', views.api_affecter_structure, name='affecter-structure'),
    path('users/<int:user_id>/affecter-departement/', views.api_affecter_departement, name='affecter-departement'),

    path('users/responsables-structure/', views.api_list_responsables_structure, name='list-responsables-structure'),
    path('users/responsables-structure/affectes/', views.api_list_responsables_structure_affectes, name='list-responsables-affectes'),
    path('users/directeurs-region/', views.api_list_directeurs_region, name='list-directeurs-region'),
    path('users/directeurs-region/affectes/', views.api_list_directeurs_region_affectes, name='list-directeurs-region-affectes'),
    # affectation role
    path('assign-role/',views.api_assign_role,name='api_assign_role'),

]