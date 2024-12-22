from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change_password/', views.change_password, name='change_password'),
    path('delete/', views.delete_user, name='delete_user'),
    path('team_list/', views.team_list, name='team_list'),
    path('create_member/', views.create_member, name='create_member'),
    path('update/<int:user_id>/', views.update_user, name='update_user'),  # Added update_user path
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
]
