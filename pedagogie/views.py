import json
import io
import base64
import qrcode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.utils import timezone
from .models import Matiere, EmploiDuTemps, Absence, Note, MoyenneEtudiant
from administration.models import (
    Departement, Filiere, Etudiant, Enseignant, Classe, Salle
)


# ════════════════════════════════════════════
# MATIÈRES
# ════════════════════════════════════════════

@login_required
def matieres_departements(request):
    departements = Departement.objects.all()
    dept_data = []
    for dept in departements:
        nb = Matiere.objects.filter(filiere__departement=dept).count()
        dept_data.append({'dept': dept, 'nb_matieres': nb,
                          'nb_filieres': Filiere.objects.filter(departement=dept).count()})
    return render(request, 'pedagogie/matieres/nav_departements.html', {'dept_data': dept_data})


@login_required
def matieres_filieres(request, dept_id):
    dept = get_object_or_404(Departement, pk=dept_id)
    filieres = Filiere.objects.filter(departement=dept).order_by('type_formation','nom')
    TYPE_LABELS = {'licence':'Licences','master':'Masters','doctorat':'Doctorat','cpi':'CPI','ci':'CI'}
    groupes = {}
    for f in filieres:
        lbl = TYPE_LABELS.get(f.type_formation, f.type_formation.capitalize())
        if lbl not in groupes:
            groupes[lbl] = []
        groupes[lbl].append({'filiere': f, 'nb_matieres': Matiere.objects.filter(filiere=f).count()})
    return render(request, 'pedagogie/matieres/nav_filieres.html', {'dept': dept, 'groupes': groupes})


@login_required
def matieres_liste(request, dept_id, filiere_id):
    dept    = get_object_or_404(Departement, pk=dept_id)
    filiere = get_object_or_404(Filiere, pk=filiere_id)
    return render(request, 'pedagogie/matieres/liste.html', {
        'dept': dept, 'filiere': filiere,
        'matieres_s1': Matiere.objects.filter(filiere=filiere, semestre=1).order_by('nom'),
        'matieres_s2': Matiere.objects.filter(filiere=filiere, semestre=2).order_by('nom'),
    })


@login_required
def ajouter_matiere(request):
    filiere_id = request.GET.get('filiere') or request.POST.get('filiere')
    dept_id    = request.GET.get('dept')    or request.POST.get('dept')
    if request.method == 'POST':
        try:
            filiere = get_object_or_404(Filiere, pk=request.POST['filiere'])
            Matiere.objects.create(
                nom=request.POST['nom'], code=request.POST['code'],
                filiere=filiere, semestre=request.POST['semestre'],
                credits=request.POST.get('credits',3),
                coefficient=request.POST.get('coefficient',1.0),
                heures_cours=request.POST.get('heures_cours',0),
                heures_td=request.POST.get('heures_td',0),
                heures_tp=request.POST.get('heures_tp',0),
            )
            messages.success(request, "Matière ajoutée !")
            return redirect('pedagogie:matieres_liste', dept_id=filiere.departement.pk, filiere_id=filiere.pk)
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    filieres    = Filiere.objects.select_related('departement').order_by('departement__nom','nom')
    filiere_sel = Filiere.objects.filter(pk=filiere_id).first() if filiere_id else None
    return render(request, 'pedagogie/matieres/ajouter.html', {
        'filieres': filieres, 'filiere_sel': filiere_sel,
        'dept_id': dept_id, 'departements': Departement.objects.all(),
    })


