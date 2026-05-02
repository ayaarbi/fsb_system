from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Departement, Filiere, Enseignant, Etudiant, Salle, Inscription
from pedagogie.models import Note, Absence
from examens.models import SessionExamen


# ──────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────
@login_required
def dashboard(request):
    stats = {
        'nb_etudiants':    Etudiant.objects.filter(statut='inscrit').count(),
        'nb_enseignants':  Enseignant.objects.filter(actif=True).count(),
        'nb_filieres':     Filiere.objects.count(),
        'nb_inscriptions': Inscription.objects.filter(valide=True).count(),
    }
    dept_stats       = Departement.objects.annotate(nb_filieres=Count('filieres'))
    sessions_recentes = SessionExamen.objects.order_by('-date_debut')[:3]
    return render(request, 'administration/dashboard.html', {
        'stats':    stats,
        'dept_stats': dept_stats,
        'sessions': sessions_recentes,
    })


# ──────────────────────────────────────────
# ÉTUDIANTS
# ──────────────────────────────────────────
@login_required
def liste_etudiants(request):
    query      = request.GET.get('q', '')
    filiere_id = request.GET.get('filiere', '')
    statut     = request.GET.get('statut', '')

    qs = Etudiant.objects.select_related('filiere').all()
    if query:
        qs = qs.filter(nom__icontains=query) \
             | qs.filter(prenom__icontains=query) \
             | qs.filter(numero_etudiant__icontains=query) \
             | qs.filter(cin__icontains=query)
    if filiere_id:
        qs = qs.filter(filiere_id=filiere_id)
    if statut:
        qs = qs.filter(statut=statut)

    return render(request, 'administration/etudiants/liste.html', {
        'etudiants': qs,
        'filieres':  Filiere.objects.all(),
        'query':     query,
        'statut':    statut,
    })


@login_required
def ajouter_etudiant(request):
    if request.method == 'POST':
        try:
            Etudiant.objects.create(
                prenom            = request.POST['prenom'],
                nom               = request.POST['nom'],
                numero_etudiant   = request.POST['numero'],
                cin               = request.POST.get('cin', ''),
                email             = request.POST.get('email', ''),
                telephone         = request.POST.get('telephone', ''),
                filiere_id        = request.POST.get('filiere') or None,
                annee_inscription = request.POST.get('annee_inscription', 2024),
            )
            messages.success(request, "Étudiant ajouté avec succès !")
            return redirect('administration:liste_etudiants')
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return render(request, 'administration/etudiants/ajouter.html', {
        'filieres': Filiere.objects.all(),
    })


@login_required
def modifier_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    if request.method == 'POST':
        try:
            etudiant.prenom            = request.POST['prenom']
            etudiant.nom               = request.POST['nom']
            etudiant.cin               = request.POST.get('cin', '')
            etudiant.email             = request.POST.get('email', '')
            etudiant.telephone         = request.POST.get('telephone', '')
            etudiant.filiere_id        = request.POST.get('filiere') or None
            etudiant.annee_inscription = request.POST.get('annee_inscription', 2024)
            etudiant.statut            = request.POST.get('statut', 'inscrit')
            etudiant.adresse           = request.POST.get('adresse', '')
            etudiant.save()
            messages.success(request, "Étudiant modifié avec succès !")
            return redirect('administration:detail_etudiant', pk=pk)
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return render(request, 'administration/etudiants/modifier.html', {
        'etudiant': etudiant,
        'filieres': Filiere.objects.all(),
    })


@login_required
def detail_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    notes    = Note.objects.filter(etudiant=etudiant).select_related('matiere')
    absences = Absence.objects.filter(etudiant=etudiant).select_related('seance__matiere')
    stages   = etudiant.stages.all()
    return render(request, 'administration/etudiants/detail.html', {
        'etudiant': etudiant,
        'notes':    notes,
        'absences': absences,
        'stages':   stages,
    })


# ──────────────────────────────────────────
# ENSEIGNANTS
# ──────────────────────────────────────────
@login_required
def liste_enseignants(request):
    query = request.GET.get('q', '')
    dept  = request.GET.get('dept', '')
    qs    = Enseignant.objects.select_related('departement').filter(actif=True)
    if query:
        qs = qs.filter(nom__icontains=query) | qs.filter(prenom__icontains=query) \
             | qs.filter(matricule__icontains=query)
    if dept:
        qs = qs.filter(departement_id=dept)
    return render(request, 'administration/enseignants/liste.html', {
        'enseignants':  qs,
        'departements': Departement.objects.all(),
        'query': query,
    })


