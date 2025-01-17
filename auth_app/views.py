from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile  # Import the UserProfile model

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in successfully! Please check out our Gallery.')
            return redirect('gallery')  # Or redirect to a gallery page
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
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
        user = User.objects.create_user(username=username, email=email, password=password1)

        # Update the user's profile
        user.userprofile.contact = contact
        user.userprofile.address = address
        user.userprofile.save()

        messages.success(request, 'Signup successful! Please log in.')
        return redirect('login')

    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('home')
