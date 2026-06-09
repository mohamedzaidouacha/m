# pyrefly: ignore [missing-import]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('<int:club_id>/', views.club_detail, name='club_detail'),
    path('<int:club_id>/apply/', views.apply_to_club, name='apply_to_club'),
    path('<int:club_id>/manage/', views.manage_adhesions, name='manage_adhesions'),
    path('<int:club_id>/members/', views.club_members, name='club_members'),
    path('adhesion/<int:adhesion_id>/approve/', views.approve_adhesion, name='approve_adhesion'),
    path('adhesion/<int:adhesion_id>/reject/', views.reject_adhesion, name='reject_adhesion'),
    path('adhesion/<int:adhesion_id>/remove/', views.remove_member, name='remove_member'),
    path('create/', views.create_club, name='create_club'),
    path('<int:club_id>/edit/', views.edit_club, name='edit_club'),
    path('<int:club_id>/validate/', views.validate_club, name='validate_club'),
    path('<int:club_id>/delete/', views.delete_club, name='delete_club'),
]
