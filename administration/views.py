from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Departement, Filiere, Enseignant, Etudiant, Salle, Inscription
from pedagogie.models import Note, Absence
from examens.models import SessionExamen

@login_required
def dashboard(request):
    stats = {
        'nb_etudiants': Etudiant.objects.filter(statut='inscrit').count(),
        'nb_enseignants': Enseignant.objects.count(),
        'nb_filieres': Filiere.objects.count(),
        'nb_inscriptions': Inscription.objects.filter(valide=True).count(),
    }
    dept_stats = Departement.objects.annotate(nb_filieres=Count('filieres')).all()
    sessions_recentes = SessionExamen.objects.order_by('-date_debut')[:3]
    return render(request, 'administration/dashboard.html', {
        'stats': stats,
        'dept_stats': dept_stats,
        'sessions': sessions_recentes,
    })

@login_required
def liste_etudiants(request):
    query = request.GET.get('q', '')
    filiere_id = request.GET.get('filiere', '')
    etudiants = Etudiant.objects.select_related('user', 'filiere').all()
    if query:
        etudiants = (etudiants.filter(user__last_name__icontains=query) |
                     etudiants.filter(user__first_name__icontains=query) |
                     etudiants.filter(numero_etudiant__icontains=query))
    if filiere_id:
        etudiants = etudiants.filter(filiere_id=filiere_id)
    return render(request, 'administration/etudiants/liste.html', {
        'etudiants': etudiants, 'filieres': Filiere.objects.all(), 'query': query,
    })

@login_required
def ajouter_etudiant(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if request.method == 'POST':
        try:
            user = User.objects.create_user(
                username=request.POST['numero'],
                email=request.POST.get('email', ''),
                password=request.POST['numero'],
                first_name=request.POST['prenom'],
                last_name=request.POST['nom'],
                role='etudiant',
            )
            Etudiant.objects.create(
                user=user,
                numero_etudiant=request.POST['numero'],
                cin=request.POST.get('cin', ''),
                filiere_id=request.POST.get('filiere'),
                annee_inscription=request.POST.get('annee_inscription', 2024),
            )
            messages.success(request, f"Étudiant {user.get_full_name()} ajouté!")
            return redirect('administration:liste_etudiants')
        except Exception as e:
            messages.error(request, f"Erreur: {e}")
    return render(request, 'administration/etudiants/ajouter.html',
                  {'filieres': Filiere.objects.all()})

@login_required
def detail_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    notes = Note.objects.filter(etudiant=etudiant).select_related('matiere')
    absences = Absence.objects.filter(etudiant=etudiant)
    return render(request, 'administration/etudiants/detail.html', {
        'etudiant': etudiant, 'notes': notes, 'absences': absences,
    })

@login_required
def liste_enseignants(request):
    enseignants = Enseignant.objects.select_related('user', 'departement').all()
    return render(request, 'administration/enseignants/liste.html',
                  {'enseignants': enseignants})

@login_required
def ajouter_enseignant(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if request.method == 'POST':
        try:
            user = User.objects.create_user(
                username=request.POST['matricule'],
                email=request.POST.get('email', ''),
                password=request.POST['matricule'],
                first_name=request.POST['prenom'],
                last_name=request.POST['nom'],
                role='enseignant',
            )
            Enseignant.objects.create(
                user=user,
                matricule=request.POST['matricule'],
                departement_id=request.POST.get('departement'),
                grade=request.POST.get('grade', 'assistant'),
                specialite=request.POST.get('specialite', ''),
            )
            messages.success(request, "Enseignant ajouté avec succès!")
            return redirect('administration:liste_enseignants')
        except Exception as e:
            messages.error(request, f"Erreur: {e}")
    return render(request, 'administration/enseignants/ajouter.html', {
        'departements': Departement.objects.all(),
        'grades': Enseignant.GRADE_CHOICES,
    })

@login_required
def detail_enseignant(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    return render(request, 'administration/enseignants/detail.html',
                  {'enseignant': enseignant})

@login_required
def gestion_inscriptions(request):
    inscriptions = Inscription.objects.select_related(
        'etudiant__user', 'filiere').order_by('-date_inscription')[:50]
    return render(request, 'administration/inscriptions.html', {
        'inscriptions': inscriptions,
        'etudiants': Etudiant.objects.all(),
        'filieres': Filiere.objects.all(),
    })

@login_required
def gestion_salles(request):
    if request.method == 'POST':
        Salle.objects.create(
            nom=request.POST['nom'],
            type_salle=request.POST['type_salle'],
            capacite=request.POST['capacite'],
            batiment=request.POST.get('batiment', ''),
        )
        messages.success(request, "Salle ajoutée!")
    return render(request, 'administration/salles.html',
                  {'salles': Salle.objects.all()})

@login_required
def releve_notes(request, etudiant_id):
    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)
    notes = Note.objects.filter(etudiant=etudiant).select_related('matiere')\
                        .order_by('semestre', 'matiere__nom')
    matieres_notes = {}
    for note in notes:
        key = (note.semestre, note.matiere.nom)
        if key not in matieres_notes:
            matieres_notes[key] = {
                'matiere': note.matiere, 'semestre': note.semestre, 'notes': []
            }
        matieres_notes[key]['notes'].append(note)
    return render(request, 'administration/releve_notes.html', {
        'etudiant': etudiant, 'matieres_notes': matieres_notes.values(),
    })