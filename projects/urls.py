from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('your-work/', views.your_work, name='your_work'),
    path('starred/', views.starred, name='starred'),
    path('create/', views.create_project, name='create_project'),
    path('project/<int:project_id>/tasks/', views.project_tasks, name='project_tasks'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('report/', views.report_view, name='report'),
    path('member-report/', views.member_report_view, name='member-report'),
    path('project/<int:project_id>/tasks/', views.project_tasks, name='project_tasks'),
]