@login_required
def modifier_matiere(request, pk):
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        try:
            matiere.nom=request.POST['nom']; matiere.code=request.POST['code']
            matiere.filiere_id=request.POST['filiere']; matiere.semestre=request.POST['semestre']
            matiere.credits=request.POST.get('credits',3)
            matiere.coefficient=request.POST.get('coefficient',1.0)
            matiere.heures_cours=request.POST.get('heures_cours',0)
            matiere.heures_td=request.POST.get('heures_td',0)
            matiere.heures_tp=request.POST.get('heures_tp',0)
            matiere.save()
            messages.success(request, "Matière modifiée !")
            return redirect('pedagogie:matieres_liste',
                dept_id=matiere.filiere.departement.pk, filiere_id=matiere.filiere.pk)
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return render(request, 'pedagogie/matieres/modifier.html', {
        'matiere': matiere,
        'filieres': Filiere.objects.select_related('departement').order_by('departement__nom','nom'),
    })


@login_required
def supprimer_matiere(request, pk):
    matiere = get_object_or_404(Matiere, pk=pk)
    dept_id, filiere_id = matiere.filiere.departement.pk, matiere.filiere.pk
    if request.method == 'POST':
        matiere.delete()
        messages.success(request, "Matière supprimée.")
        return redirect('pedagogie:matieres_liste', dept_id=dept_id, filiere_id=filiere_id)
    return render(request, 'pedagogie/matieres/confirmer_suppression.html', {'matiere': matiere})


# ════════════════════════════════════════════
# EMPLOI DU TEMPS
# ════════════════════════════════════════════

def _dept_data_edt(departements):
    data = []
    for dept in departements:
        nb = EmploiDuTemps.objects.filter(matiere__filiere__departement=dept).count()
        data.append({'dept': dept, 'nb_seances': nb})
    return data


@login_required
def edt_departements(request):
    return render(request, 'pedagogie/edt/nav_departements.html', {
        'dept_data': _dept_data_edt(Departement.objects.all())
    })


@login_required
def edt_filieres(request, dept_id):
    dept    = get_object_or_404(Departement, pk=dept_id)
    filieres = Filiere.objects.filter(departement=dept)
    fil_data = []
    for f in filieres:
        nb = EmploiDuTemps.objects.filter(matiere__filiere=f).count()
        fil_data.append({'filiere': f, 'nb_seances': nb,
                         'nb_classes': f.classes.count()})
    return render(request, 'pedagogie/edt/nav_filieres.html', {
        'dept': dept, 'fil_data': fil_data
    })


@login_required
def edt_classes(request, dept_id, filiere_id):
    dept    = get_object_or_404(Departement, pk=dept_id)
    filiere = get_object_or_404(Filiere, pk=filiere_id)
    classes = filiere.classes.all().order_by('niveau','nom')
    cl_data = []
    for cl in classes:
        nb = cl.seances.count()
        cl_data.append({'classe': cl, 'nb_seances': nb})
    return render(request, 'pedagogie/edt/nav_classes.html', {
        'dept': dept, 'filiere': filiere, 'cl_data': cl_data
    })


@login_required
def edt_classe_detail(request, classe_id):
    classe   = get_object_or_404(Classe, pk=classe_id)
    dept     = classe.filiere.departement
    semestre = int(request.GET.get('semestre', 1))

    seances  = EmploiDuTemps.objects.filter(
        classe=classe, semestre=semestre
    ).select_related('matiere','enseignant','salle').order_by('jour','heure_debut')

    JOURS = {1:'Lundi',2:'Mardi',3:'Mercredi',4:'Jeudi',5:'Vendredi',6:'Samedi'}
    HORAIRES = ['08:00','09:30','11:00','13:30','15:00','16:30']

    # Grille emploi du temps
    grille = {j: {} for j in JOURS.keys()}
    for s in seances:
        h = s.heure_debut.strftime('%H:%M')
        if h not in grille[s.jour]:
            grille[s.jour][h] = []
        grille[s.jour][h].append(s)

    return render(request, 'pedagogie/edt/classe_detail.html', {
        'classe':    classe,
        'dept':      dept,
        'semestre':  semestre,
        'seances':   seances,
        'grille':    grille,
        'jours':     JOURS,
        'horaires':  HORAIRES,
        'matieres':  Matiere.objects.filter(filiere=classe.filiere, semestre=semestre),
        'enseignants': Enseignant.objects.filter(departement=dept, actif=True),
        'salles':    Salle.objects.all(),
    })


