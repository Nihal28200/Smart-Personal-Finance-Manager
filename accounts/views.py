from django.shortcuts import render, redirect
from django.contrib.auth import login
from core.forms import SignUpForm 

def signup(request):
    """User Registration View"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})