from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DemandeStage, Diplome
from administration.models import Etudiant, Enseignant


@login_required
def liste_demandes(request):
    statut = request.GET.get('statut', '')
    qs     = DemandeStage.objects.select_related('etudiant', 'encadrant_fsb').all()
    if statut:
        qs = qs.filter(statut=statut)
    return render(request, 'stages/liste.html', {
        'demandes': qs,
        'statut':   statut,
    })


@login_required
def nouvelle_demande(request):
    """
    L'agent admin crée la demande AU NOM de l'étudiant.
    """
    if request.method == 'POST':
        try:
            DemandeStage.objects.create(
                etudiant_id  = request.POST['etudiant'],
                type_stage   = request.POST['type_stage'],
                entreprise   = request.POST['entreprise'],
                sujet        = request.POST['sujet'],
                description  = request.POST.get('description', ''),
                date_debut   = request.POST['date_debut'],
                date_fin     = request.POST['date_fin'],
            )
            messages.success(request, "Demande de stage créée !")
            return redirect('stages:demandes')
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return render(request, 'stages/nouvelle_demande.html', {
        'etudiants': Etudiant.objects.filter(statut='inscrit'),
    })


@login_required
def detail_demande(request, pk):
    demande = get_object_or_404(DemandeStage, pk=pk)
    if request.method == 'POST':
        demande.statut               = request.POST.get('statut', demande.statut)
        demande.encadrant_fsb_id     = request.POST.get('encadrant') or None
        demande.commentaire_admin    = request.POST.get('commentaire', '')
        if request.POST.get('note_stage'):
            demande.note_stage       = request.POST['note_stage']
        demande.save()
        messages.success(request, "Demande mise à jour !")
    return render(request, 'stages/detail.html', {
        'demande':     demande,
        'enseignants': Enseignant.objects.filter(actif=True),
    })


@login_required
def liste_diplomes(request):
    qs = Diplome.objects.select_related('etudiant').all()
    return render(request, 'stages/diplomes.html', {'diplomes': qs})


@login_required
def ajouter_diplome(request):
    if request.method == 'POST':
        try:
            Diplome.objects.create(
                etudiant_id      = request.POST['etudiant'],
                type_diplome     = request.POST['type_diplome'],
                specialite       = request.POST['specialite'],
                annee_obtention  = request.POST['annee_obtention'],
                mention          = request.POST.get('mention', ''),
                moyenne_generale = request.POST.get('moyenne') or None,
                numero_diplome   = request.POST['numero_diplome'],
                date_delivrance  = request.POST.get('date_delivrance') or None,
            )
            messages.success(request, "Diplôme enregistré !")
            return redirect('stages:diplomes')
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return render(request, 'stages/ajouter_diplome.html', {
        'etudiants': Etudiant.objects.filter(statut__in=['inscrit','diplome']),
    })