@login_required
def ajouter_seance(request):
    if request.method == 'POST':
        try:
            classe_id  = request.POST['classe']
            jour       = request.POST['jour']
            heure_deb  = request.POST['heure_debut']
            heure_fin  = request.POST['heure_fin']
            salle_id   = request.POST.get('salle') or None
            ens_id     = request.POST.get('enseignant') or None
            semestre   = request.POST['semestre']

            # Vérif conflit salle
            if salle_id:
                conflit = EmploiDuTemps.objects.filter(
                    salle_id=salle_id, jour=jour, semestre=semestre,
                    heure_debut__lt=heure_fin, heure_fin__gt=heure_deb
                )
                if conflit.exists():
                    s = conflit.first()
                    messages.error(request,
                        f"Conflit salle : {s.salle.nom} occupée {s.get_jour_display()} "
                        f"{s.heure_debut.strftime('%H:%M')}–{s.heure_fin.strftime('%H:%M')} "
                        f"({s.matiere.nom})")
                    return redirect(f"{request.META.get('HTTP_REFERER','/')}")

            # Vérif conflit enseignant
            if ens_id:
                conflit_ens = EmploiDuTemps.objects.filter(
                    enseignant_id=ens_id, jour=jour, semestre=semestre,
                    heure_debut__lt=heure_fin, heure_fin__gt=heure_deb
                )
                if conflit_ens.exists():
                    s = conflit_ens.first()
                    messages.error(request,
                        f"Conflit enseignant : déjà une séance {s.get_jour_display()} "
                        f"{s.heure_debut.strftime('%H:%M')}–{s.heure_fin.strftime('%H:%M')}")
                    return redirect(f"{request.META.get('HTTP_REFERER','/')}")

            EmploiDuTemps.objects.create(
                matiere_id=request.POST['matiere'],
                enseignant_id=ens_id,
                salle_id=salle_id,
                classe_id=classe_id,
                jour=jour,
                heure_debut=heure_deb,
                heure_fin=heure_fin,
                type_seance=request.POST['type_seance'],
                annee_universitaire=request.POST.get('annee_univ','2024-2025'),
                semestre=semestre,
            )
            messages.success(request, "Séance ajoutée !")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def modifier_seance(request, pk):
    seance = get_object_or_404(EmploiDuTemps, pk=pk)
    classe = seance.classe
    if request.method == 'POST':
        try:
            seance.matiere_id    = request.POST['matiere']
            seance.enseignant_id = request.POST.get('enseignant') or None
            seance.salle_id      = request.POST.get('salle') or None
            seance.jour          = request.POST['jour']
            seance.heure_debut   = request.POST['heure_debut']
            seance.heure_fin     = request.POST['heure_fin']
            seance.type_seance   = request.POST['type_seance']
            seance.semestre      = request.POST['semestre']
            seance.save()
            messages.success(request, "Séance modifiée !")
            return redirect('pedagogie:edt_classe', classe_id=classe.pk)
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return render(request, 'pedagogie/edt/modifier_seance.html', {
        'seance': seance, 'classe': classe,
        'matieres':    Matiere.objects.filter(filiere=classe.filiere),
        'enseignants': Enseignant.objects.filter(actif=True),
        'salles':      Salle.objects.all(),
        'jours':       EmploiDuTemps.JOUR_CHOICES,
        'types':       EmploiDuTemps.TYPE_CHOICES,
    })


@login_required
def supprimer_seance(request, pk):
    seance    = get_object_or_404(EmploiDuTemps, pk=pk)
    classe_id = seance.classe.pk if seance.classe else None
    seance.delete()
    messages.success(request, "Séance supprimée.")
    if classe_id:
        return redirect('pedagogie:edt_classe', classe_id=classe_id)
    return redirect('pedagogie:emploi_du_temps')


