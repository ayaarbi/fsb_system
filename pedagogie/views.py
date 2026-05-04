from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Matiere, EmploiDuTemps, Absence, Note
from administration.models import (
    Departement, Filiere, Etudiant, Enseignant, Classe
)


# ══════════════════════════════════════════
# MATIÈRES — NAVIGATION
# ══════════════════════════════════════════

@login_required
def matieres_departements(request):
    """Étape 1 : choisir un département"""
    departements = Departement.objects.all()
    dept_data = []
    for dept in departements:
        nb = Matiere.objects.filter(filiere__departement=dept).count()
        nb_filieres = Filiere.objects.filter(departement=dept).count()
        dept_data.append({
            'dept':       dept,
            'nb_matieres': nb,
            'nb_filieres': nb_filieres,
        })
    return render(request, 'pedagogie/matieres/nav_departements.html', {
        'dept_data': dept_data,
    })


@login_required
def matieres_filieres(request, dept_id):
    """Étape 2 : choisir une filière"""
    dept    = get_object_or_404(Departement, pk=dept_id)
    filieres = Filiere.objects.filter(departement=dept).order_by('type_formation', 'nom')

    TYPE_LABELS = {
        'licence':  'Licences',
        'master':   'Masters',
        'doctorat': 'Doctorat',
        'cpi':      'CPI',
        'ci':       'CI',
    }
    groupes = {}
    for f in filieres:
        tf  = f.type_formation
        lbl = TYPE_LABELS.get(tf, tf.capitalize())
        if lbl not in groupes:
            groupes[lbl] = []
        nb = Matiere.objects.filter(filiere=f).count()
        groupes[lbl].append({'filiere': f, 'nb_matieres': nb})

    return render(request, 'pedagogie/matieres/nav_filieres.html', {
        'dept':    dept,
        'groupes': groupes,
    })


@login_required
def matieres_liste(request, dept_id, filiere_id):
    """Étape 3 : liste des matières divisées par semestre"""
    dept    = get_object_or_404(Departement, pk=dept_id)
    filiere = get_object_or_404(Filiere, pk=filiere_id)

    matieres_s1 = Matiere.objects.filter(
        filiere=filiere, semestre=1
    ).order_by('nom')
    matieres_s2 = Matiere.objects.filter(
        filiere=filiere, semestre=2
    ).order_by('nom')

    return render(request, 'pedagogie/matieres/liste.html', {
        'dept':        dept,
        'filiere':     filiere,
        'matieres_s1': matieres_s1,
        'matieres_s2': matieres_s2,
    })


@login_required
def ajouter_matiere(request):
    """Ajouter une matière"""
    # Pré-sélection filière si passée en GET
    filiere_id = request.GET.get('filiere') or request.POST.get('filiere')
    dept_id    = request.GET.get('dept')    or request.POST.get('dept')

    if request.method == 'POST':
        try:
            filiere = get_object_or_404(Filiere, pk=request.POST['filiere'])
            Matiere.objects.create(
                nom          = request.POST['nom'],
                code         = request.POST['code'],
                filiere      = filiere,
                semestre     = request.POST['semestre'],
                credits      = request.POST.get('credits', 3),
                coefficient  = request.POST.get('coefficient', 1.0),
                heures_cours = request.POST.get('heures_cours', 0),
                heures_td    = request.POST.get('heures_td', 0),
                heures_tp    = request.POST.get('heures_tp', 0),
            )
            messages.success(request, "Matière ajoutée avec succès !")
            # Rediriger vers la liste de la filière
            dept_id = filiere.departement.pk
            return redirect(
                'pedagogie:matieres_liste', dept_id=dept_id, filiere_id=filiere.pk
            )
        except Exception as e:
            messages.error(request, f"Erreur : {e}")

    filieres    = Filiere.objects.select_related('departement').order_by(
        'departement__nom', 'type_formation', 'nom'
    )
    filiere_sel = None
    if filiere_id:
        try:
            filiere_sel = Filiere.objects.get(pk=filiere_id)
        except Filiere.DoesNotExist:
            pass

    return render(request, 'pedagogie/matieres/ajouter.html', {
        'filieres':    filieres,
        'filiere_sel': filiere_sel,
        'dept_id':     dept_id,
        'departements': Departement.objects.all(),
    })


