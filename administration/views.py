from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Departement, Filiere, Enseignant, Etudiant, Salle, Inscription, Classe
from pedagogie.models import Note, Absence
from examens.models import SessionExamen
from django.db import models
import qrcode
import io
import base64
from django.http import HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string

# ──────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────
@login_required
def dashboard(request):
    stats = {
        'nb_etudiants':    Etudiant.objects.filter(statut='inscrit').count(),
        'nb_enseignants':  Enseignant.objects.filter(actif=True).count(),
        'nb_filieres':     Filiere.objects.count(),
        'nb_inscriptions': Inscription.objects.filter(statut='valide').count(),
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
# DASHBOARD  
# ──────────────────────────────────────────
@login_required
def dashboard(request):
    from pedagogie.models import Note, Absence
    stats = {
        'nb_etudiants':    Etudiant.objects.filter(statut='inscrit').count(),
        'nb_enseignants':  Enseignant.objects.filter(actif=True).count(),
        'nb_filieres':     Filiere.objects.count(),
        'nb_inscriptions': Inscription.objects.filter(statut='valide').count(),
    }

    # Comptages par type de formation pour les boutons
    formations = {
        'licence':  Filiere.objects.filter(type_formation='licence').count(),
        'master':   Filiere.objects.filter(type_formation='master').count(),
        'doctorat': Filiere.objects.filter(type_formation='doctorat').count(),
        'cpi':      Filiere.objects.filter(type_formation='cpi').count(),
        'ci':       Filiere.objects.filter(type_formation='ci').count(),
    }

    sessions_recentes = SessionExamen.objects.order_by('-date_debut')[:3]

    return render(request, 'administration/dashboard.html', {
        'stats':      stats,
        'formations': formations,
        'sessions':   sessions_recentes,
    })


# ──────────────────────────────────────────
# VUE : Liste des départements pour un type
# ──────────────────────────────────────────
@login_required
def formation_detail(request, type_formation):
    LABELS = {
        'licence':  'Licences',
        'master':   'Masters',
        'doctorat': 'Doctorats',
        'cpi':      'CPI',
        'ci':       'CI',
    }
    label = LABELS.get(type_formation, type_formation.capitalize())

    # Navigation entre les types
    type_list = list(LABELS.items())   # [('licence','Licences'), ...]

    departements = Departement.objects.filter(
        filieres__type_formation=type_formation
    ).distinct()

    dept_data = []
    for dept in departements:
        filieres = Filiere.objects.filter(
            departement=dept, type_formation=type_formation
        )
        nb_etudiants   = Etudiant.objects.filter(
            filiere__in=filieres, statut='inscrit'
        ).count()
        nb_enseignants = Enseignant.objects.filter(
            departement=dept, actif=True
        ).count()
        dept_data.append({
            'dept':           dept,
            'filieres':       filieres,
            'nb_etudiants':   nb_etudiants,
            'nb_enseignants': nb_enseignants,
        })

    return render(request, 'administration/formation_detail.html', {
        'type_formation': type_formation,
        'label':          label,
        'dept_data':      dept_data,
        'type_list':      type_list,
    })

# ──────────────────────────────────────────
# VUE : Détail d'un département
# ──────────────────────────────────────────
@login_required
def departement_detail(request, type_formation, dept_id):
    from django.db import models as django_models
    dept     = get_object_or_404(Departement, pk=dept_id)
    filieres = Filiere.objects.filter(
        departement=dept, type_formation=type_formation
    )
    nb_etudiants  = Etudiant.objects.filter(
        filiere__in=filieres, statut='inscrit'
    ).count()
    nb_enseignants = Enseignant.objects.filter(
        departement=dept, actif=True
    ).count()
    enseignants    = Enseignant.objects.filter(
        departement=dept, actif=True
    ).order_by('grade', 'nom')

    return render(request, 'administration/departement_detail.html', {
        'dept':           dept,
        'type_formation': type_formation,
        'filieres':       filieres,
        'nb_etudiants':   nb_etudiants,
        'nb_enseignants': nb_enseignants,
        'enseignants':    enseignants,
    })


# ──────────────────────────────────────────
# VUE : Détail d'une filière + classes
# ──────────────────────────────────────────
@login_required
def filiere_detail(request, type_formation, dept_id, filiere_id):
    from administration.models import Classe
    filiere       = get_object_or_404(Filiere, pk=filiere_id)
    dept          = get_object_or_404(Departement, pk=dept_id)
    etudiants     = Etudiant.objects.filter(
        filiere=filiere, statut='inscrit'
    ).order_by('nom')
    nb_enseignants = Enseignant.objects.filter(
        departement=filiere.departement, actif=True
    ).count()
    classes       = filiere.classes.all().order_by('niveau')

    return render(request, 'administration/filiere_detail.html', {
        'filiere':        filiere,
        'dept':           dept,
        'type_formation': type_formation,
        'etudiants':      etudiants,
        'nb_enseignants': nb_enseignants,
        'classes':        classes,
    })
# ══════════════════════════════════════════
# NAVIGATION ÉTUDIANTS
# ══════════════════════════════════════════

@login_required
def etudiants_departements(request):
    """Étape 1 : choisir un département"""
    departements = Departement.objects.all()
    dept_data = []
    for dept in departements:
        nb = Etudiant.objects.filter(
            filiere__departement=dept, statut='inscrit'
        ).count()
        dept_data.append({'dept': dept, 'nb_etudiants': nb})

    return render(request, 'administration/etudiants/nav_departements.html', {
        'dept_data': dept_data,
    })


@login_required
def etudiants_filieres(request, dept_id):
    """Étape 2 : choisir une filière (groupées par type)"""
    dept = get_object_or_404(Departement, pk=dept_id)

    TYPE_LABELS = [
        ('licence',  'Licences'),
        ('master',   'Masters'),
        ('doctorat', 'Doctorat'),
        ('cpi',      'CPI'),
        ('ci',       'CI'),
    ]

    groupes = []
    for tf, label in TYPE_LABELS:
        filieres = Filiere.objects.filter(
            departement=dept, type_formation=tf
        )
        if filieres.exists():
            fil_data = []
            for f in filieres:
                nb = Etudiant.objects.filter(
                    filiere=f, statut='inscrit'
                ).count()
                nb_classes = f.classes.count()
                fil_data.append({
                    'filiere':     f,
                    'nb_etudiants': nb,
                    'nb_classes':  nb_classes,
                })
            groupes.append({'label': label, 'type': tf, 'filieres': fil_data})

    return render(request, 'administration/etudiants/nav_filieres.html', {
        'dept':    dept,
        'groupes': groupes,
    })


@login_required
def etudiants_classes(request, dept_id, filiere_id):
    """Étape 3 : choisir une classe"""
    dept    = get_object_or_404(Departement, pk=dept_id)
    filiere = get_object_or_404(Filiere, pk=filiere_id)
    classes = filiere.classes.all().order_by('niveau', 'nom')

    classes_data = []
    for cl in classes:
        nb = Etudiant.objects.filter(
            filiere=filiere, statut='inscrit'
        ).count()
        classes_data.append({'classe': cl, 'nb_etudiants': nb})

    # Si aucune classe : afficher directement les étudiants de la filière
    if not classes.exists():
        etudiants = Etudiant.objects.filter(
            filiere=filiere, statut='inscrit'
        ).order_by('nom')
        return render(request, 'administration/etudiants/nav_classes.html', {
            'dept':          dept,
            'filiere':       filiere,
            'classes_data':  [],
            'etudiants_direct': etudiants,
        })

    return render(request, 'administration/etudiants/nav_classes.html', {
        'dept':         dept,
        'filiere':      filiere,
        'classes_data': classes_data,
    })


@login_required
def etudiants_liste_classe(request, dept_id, filiere_id, classe_id):
    """Étape 4 : liste des étudiants d'une classe"""
    dept    = get_object_or_404(Departement, pk=dept_id)
    filiere = get_object_or_404(Filiere, pk=filiere_id)
    classe  = get_object_or_404(Classe, pk=classe_id)

    # Les étudiants de cette filière (classe = niveau de la filière)
    etudiants = Etudiant.objects.filter(
        filiere=filiere, statut='inscrit'
    ).order_by('nom', 'prenom')

    query = request.GET.get('q', '')
    if query:
        etudiants = etudiants.filter(
            nom__icontains=query
        ) | Etudiant.objects.filter(
            prenom__icontains=query, filiere=filiere
        )

    return render(request, 'administration/etudiants/nav_liste.html', {
        'dept':      dept,
        'filiere':   filiere,
        'classe':    classe,
        'etudiants': etudiants,
        'query':     query,
    })


# ══════════════════════════════════════════
# NAVIGATION ENSEIGNANTS
# ══════════════════════════════════════════

@login_required
def enseignants_departements(request):
    """Étape 1 : choisir un département"""
    departements = Departement.objects.all()
    dept_data = []
    for dept in departements:
        nb = Enseignant.objects.filter(
            departement=dept, actif=True
        ).count()
        dept_data.append({'dept': dept, 'nb_enseignants': nb})

    return render(request, 'administration/enseignants/nav_departements.html', {
        'dept_data': dept_data,
    })


@login_required
def enseignants_liste(request, dept_id):
    """Étape 2 : liste des enseignants du département"""
    dept        = get_object_or_404(Departement, pk=dept_id)
    enseignants = Enseignant.objects.filter(
        departement=dept, actif=True
    ).order_by('grade', 'nom')

    query = request.GET.get('q', '')
    if query:
        enseignants = enseignants.filter(
            nom__icontains=query
        ) | Enseignant.objects.filter(
            prenom__icontains=query, departement=dept, actif=True
        )

    return render(request, 'administration/enseignants/nav_liste.html', {
        'dept':        dept,
        'enseignants': enseignants,
        'query':       query,
    })


@login_required
def detail_enseignant(request, pk):
    """Fiche enseignant + emploi du temps + matières par classe"""
    from pedagogie.models import EmploiDuTemps, Matiere

    enseignant = get_object_or_404(Enseignant, pk=pk)

    # Toutes les séances de cet enseignant
    seances = EmploiDuTemps.objects.filter(
        enseignant=enseignant
    ).select_related('matiere', 'salle', 'matiere__filiere').order_by('jour', 'heure_debut')

    # Regrouper par jour pour l'emploi du temps
    JOURS = {1:'Lundi', 2:'Mardi', 3:'Mercredi', 4:'Jeudi', 5:'Vendredi', 6:'Samedi'}
    emploi_par_jour = {}
    for j_num, j_nom in JOURS.items():
        seances_jour = [s for s in seances if s.jour == j_num]
        if seances_jour:
            emploi_par_jour[j_nom] = seances_jour

    # Matières par classe/filière enseignées
    # Regrouper : filière → liste de matières distinctes
    matieres_par_filiere = {}
    for seance in seances:
        filiere = seance.matiere.filiere
        key     = filiere.nom
        if key not in matieres_par_filiere:
            matieres_par_filiere[key] = {
                'filiere':  filiere,
                'matieres': set(),
                'classes':  set(),
            }
        matieres_par_filiere[key]['matieres'].add(seance.matiere.nom)
        # Trouver les classes associées à cette filière
        for cl in filiere.classes.all():
            matieres_par_filiere[key]['classes'].add(cl.nom)

    # Convertir les sets en listes pour le template
    matieres_classes = []
    for key, val in matieres_par_filiere.items():
        matieres_classes.append({
            'filiere':  val['filiere'],
            'matieres': sorted(val['matieres']),
            'classes':  sorted(val['classes']),
        })

    # Aussi les séances explicitement par classe (si EmploiDuTemps a un champ classe)
    # On regroupe directement seance → matiere → filiere → classes de cette filière
    seances_par_classe = {}
    for seance in seances:
        for cl in seance.matiere.filiere.classes.all():
            key = cl.nom
            if key not in seances_par_classe:
                seances_par_classe[key] = {
                    'classe':   cl,
                    'matieres': [],
                }
            mat_entry = {
                'matiere':    seance.matiere.nom,
                'type':       seance.get_type_seance_display(),
                'heure':      f"{seance.heure_debut.strftime('%H:%M')} – {seance.heure_fin.strftime('%H:%M')}",
                'jour':       JOURS.get(seance.jour, ''),
            }
            # Éviter les doublons
            if mat_entry not in seances_par_classe[key]['matieres']:
                seances_par_classe[key]['matieres'].append(mat_entry)

    return render(request, 'administration/enseignants/detail.html', {
        'enseignant':       enseignant,
        'seances':          seances,
        'emploi_par_jour':  emploi_par_jour,
        'matieres_classes': matieres_classes,
        'seances_par_classe': seances_par_classe.values(),
        'jours_ordre':      list(JOURS.values()),
    })
# ──────────────────────────────────────────
# INSCRIPTIONS
# ──────────────────────────────────────────
@login_required
def gestion_inscriptions(request):
    # POST : Nouvelle inscription
    if request.method == 'POST' and request.POST.get('action') == 'inscrire':
        try:
            etudiant = get_object_or_404(Etudiant, pk=request.POST['etudiant'])
            ins, created = Inscription.objects.get_or_create(
                etudiant=etudiant,
                annee_universitaire=request.POST['annee_univ'],
                defaults={
                    'filiere': etudiant.filiere,
                    'statut':  'en_attente',
                }
            )
            if not created:
                messages.warning(request, "L'étudiant est déjà inscrit pour cette année.")
            else:
                messages.success(request, f"Inscription de {etudiant.get_full_name()} créée !")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
        return redirect('administration:inscriptions')

    # POST : Changer le statut d'une inscription
    if request.method == 'POST' and request.POST.get('action') == 'changer_statut':
        try:
            ins = get_object_or_404(Inscription, pk=request.POST['inscription_id'])
            nouveau_statut = request.POST['statut']
            ins.statut      = nouveau_statut
            ins.commentaire = request.POST.get('commentaire', '')
            if nouveau_statut == 'validee':
                ins.date_validation = timezone.now().date()
                ins.valide_par      = request.user.get_full_name()
            ins.save()
            messages.success(request, f"Statut mis à jour : {ins.get_statut_display()}")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
        return redirect('administration:inscriptions')

    # Filtres
    statut_filtre   = request.GET.get('statut', '')
    annee_filtre    = request.GET.get('annee', '')
    dept_filtre     = request.GET.get('dept', '')
    query           = request.GET.get('q', '')

    inscriptions = Inscription.objects.select_related(
        'etudiant', 'filiere', 'filiere__departement'
    ).all()

    if statut_filtre:
        inscriptions = inscriptions.filter(statut=statut_filtre)
    if annee_filtre:
        inscriptions = inscriptions.filter(annee_universitaire=annee_filtre)
    if dept_filtre:
        inscriptions = inscriptions.filter(filiere__departement_id=dept_filtre)
    if query:
        inscriptions = inscriptions.filter(
            etudiant__nom__icontains=query
        ) | inscriptions.filter(
            etudiant__prenom__icontains=query
        ) | inscriptions.filter(
            etudiant__numero_etudiant__icontains=query
        )

    # Comptages par statut pour les indicateurs
    from django.db.models import Count
    stats_statut = {
        'en_attente':         Inscription.objects.filter(statut='en_attente').count(),
        'dossier_incomplet':  Inscription.objects.filter(statut='dossier_incomplet').count(),
        'frais_non_payes':    Inscription.objects.filter(statut='frais_non_payes').count(),
        'validee':            Inscription.objects.filter(statut='validee').count(),
        'suspendue':          Inscription.objects.filter(statut='suspendue').count(),
        'annulee':            Inscription.objects.filter(statut='annulee').count(),
    }

    return render(request, 'administration/inscriptions.html', {
        'inscriptions':   inscriptions,
        'etudiants':      Etudiant.objects.filter(statut='inscrit').order_by('nom'),
        'departements':   Departement.objects.all(),
        'statut_choices': Inscription.STATUT_CHOICES,
        'statut_filtre':  statut_filtre,
        'annee_filtre':   annee_filtre,
        'dept_filtre':    dept_filtre,
        'query':          query,
        'stats':          stats_statut,
    })


@login_required
def valider_inscription(request, pk):
    ins = get_object_or_404(Inscription, pk=pk)
    ins.statut          = 'validee'
    ins.date_validation = timezone.now().date()
    ins.valide_par      = request.user.get_full_name()
    ins.save()
    messages.success(request, f"Inscription de {ins.etudiant.get_full_name()} validée !")
    return redirect('administration:inscriptions')


@login_required
def attestation_inscription(request, pk):
    """Génère une attestation d'inscription avec QR Code"""
    ins = get_object_or_404(Inscription, pk=pk)

    if ins.statut != 'validee':
        messages.error(request, "Seules les inscriptions validées peuvent avoir une attestation.")
        return redirect('administration:inscriptions')

    # Générer QR Code
    qr_data = (
        f"FSB-ATTESTATION\n"
        f"Etudiant: {ins.etudiant.get_full_name()}\n"
        f"N: {ins.etudiant.numero_etudiant}\n"
        f"Filiere: {ins.filiere.nom}\n"
        f"Annee: {ins.annee_universitaire}\n"
        f"Date validation: {ins.date_validation}\n"
        f"Valide par: {ins.valide_par}"
    )
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0b1e3d", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'administration/attestation.html', {
        'ins':    ins,
        'qr_b64': qr_b64,
    })

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