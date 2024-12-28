from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
import logging
from .models import User
from projects.models import Project
from .forms import SignupForm, UserProfileForm, UserCreationForm
from .forms import UserUpdateForm

# views.py
@login_required
def update_user(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('users:team_list')
    else:
        form = UserUpdateForm(instance=user)
    
    return render(request, 'users/update_user.html', {'form': form, 'user': user})


def delete_user(request, user_id):
    # Get the user object using the provided user_id
    user = get_object_or_404(User, id=user_id)

    # Check if the user is authorized to delete this user
    if not request.user.is_staff and request.user != user.created_by:
        messages.error(request, "You are not authorized to delete this user.")
        return redirect('users:team_list')

    if request.method == 'POST':
        # Perform the delete operation
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('users:team_list')  # Redirect to the team list page

    # If it's not a POST request, show the confirmation page
    return render(request, 'users/delete_user.html', {'user': user})

@login_required
def create_member(request):
    # Check if the user is a Manager
    if request.user.user_role == 'Manager':
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                # Save the new member, assigning the logged-in user as created_by
                new_user = form.save(commit=False)
                new_user.user_role = 'Member'  # Assign "Member" role automatically
                new_user.created_by = request.user  # Set the manager who created the member
                new_user.save()  # Save the user to the database

                messages.success(request, 'Member created successfully!')
                return redirect('users:team_list')  # Redirect to the team list view
            else:
                # If form is not valid, render the form again with error messages
                messages.error(request, 'Please fix the errors below.')
        else:
            form = UserCreationForm()
        
        return render(request, 'users/create_member.html', {'form': form})
    else:
        messages.error(request, "You do not have permission to create a member.")
        return redirect('users:team_list')


@login_required
def team_list(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Automatically assign 'Member' role to the new user
            user = form.save(commit=False)
            user.user_role = 'Member'  # Ensure the role is set to Member
            user.created_by = request.user  # Set the logged-in user as the creator
            user.save()
            messages.success(request, "New member created successfully!")
            return redirect('users:team_list')  # Redirect to the same page or other as needed
        else:
            messages.error(request, "Error creating member. Please check the form.")

    else:
        form = UserCreationForm()

    # Fetch the users created by the current manager
    users = User.objects.filter(created_by=request.user)
    return render(request, 'users/team_list.html', {'form': form, 'users': users})





logger = logging.getLogger(__name__)

def user_login(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        user = None
        if '@' in username_or_email:  # Check if it's an email
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username  # Get the username from the user object
            except User.DoesNotExist:
                user = None
        else:
            user = User.objects.filter(username=username_or_email).first()
            username = username_or_email  # Directly use the input as username

        if user:
            user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            
            # Check the user's role and redirect to the appropriate dashboard
            if user.user_role == 'Manager':
                return redirect('manager-dashboard')  # Redirect to the manager dashboard
            elif user.user_role == 'Member':
                return redirect('member-dashboard')  # Redirect to the member dashboard
            else:
                messages.error(request, 'You do not have a valid role assigned.')
                return redirect('login')  # Redirect back to the login page if no role
            
        else:
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'users/login.html')


# users/views.py
def register(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Check if the username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        elif form.is_valid():
            form.save()  # Save the user with default 'Manager' role
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('users:login')  # Redirect to the 'login' page after successful registration
    else:
        form = SignupForm()

    return render(request, 'users/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('users:login')  # Use the correct 'users:login' name


@login_required
def profile_view(request):
    print("Profile view accessed")  # Debugging output
    return render(request, 'users/profile.html')

@login_required
def profile_edit(request):
    """Allow the user to update their profile."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')  # Redirect to profile view after saving
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})



@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Update session so the user doesn't get logged out
            update_session_auth_hash(request, form.user)
            return redirect('users:profile')  # Redirect to profile view after password change
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': form})

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('users:team_list')  # Or any other relevant URL
    return render(request, 'users/delete_user_confirm.html')
