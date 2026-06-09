# pyrefly: ignore [missing-import]
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/files/upload/', views.upload_managed_file, name='upload_managed_file'),
    path('dashboard/files/<str:filename>/download/', views.download_managed_file, name='download_managed_file'),
    path('dashboard/files/<str:filename>/delete/', views.delete_managed_file, name='delete_managed_file'),
    path('dashboard/users/', views.admin_users, name='admin_users'),
    path('dashboard/users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
    path('dashboard/users/<int:user_id>/unban/', views.unban_user, name='unban_user'),
    path('account/delete/', views.delete_account, name='delete_account'),
]