@login_required
def modifier_matiere(request, pk):
    """Modifier une matière"""
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        try:
            matiere.nom          = request.POST['nom']
            matiere.code         = request.POST['code']
            matiere.filiere_id   = request.POST['filiere']
            matiere.semestre     = request.POST['semestre']
            matiere.credits      = request.POST.get('credits', 3)
            matiere.coefficient  = request.POST.get('coefficient', 1.0)
            matiere.heures_cours = request.POST.get('heures_cours', 0)
            matiere.heures_td    = request.POST.get('heures_td', 0)
            matiere.heures_tp    = request.POST.get('heures_tp', 0)
            matiere.save()
            messages.success(request, "Matière modifiée avec succès !")
            return redirect(
                'pedagogie:matieres_liste',
                dept_id=matiere.filiere.departement.pk,
                filiere_id=matiere.filiere.pk,
            )
        except Exception as e:
            messages.error(request, f"Erreur : {e}")

    filieres = Filiere.objects.select_related('departement').order_by(
        'departement__nom', 'type_formation', 'nom'
    )
    return render(request, 'pedagogie/matieres/modifier.html', {
        'matiere':  matiere,
        'filieres': filieres,
    })


@login_required
def supprimer_matiere(request, pk):
    """Supprimer une matière"""
    matiere = get_object_or_404(Matiere, pk=pk)
    dept_id    = matiere.filiere.departement.pk
    filiere_id = matiere.filiere.pk
    if request.method == 'POST':
        matiere.delete()
        messages.success(request, "Matière supprimée.")
        return redirect(
            'pedagogie:matieres_liste',
            dept_id=dept_id, filiere_id=filiere_id
        )
    return render(request, 'pedagogie/matieres/confirmer_suppression.html', {
        'matiere': matiere,
    })


# ══════════════════════════════════════════
# EMPLOI DU TEMPS
# ══════════════════════════════════════════

@login_required
def emploi_du_temps(request):
    filiere_id = request.GET.get('filiere', '')
    qs = EmploiDuTemps.objects.select_related(
        'matiere', 'enseignant', 'salle'
    ).all()
    if filiere_id:
        qs = qs.filter(matiere__filiere_id=filiere_id)
    return render(request, 'pedagogie/emploi_du_temps.html', {
        'emploi':    qs,
        'filieres':  Filiere.objects.all(),
        'filiere_id': filiere_id,
    })


# ══════════════════════════════════════════
# ABSENCES
# ══════════════════════════════════════════

@login_required
def gestion_absences(request):
    if request.method == 'POST':
        try:
            _, created = Absence.objects.get_or_create(
                etudiant_id = request.POST['etudiant'],
                seance_id   = request.POST['seance'],
                date        = request.POST['date'],
                defaults={
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
        'etudiant', 'seance__matiere'
    ).order_by('-date')[:100]

    etudiants = Etudiant.objects.filter(statut='inscrit')
    if filiere_id:
        etudiants = etudiants.filter(filiere_id=filiere_id)

    return render(request, 'pedagogie/absences.html', {
        'absences':  absences,
        'seances':   EmploiDuTemps.objects.select_related('matiere').all(),
        'etudiants': etudiants,
        'filieres':  Filiere.objects.all(),
    })


# ══════════════════════════════════════════
# NOTES
# ══════════════════════════════════════════

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
                    'note':          request.POST['note'],
                    'enseignant_id': request.POST.get('enseignant') or None,
                    'saisie_par':    request.user.get_full_name(),
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
        'matieres':    Matiere.objects.select_related('filiere').all(),
        'etudiants':   etudiants,
        'enseignants': Enseignant.objects.filter(actif=True),
        'filieres':    Filiere.objects.all(),
    })


@login_required
def liste_notes(request):
    matiere_id  = request.GET.get('matiere', '')
    etudiant_id = request.GET.get('etudiant', '')
    qs = Note.objects.select_related('etudiant', 'matiere', 'enseignant').all()
    if matiere_id:
        qs = qs.filter(matiere_id=matiere_id)
    if etudiant_id:
        qs = qs.filter(etudiant_id=etudiant_id)
    return render(request, 'pedagogie/liste_notes.html', {
        'notes':    qs,
        'matieres': Matiere.objects.all(),
    })