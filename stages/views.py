from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DemandeStage, Diplome
from administration.models import Etudiant, Enseignant

@login_required
def liste_demandes(request):
    if hasattr(request.user, 'etudiant_profile'):
        demandes = DemandeStage.objects.filter(etudiant=request.user.etudiant_profile)
    else:
        demandes = DemandeStage.objects.select_related('etudiant__user').all()
    return render(request, 'stages/liste.html', {'demandes': demandes})

@login_required
def nouvelle_demande(request):
    if request.method == 'POST':
        etudiant = getattr(request.user, 'etudiant_profile', None)
        if not etudiant:
            messages.error(request, "Profil étudiant non trouvé.")
            return redirect('stages:demandes')
        DemandeStage.objects.create(
            etudiant=etudiant,
            type_stage=request.POST['type_stage'],
            entreprise=request.POST['entreprise'],
            sujet=request.POST['sujet'],
            description=request.POST.get('description', ''),
            date_debut=request.POST['date_debut'],
            date_fin=request.POST['date_fin'],
        )
        messages.success(request, "Demande de stage soumise!")
        return redirect('stages:demandes')
    return render(request, 'stages/nouvelle_demande.html')

@login_required
def detail_demande(request, pk):
    demande = get_object_or_404(DemandeStage, pk=pk)
    if request.method == 'POST' and request.user.is_admin_staff:
        demande.statut = request.POST.get('statut', demande.statut)
        demande.encadrant_fsb_id = request.POST.get('encadrant') or None
        demande.save()
        messages.success(request, "Demande mise à jour!")
    return render(request, 'stages/detail.html', {
        'demande': demande, 'enseignants': Enseignant.objects.all(),
    })

@login_required
def liste_diplomes(request):
    return render(request, 'stages/diplomes.html',
                  {'diplomes': Diplome.objects.select_related('etudiant__user').all()})