# ════════════════════════════════════════════
# ABSENCES (lecture seule)
# ════════════════════════════════════════════

@login_required
def absences_departements(request):
    dept_data = []
    for dept in Departement.objects.all():
        nb = Absence.objects.filter(seance__classe__filiere__departement=dept).count()
        dept_data.append({'dept': dept, 'nb_absences': nb})
    return render(request, 'pedagogie/absences/nav_departements.html', {'dept_data': dept_data})


@login_required
def absences_filieres(request, dept_id):
    dept    = get_object_or_404(Departement, pk=dept_id)
    filieres = Filiere.objects.filter(departement=dept)
    fil_data = []
    for f in filieres:
        nb = Absence.objects.filter(seance__classe__filiere=f).count()
        fil_data.append({'filiere': f, 'nb_absences': nb})
    return render(request, 'pedagogie/absences/nav_filieres.html', {
        'dept': dept, 'fil_data': fil_data
    })


@login_required
def absences_classes(request, dept_id, filiere_id):
    dept    = get_object_or_404(Departement, pk=dept_id)
    filiere = get_object_or_404(Filiere, pk=filiere_id)
    classes = filiere.classes.all()
    cl_data = []
    for cl in classes:
        nb = Absence.objects.filter(seance__classe=cl).count()
        cl_data.append({'classe': cl, 'nb_absences': nb})
    return render(request, 'pedagogie/absences/nav_classes.html', {
        'dept': dept, 'filiere': filiere, 'cl_data': cl_data
    })


@login_required
def absences_classe_detail(request, classe_id):
    classe   = get_object_or_404(Classe, pk=classe_id)
    dept     = classe.filiere.departement
    etudiants = Etudiant.objects.filter(filiere=classe.filiere, statut='inscrit')

    # Pour chaque étudiant : absences par matière + vérif élimination
    data_etudiants = []
    matieres = Matiere.objects.filter(filiere=classe.filiere)

    for et in etudiants:
        absences_et = []
        elimine     = False
        total_abs   = 0
        for mat in matieres:
            nb_abs = Absence.objects.filter(
                etudiant=et,
                seance__matiere=mat,
            ).count()
            seuil    = mat.seuil_elimination()
            est_elim = nb_abs > seuil and seuil > 0
            if est_elim:
                elimine = True
            total_abs += nb_abs
            absences_et.append({
                'matiere':    mat,
                'nb_absences': nb_abs,
                'seuil':      seuil,
                'elimine':    est_elim,
                'pct':        round((nb_abs / mat.total_heures() * 100), 1) if mat.total_heures() > 0 else 0,
            })
        data_etudiants.append({
            'etudiant':   et,
            'absences':   absences_et,
            'total_abs':  total_abs,
            'elimine':    elimine,
        })

    # Stats pour chart
    nb_elimines = sum(1 for d in data_etudiants if d['elimine'])
    nb_ok       = len(data_etudiants) - nb_elimines

    # Absences par matière pour chart
    abs_par_matiere = []
    for mat in matieres:
        nb = Absence.objects.filter(seance__matiere=mat, etudiant__filiere=classe.filiere).count()
        abs_par_matiere.append({'matiere': mat.nom, 'nb': nb})

    return render(request, 'pedagogie/absences/classe_detail.html', {
        'classe':          classe,
        'dept':            dept,
        'data_etudiants':  data_etudiants,
        'nb_elimines':     nb_elimines,
        'nb_ok':           nb_ok,
        'abs_par_matiere': json.dumps(abs_par_matiere),
        'labels_etudiants': json.dumps([d['etudiant'].get_full_name() for d in data_etudiants]),
        'data_totaux':     json.dumps([d['total_abs'] for d in data_etudiants]),
    })


# ════════════════════════════════════════════
# NOTES (lecture + calculs admin)
# ════════════════════════════════════════════

