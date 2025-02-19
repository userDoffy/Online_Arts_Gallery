from sqlite3 import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile  # Import the UserProfile model
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in successfully!')
            return redirect('gallery')  # Redirect normal users to gallery

        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']  # Added
        last_name = request.POST['last_name']  # Added
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        contact = request.POST['contact']
        address = request.POST['address']

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken! Please choose a different one.')
            return redirect('signup')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered! Please use a different email.')
            return redirect('signup')

        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('signup')

        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,  # Added
            last_name=last_name,  # Added
        )

        # Create and update the user's profile
        profile=UserProfile.objects.get(user=user)
        profile.contact = contact
        profile.address = address
        profile.save()

        messages.success(request, 'Signup successful! Please log in.')
        return redirect('login')

    return render(request, 'signup.html')


@login_required(login_url='/auth/login/')
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url='/auth/login/')
def profile_view(request):
    if request.method == 'POST':
        # Update user details
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        # Update user profile details
        profile = user.userprofile
        profile.contact = request.POST.get('contact', profile.contact)
        profile.address = request.POST.get('address', profile.address)
        profile.save()

        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')

    return render(request, 'profile.html', {
        'user': request.user,
        'profile': request.user.userprofile,
    })

