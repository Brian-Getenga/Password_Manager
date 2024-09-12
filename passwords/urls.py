from django.contrib import admin
from django.urls import path
from passwords import views
from .views import profile


urlpatterns = [
    path('passwords', views.password_list, name='password_list'),
    path('create/', views.password_create, name='password_create'),
    path('update/<int:pk>/', views.password_update, name='password_update'),
    path('delete/<int:pk>/', views.password_delete, name='password_delete'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('search/', views.password_search, name='password_search'),
    path('generate/', views.generate_password, name='generate_password'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('', views.file_list, name='file_list'),
    path('upload/', views.upload_file, name='upload_file'),
    path('share/', views.share_file, name='share_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('upgrade-storage/', views.upgrade_storage, name='upgrade_storage'),
    path('files/<int:file_id>/', views.file_detail, name='file_detail'),
    path('files/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('files/<int:file_id>/update/', views.update_file, name='update_file'),
    path('upload/', views.upload_file, name='upload_file'),
    path('edit/<int:file_id>/', views.edit_file, name='edit_file'),
    path('print/<int:file_id>/', views.print_file, name='print_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('file/delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('checkout/<int:package_id>/', views.checkout, name='checkout'),
    path('shared-files/', views.shared_files, name='shared_files'),
     path('files/<int:file_id>/update/', views.update_file, name='update_file'),
]