@login_required
def notes_departements(request):
    dept_data = []
    for dept in Departement.objects.all():
        nb = Note.objects.filter(matiere__filiere__departement=dept).count()
        dept_data.append({'dept': dept, 'nb_notes': nb})
    return render(request, 'pedagogie/notes/nav_departements.html', {'dept_data': dept_data})


@login_required
def notes_filieres(request, dept_id):
    dept    = get_object_or_404(Departement, pk=dept_id)
    filieres = Filiere.objects.filter(departement=dept)
    fil_data = []
    for f in filieres:
        nb = Note.objects.filter(matiere__filiere=f).count()
        fil_data.append({'filiere': f, 'nb_notes': nb})
    return render(request, 'pedagogie/notes/nav_filieres.html', {
        'dept': dept, 'fil_data': fil_data
    })


@login_required
def notes_classes(request, dept_id, filiere_id):
    dept    = get_object_or_404(Departement, pk=dept_id)
    filiere = get_object_or_404(Filiere, pk=filiere_id)
    classes = filiere.classes.all()
    cl_data = []
    for cl in classes:
        nb_moy = MoyenneEtudiant.objects.filter(classe=cl).count()
        cl_data.append({'classe': cl, 'nb_moyennes': nb_moy})
    return render(request, 'pedagogie/notes/nav_classes.html', {
        'dept': dept, 'filiere': filiere, 'cl_data': cl_data
    })


@login_required
def notes_classe_detail(request, classe_id):
    classe    = get_object_or_404(Classe, pk=classe_id)
    dept      = classe.filiere.departement
    semestre  = int(request.GET.get('semestre', 1))
    annee     = request.GET.get('annee', '2024-2025')
    etudiants = Etudiant.objects.filter(filiere=classe.filiere, statut='inscrit')
    matieres  = Matiere.objects.filter(filiere=classe.filiere, semestre=semestre)

    # Récupérer les moyennes calculées
    moyennes_map = {}
    for m in MoyenneEtudiant.objects.filter(
        classe=classe, semestre=semestre, annee_universitaire=annee
    ):
        moyennes_map[m.etudiant_id] = m

    data_etudiants = []
    for et in etudiants:
        notes_et = Note.objects.filter(
            etudiant=et, matiere__filiere=classe.filiere,
            semestre=semestre, annee_universitaire=annee
        ).select_related('matiere')
        moy_obj = moyennes_map.get(et.pk)
        data_etudiants.append({
            'etudiant': et,
            'notes':    notes_et,
            'moyenne':  moy_obj,
        })

    # Stats chart
    mentions_count = {
        'excellent':  0, 'tres_bien': 0, 'bien': 0,
        'assez_bien': 0, 'passable':  0, 'echec': 0,
    }
    nb_admis = 0
    for d in data_etudiants:
        if d['moyenne']:
            if d['moyenne'].admis:
                nb_admis += 1
                m = d['moyenne'].mention
                if m in mentions_count:
                    mentions_count[m] += 1
            else:
                mentions_count['echec'] += 1

    nb_total  = len(data_etudiants)
    pct_reuss = round(nb_admis / nb_total * 100, 1) if nb_total else 0

    return render(request, 'pedagogie/notes/classe_detail.html', {
        'classe':         classe,
        'dept':           dept,
        'semestre':       semestre,
        'annee':          annee,
        'matieres':       matieres,
        'data_etudiants': data_etudiants,
        'nb_admis':       nb_admis,
        'nb_total':       nb_total,
        'pct_reuss':      pct_reuss,
        'mentions_json':  json.dumps(mentions_count),
        'moyennes_calculees': bool(moyennes_map),
    })


