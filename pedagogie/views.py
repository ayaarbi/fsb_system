from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Matiere, EmploiDuTemps, Absence, Note
from administration.models import Etudiant, Enseignant, Filiere

@login_required
def liste_matieres(request):
    return render(request, 'pedagogie/matieres.html',
                  {'matieres': Matiere.objects.select_related('filiere').all()})

@login_required
def emploi_du_temps(request):
    filiere_id = request.GET.get('filiere')
    emploi = EmploiDuTemps.objects.select_related(
        'matiere', 'enseignant__user', 'salle').all()
    if filiere_id:
        emploi = emploi.filter(matiere__filiere_id=filiere_id)
    return render(request, 'pedagogie/emploi_du_temps.html', {
        'emploi': emploi,
        'jours': range(1, 7),
        'filieres': Filiere.objects.all(),
        'filiere_id': filiere_id,
    })

@login_required
def gestion_absences(request):
    if request.method == 'POST':
        try:
            Absence.objects.get_or_create(
                etudiant_id=request.POST['etudiant'],
                seance_id=request.POST['seance'],
                date=request.POST['date'],
                defaults={'justifiee': False},
            )
            messages.success(request, "Absence enregistrée!")
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'pedagogie/absences.html', {
        'absences': Absence.objects.select_related(
            'etudiant__user', 'seance__matiere').order_by('-date')[:50],
        'seances': EmploiDuTemps.objects.select_related('matiere').all(),
        'etudiants': Etudiant.objects.select_related('user').all(),
    })

@login_required
def saisie_notes(request):
    if request.method == 'POST':
        try:
            Note.objects.update_or_create(
                etudiant_id=request.POST['etudiant'],
                matiere_id=request.POST['matiere'],
                type_note=request.POST['type_note'],
                annee_universitaire=request.POST['annee_univ'],
                semestre=request.POST['semestre'],
                defaults={
                    'note': request.POST['note'],
                    'enseignant_id': request.POST.get('enseignant'),
                },
            )
            messages.success(request, "Note enregistrée!")
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'pedagogie/saisie_notes.html', {
        'matieres': Matiere.objects.all(),
        'etudiants': Etudiant.objects.select_related('user').all(),
        'enseignants': Enseignant.objects.select_related('user').all(),
    })

@login_required
def liste_notes(request):
    matiere_id = request.GET.get('matiere')
    notes = Note.objects.select_related(
        'etudiant__user', 'matiere', 'enseignant__user').all()
    if matiere_id:
        notes = notes.filter(matiere_id=matiere_id)
    return render(request, 'pedagogie/liste_notes.html', {
        'notes': notes, 'matieres': Matiere.objects.all(),
    })