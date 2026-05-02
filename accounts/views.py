from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        return redirect('administration:dashboard')
    return redirect('accounts:login')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})