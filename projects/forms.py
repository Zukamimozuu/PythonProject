from django import forms
from .models import Project
from django.core.exceptions import ValidationError
from users.models import User

    
#class ProjectForm(forms.ModelForm):
    #class Meta:
        #model = Project
        #fields = ['project_name', 'description', 'start_date', 'end_date', 'members']
        #widgets = {
            #'start_date': forms.DateInput(attrs={'type': 'date'}),
            #'end_date': forms.DateInput(attrs={'type': 'date'}),
        #}

   # members = forms.ModelMultipleChoiceField(
        #queryset=User.objects.all(),
        #widget=forms.SelectMultiple(attrs={'class': 'form-control'})  # Added a class for styling
    #)

    #def clean_project_name(self):
        #project_name = self.cleaned_data.get('project_name')
        #user = self.instance.created_by  # Assuming 'created_by' is the user who creates the project
        # Check if a project with the same name already exists for this user
        #if Project.objects.filter(project_name=project_name, created_by=user).exists():
            #raise ValidationError(f"A project with the name '{project_name}' already exists.")
        #return project_name




class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'description', 'start_date', 'end_date', 'members']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # Default to none
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check'})
    )

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if current_user:
            # Filter members to show only users created by the current user
            self.fields['members'].queryset = User.objects.filter(created_by=current_user)