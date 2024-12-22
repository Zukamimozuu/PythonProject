from django import forms
from .models import Task
from projects.models import Project
from users.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_name', 'description', 'priority', 'start_date', 'due_date', 'assigned_to']  # Removed 'status'

    # Add a project selection field (hidden)
    project = forms.ModelChoiceField(queryset=Project.objects.all(), widget=forms.HiddenInput())  # Hidden to use in view

    def __init__(self, *args, **kwargs):
        # Accept user and project as parameters
        self.user = kwargs.pop('user', None)  # Pop the 'user' keyword argument
        self.project = kwargs.pop('project', None)  # Pop the project argument
        super().__init__(*args, **kwargs)

        if self.user and self.project:
            # Filter the 'assigned_to' field to show users created by the current logged-in manager
            # and who are also members of the current project
            self.fields['assigned_to'].queryset = User.objects.filter(
                created_by=self.user,
                user_role='Member',
                projects=self.project  # Filter by users who are members of the current project
            )
