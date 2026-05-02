from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Matiere, EmploiDuTemps, Absence, Note
from administration.models import Etudiant, Enseignant, Filiere


@login_required
def liste_matieres(request):
    filiere_id = request.GET.get('filiere', '')
    qs = Matiere.objects.select_related('filiere').all()
    if filiere_id:
        qs = qs.filter(filiere_id=filiere_id)
    return render(request, 'pedagogie/matieres.html', {
        'matieres': qs,
        'filieres': Filiere.objects.all(),
    })


@login_required
def emploi_du_temps(request):
    filiere_id = request.GET.get('filiere', '')
    qs = EmploiDuTemps.objects.select_related(
        'matiere', 'enseignant', 'salle').all()
    if filiere_id:
        qs = qs.filter(matiere__filiere_id=filiere_id)
    return render(request, 'pedagogie/emploi_du_temps.html', {
        'emploi':    qs,
        'filieres':  Filiere.objects.all(),
        'filiere_id': filiere_id,
    })


@login_required
def gestion_absences(request):
    if request.method == 'POST':
        try:
            _, created = Absence.objects.get_or_create(
                etudiant_id = request.POST['etudiant'],
                seance_id   = request.POST['seance'],
                date        = request.POST['date'],
                defaults    = {
                    'justifiee': request.POST.get('justifiee') == 'on',
                    'motif':     request.POST.get('motif', ''),
                }
            )
            if created:
                messages.success(request, "Absence enregistrée !")
            else:
                messages.warning(request, "Cette absence est déjà enregistrée.")
        except Exception as e:
            messages.error(request, str(e))

    filiere_id = request.GET.get('filiere', '')
    absences   = Absence.objects.select_related(
        'etudiant', 'seance__matiere').order_by('-date')[:100]

    etudiants = Etudiant.objects.filter(statut='inscrit')
    if filiere_id:
        etudiants = etudiants.filter(filiere_id=filiere_id)

    return render(request, 'pedagogie/absences.html', {
        'absences':  absences,
        'seances':   EmploiDuTemps.objects.select_related('matiere').all(),
        'etudiants': etudiants,
        'filieres':  Filiere.objects.all(),
    })


@login_required
def saisie_notes(request):
    if request.method == 'POST':
        try:
            Note.objects.update_or_create(
                etudiant_id         = request.POST['etudiant'],
                matiere_id          = request.POST['matiere'],
                type_note           = request.POST['type_note'],
                annee_universitaire = request.POST['annee_univ'],
                semestre            = request.POST['semestre'],
                defaults={
                    'note':       request.POST['note'],
                    'enseignant_id': request.POST.get('enseignant') or None,
                    'saisie_par': request.user.get_full_name(),
                }
            )
            messages.success(request, "Note enregistrée !")
        except Exception as e:
            messages.error(request, str(e))

    filiere_id = request.GET.get('filiere', '')
    etudiants  = Etudiant.objects.filter(statut='inscrit')
    if filiere_id:
        etudiants = etudiants.filter(filiere_id=filiere_id)

    return render(request, 'pedagogie/saisie_notes.html', {
        'matieres':   Matiere.objects.select_related('filiere').all(),
        'etudiants':  etudiants,
        'enseignants':Enseignant.objects.filter(actif=True),
        'filieres':   Filiere.objects.all(),
    })


@login_required
def liste_notes(request):
    matiere_id = request.GET.get('matiere', '')
    etudiant_id= request.GET.get('etudiant', '')
    qs = Note.objects.select_related('etudiant', 'matiere', 'enseignant').all()
    if matiere_id:
        qs = qs.filter(matiere_id=matiere_id)
    if etudiant_id:
        qs = qs.filter(etudiant_id=etudiant_id)
    return render(request, 'pedagogie/liste_notes.html', {
        'notes':    qs,
        'matieres': Matiere.objects.all(),
    })