@login_required
def ajouter_enseignant(request):
    if request.method == 'POST':
        try:
            Enseignant.objects.create(
                prenom       = request.POST['prenom'],
                nom          = request.POST['nom'],
                matricule    = request.POST['matricule'],
                email        = request.POST.get('email', ''),
                telephone    = request.POST.get('telephone', ''),
                departement_id = request.POST.get('departement') or None,
                grade        = request.POST.get('grade', 'assistant'),
                specialite   = request.POST.get('specialite', ''),
            )
            messages.success(request, "Enseignant ajouté avec succès !")
            return redirect('administration:liste_enseignants')
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return render(request, 'administration/enseignants/ajouter.html', {
        'departements': Departement.objects.all(),
        'grades':       Enseignant.GRADE_CHOICES,
    })


@login_required
def modifier_enseignant(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    if request.method == 'POST':
        try:
            enseignant.prenom        = request.POST['prenom']
            enseignant.nom           = request.POST['nom']
            enseignant.email         = request.POST.get('email', '')
            enseignant.telephone     = request.POST.get('telephone', '')
            enseignant.departement_id= request.POST.get('departement') or None
            enseignant.grade         = request.POST.get('grade', 'assistant')
            enseignant.specialite    = request.POST.get('specialite', '')
            enseignant.actif         = 'actif' in request.POST
            enseignant.save()
            messages.success(request, "Enseignant modifié !")
            return redirect('administration:detail_enseignant', pk=pk)
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return render(request, 'administration/enseignants/modifier.html', {
        'enseignant':   enseignant,
        'departements': Departement.objects.all(),
        'grades':       Enseignant.GRADE_CHOICES,
    })


@login_required
def detail_enseignant(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    return render(request, 'administration/enseignants/detail.html', {
        'enseignant': enseignant,
    })


# ──────────────────────────────────────────
# INSCRIPTIONS
# ──────────────────────────────────────────
@login_required
def gestion_inscriptions(request):
    if request.method == 'POST':
        try:
            ins, created = Inscription.objects.get_or_create(
                etudiant_id         = request.POST['etudiant'],
                annee_universitaire = request.POST['annee_univ'],
                defaults={
                    'filiere_id': request.POST.get('filiere'),
                    'valide':     False,
                }
            )
            if not created:
                messages.warning(request, "L'étudiant est déjà inscrit pour cette année.")
            else:
                messages.success(request, "Inscription enregistrée !")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")

    inscriptions = Inscription.objects.select_related(
        'etudiant', 'filiere').order_by('-date_inscription')
    return render(request, 'administration/inscriptions.html', {
        'inscriptions': inscriptions,
        'etudiants':    Etudiant.objects.filter(statut='inscrit'),
        'filieres':     Filiere.objects.all(),
    })


@login_required
def valider_inscription(request, pk):
    ins = get_object_or_404(Inscription, pk=pk)
    ins.valide = not ins.valide
    ins.save()
    etat = "validée" if ins.valide else "invalidée"
    messages.success(request, f"Inscription {etat}.")
    return redirect('administration:inscriptions')


# ──────────────────────────────────────────
# SALLES
# ──────────────────────────────────────────
@login_required
def gestion_salles(request):
    if request.method == 'POST':
        try:
            Salle.objects.create(
                nom        = request.POST['nom'],
                type_salle = request.POST['type_salle'],
                capacite   = request.POST['capacite'],
                batiment   = request.POST.get('batiment', ''),
            )
            messages.success(request, "Salle ajoutée !")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return render(request, 'administration/salles.html', {
        'salles': Salle.objects.all(),
    })


# ──────────────────────────────────────────
# RELEVÉ DE NOTES
# ──────────────────────────────────────────
@login_required
def releve_notes(request, etudiant_id):
    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)
    notes    = Note.objects.filter(etudiant=etudiant).select_related('matiere') \
                           .order_by('semestre', 'matiere__nom')

    # Regrouper par semestre/matière
    matieres_notes = {}
    for note in notes:
        key = (note.semestre, note.matiere.pk)
        if key not in matieres_notes:
            matieres_notes[key] = {
                'matiere':  note.matiere,
                'semestre': note.semestre,
                'notes':    [],
            }
        matieres_notes[key]['notes'].append(note)

    return render(request, 'administration/releve_notes.html', {
        'etudiant':      etudiant,
        'matieres_notes': matieres_notes.values(),
    })