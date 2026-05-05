from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model

User = get_user_model()


def home(request):
    if request.user.is_authenticated:
        return redirect('administration:dashboard')
    return redirect('accounts:login')


@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name  = request.POST.get('last_name', user.last_name)
        user.email      = request.POST.get('email', user.email)
        user.telephone  = request.POST.get('telephone', user.telephone)
        user.save()
        from django.contrib import messages
        messages.success(request, "Profil mis à jour !")
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def gestion_agents(request):
    """
    Uniquement accessible aux super_admin : gestion des comptes agents admin.
    """
    if not request.user.is_super_admin:
        from django.contrib import messages
        messages.error(request, "Accès refusé.")
        return redirect('administration:dashboard')

    agents = User.objects.all().order_by('role', 'last_name')

    if request.method == 'POST':
        try:
            u = User.objects.create_user(
                username   = request.POST['username'],
                password   = request.POST['password'],
                first_name = request.POST['first_name'],
                last_name  = request.POST['last_name'],
                email      = request.POST.get('email', ''),
                role       = request.POST.get('role', 'scolarite'),
            )
            u.telephone   = request.POST.get('telephone', '')
            u.departement = request.POST.get('departement', '')
            u.save()
            from django.contrib import messages
            messages.success(request, f"Agent {u.get_full_name()} créé !")
            return redirect('accounts:gestion_agents')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f"Erreur : {e}")

    return render(request, 'accounts/gestion_agents.html', {
        'agents': agents,
        'roles':  User.ROLE_CHOICES,
    })

def logout_view(request):
    auth_logout(request)
    return redirect('accounts:login')