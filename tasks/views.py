from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Task
from .forms import TaskForm
from projects.models import Project
from notifications.models import Notification  # Import the Notification model

def add_task(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user, project=project)  # Pass the user and project to the form
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project  # Assign the task to the selected project
            task.status = 'Pending'  # Set the status to 'Pending' automatically
            task.save()

            # Create a notification for the assigned user
            Notification.objects.create(
                user=task.assigned_to,  # Notify the assigned user
                message=f"You have been assigned a new task: '{task.task_name}' in project '{project.project_name}'.",
            )

            messages.success(request, "Task added successfully!")
            return redirect('projects:project_tasks', project_id=project.project_id)  # Correct namespace for project_tasks
    else:
        form = TaskForm(initial={'project': project}, user=request.user, project=project)  # Pass user and project when initializing the form

    return render(request, 'tasks/add_task.html', {'form': form, 'project': project})


def update_task_status(request, task_id):
    task = get_object_or_404(Task, task_id=task_id)

    if request.user == task.assigned_to:
        if request.method == 'POST':
            new_status = request.POST.get('status')

            if new_status in dict(Task.STATUS_CHOICES).keys():
                task.status = new_status

                # Automatically set the progress based on the status
                if new_status == 'Pending':
                    task.progress = 0.0
                elif new_status == 'In Progress':
                    task.progress = 50.0
                elif new_status == 'Completed':
                    task.progress = 100.0

                task.save()
                messages.success(request, f"Task status updated to {new_status} and progress updated to {task.progress}%.")
            else:
                messages.error(request, "Invalid status.")
        else:
            messages.error(request, "Invalid request method.")
    else:
        messages.error(request, "You are not authorized to update the status of this task.")

    return redirect('projects:project_tasks', project_id=task.project.project_id)  # Adjust based on your primary key



