from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProjectForm
from .models import Project, ProjectMember
from tasks.models import Task
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import get_user_model
from users.forms import UserCreationForm 
from django.db.models import Avg, Count, Sum
from users.models import User

User = get_user_model()

def project_tasks(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project)

    return render(request, 'projects/project_tasks.html', {
        'project': project,
        'tasks': tasks,
    })

@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            task.status = new_status
            task.save()
            messages.success(request, f'Task status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status.')
        
        return redirect('tasks:project_tasks', project_id=task.project.id)

    return redirect('tasks:project_tasks', project_id=task.project.id)



@login_required
def member_report_view(request):
    # Get the logged-in user
    user = request.user

    # Get all the projects the user is a member of
    projects = Project.objects.filter(members=user)

    # Get tasks assigned to the user in these projects
    tasks = Task.objects.filter(assigned_to=user)

    # Calculate the total progress for each project, and filter out projects with no tasks
    project_progress_data = []

    for project in projects:
        # Filter the tasks for the current project
        project_tasks = tasks.filter(project=project)

        if project_tasks.exists():  # Only process projects that have tasks assigned to the user
            total_progress = sum(task.progress for task in project_tasks) / len(project_tasks) if project_tasks else 0
            project_progress_data.append({
                'project': project,
                'tasks': project_tasks,
                'total_progress': total_progress
            })

    # Context for rendering
    context = {
        'projects': project_progress_data,
    }

    # Render the report in the template
    return render(request, 'projects/member_report.html', context)


def report_view(request):


    # Get projects created by the logged-in manager
    projects = Project.objects.filter(created_by=request.user)

    # Collect data for each project
    project_data = []
    for project in projects:
        # Get all tasks related to the project
        tasks = project.tasks.all()
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='Completed').count()
        pending_tasks = tasks.filter(status='Pending').count()
        in_progress_tasks = tasks.filter(status='In Progress').count()
        average_progress = tasks.aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0

        # Collect each member's progress (the member data is fetched via the many-to-many relationship)
        members_data = []
        for member in project.members.all():
            member_tasks = tasks.filter(assigned_to=member)  # Filter tasks by the member
            member_progress = member_tasks.aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0
            members_data.append({
                'member': member,
                'member_progress': member_progress,
            })

        # Append project-related data
        project_data.append({
            'project': project,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'average_progress': average_progress,
            'members_data': members_data,  # Add members' progress data
            'tasks': tasks,  # Add tasks for Gantt chart generation
        })

    # Prepare context for rendering in the template
    context = {
        'project_data': project_data,
    }

    # Render the report view with the project data context
    return render(request, 'projects/report.html', context)


#def project_tasks(request, project_id):
    # Use filter() to get all projects that match the project_id
    #projects = Project.objects.filter(project_id=project_id)
    
    #if not projects.exists():
        #return render(request, '404.html')  # Optionally return a 404 page if no project is found
    
    # Assuming there is only one project per `project_id` that you want to display tasks for
    #project = projects.first()  # Get the first project or adjust as needed
    
    # Get tasks related to the project
    #tasks = Task.objects.filter(project=project)

    #return render(request, 'projects/projects.html', {'project': project, 'tasks': tasks})


@login_required
def project_tasks(request, project_id):
    # Retrieve the project by primary key
    project = get_object_or_404(Project, pk=project_id)

    # Determine tasks to display based on user's role
    if request.user == project.created_by:
        tasks = Task.objects.filter(project=project)  # All tasks for managers
    else:
        tasks = Task.objects.filter(project=project, assigned_to=request.user)  # User-specific tasks

    # Render the template with project and tasks
    return render(request, 'projects/project_tasks.html', {'project': project, 'tasks': tasks})





@login_required
def your_work(request):
    user = request.user
    tasks = Task.objects.filter(assigned_to=user)  # Filter tasks assigned to the logged-in user
    
    # Get projects that the user is part of (as a member) and projects they created (if user is a manager)
    projects = user.projects.all()  # Projects where the user is a member
    if user.user_role == "Manager":
        # Include projects the manager has created
        created_projects = Project.objects.filter(created_by=user)
        projects = projects | created_projects  # Combine both sets of projects (member + created)
    
    # Remove duplicates by using distinct
    projects = projects.distinct()

    # Debugging: print the projects queryset to check if duplicates are removed
    print("Projects for the user:", projects)

    return render(request, 'projects/your_work.html', {'tasks': tasks, 'projects': projects, 'user': user})








@login_required
def delete_project(request, project_id):
    # Get the project using project_id
    project = get_object_or_404(Project, project_id=project_id)
    
    # Check if the user is the manager (creator) of the project
    if project.created_by != request.user:
        messages.error(request, "You do not have permission to delete this project.")
        return redirect('projects:your_work')

    # Delete the project
    project.delete()
    messages.success(request, "Project deleted successfully!")
    return redirect('projects:your_work')



def starred(request):
    return render(request, 'projects/starred.html', {'title': 'Starred'})

def projects(request):
    return render(request, 'projects/projects.html', {'title': 'Projects'})

def team_list(request):
    return render(request, 'projects/team_list.html', {'title': 'Teams'})


from django.db import IntegrityError

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            # Save the project instance
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()

            # Save many-to-many relationships
            form.save_m2m()

            # Add members to the project, avoiding duplicates
            for member in form.cleaned_data['members']:
                try:
                    ProjectMember.objects.get_or_create(user=member, project=project, defaults={'member_role': "Member"})
                except IntegrityError:
                    # Handle the error gracefully if needed (e.g., log it or ignore duplicates)
                    pass

            # Add a success message
            messages.success(request, "Project created successfully!")
            return redirect('projects:your_work')  # Replace with the correct redirect URL
    else:
        form = ProjectForm(user=request.user)

    return render(request, 'projects/create_project.html', {'form': form})