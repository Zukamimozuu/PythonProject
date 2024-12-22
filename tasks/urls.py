from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('project/<int:project_id>/add/', views.add_task, name='add_task'),
    path('update_status/<int:task_id>/', views.update_task_status, name='update_status'),

]