@login_required
def calculer_moyennes(request, classe_id):
    """Admin lance le calcul — ne modifie pas les notes"""
    if request.method != 'POST':
        return redirect('pedagogie:notes_classe', classe_id=classe_id)

    classe    = get_object_or_404(Classe, pk=classe_id)
    semestre  = int(request.POST.get('semestre', 1))
    annee     = request.POST.get('annee', '2024-2025')
    etudiants = Etudiant.objects.filter(filiere=classe.filiere, statut='inscrit')
    matieres  = Matiere.objects.filter(filiere=classe.filiere, semestre=semestre)
    nb_calcul = 0

    for et in etudiants:
        somme_pond  = 0
        somme_coeff = 0
        for mat in matieres:
            notes_mat = Note.objects.filter(
                etudiant=et, matiere=mat,
                semestre=semestre, annee_universitaire=annee
            )
            if notes_mat.exists():
                # DS 40% + Exam 60% (ou moyenne simple)
                note_ds   = notes_mat.filter(type_note='ds').first()
                note_exam = notes_mat.filter(type_note='exam').first()
                note_tp   = notes_mat.filter(type_note='tp').first()

                if note_ds and note_exam:
                    note_mat = (note_ds.note * 0.4) + (note_exam.note * 0.6)
                elif note_exam:
                    note_mat = note_exam.note
                elif note_ds:
                    note_mat = note_ds.note
                else:
                    note_mat = notes_mat.aggregate(Avg('note'))['note__avg'] or 0

                if note_tp:
                    note_mat = (note_mat * 0.7) + (note_tp.note * 0.3)

                somme_pond  += note_mat * mat.coefficient
                somme_coeff += mat.coefficient

        if somme_coeff > 0:
            moy = round(somme_pond / somme_coeff, 2)
            mention = MoyenneEtudiant.calculer_mention(moy)
            MoyenneEtudiant.objects.update_or_create(
                etudiant=et, classe=classe,
                annee_universitaire=annee, semestre=semestre,
                defaults={
                    'moyenne': moy,
                    'mention': mention,
                    'admis':   moy >= 10,
                }
            )
            nb_calcul += 1

    messages.success(request, f"Moyennes calculées pour {nb_calcul} étudiant(s).")
    return redirect(f"{request.build_absolute_uri('/')[:-1]}"
                    f"/pedagogie/notes/classe/{classe_id}/?semestre={semestre}&annee={annee}")


@login_required
def releve_notes_etudiant(request, etudiant_id):
    etudiant  = get_object_or_404(Etudiant, pk=etudiant_id)
    semestre  = int(request.GET.get('semestre', 1))
    annee     = request.GET.get('annee', '2024-2025')
    notes     = Note.objects.filter(
        etudiant=etudiant, semestre=semestre, annee_universitaire=annee
    ).select_related('matiere').order_by('matiere__nom')
    moyenne   = MoyenneEtudiant.objects.filter(
        etudiant=etudiant, semestre=semestre, annee_universitaire=annee
    ).first()
    return render(request, 'pedagogie/notes/releve.html', {
        'etudiant': etudiant, 'notes': notes,
        'moyenne': moyenne, 'semestre': semestre, 'annee': annee,
    })


@login_required
def attestation_reussite(request, etudiant_id):
    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)
    semestre = int(request.GET.get('semestre', 1))
    annee    = request.GET.get('annee', '2024-2025')
    moyenne  = MoyenneEtudiant.objects.filter(
        etudiant=etudiant, semestre=semestre, annee_universitaire=annee
    ).first()

    if not moyenne or not moyenne.admis:
        messages.error(request, "Attestation disponible uniquement pour les étudiants admis.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # QR Code
    qr_data = (
        f"FSB-REUSSITE\n"
        f"Etudiant: {etudiant.get_full_name()}\n"
        f"N: {etudiant.numero_etudiant}\n"
        f"Filiere: {etudiant.filiere}\n"
        f"Moyenne: {moyenne.moyenne}/20\n"
        f"Mention: {moyenne.get_mention_display()}\n"
        f"Annee: {annee} S{semestre}"
    )
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0b1e3d", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return render(request, 'pedagogie/notes/attestation_reussite.html', {
        'etudiant': etudiant, 'moyenne': moyenne,
        'semestre': semestre, 'annee': annee, 'qr_b64': qr_b64,
    })