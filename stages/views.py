import io
import base64
import qrcode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import DemandeStage, Diplome
from administration.models import Etudiant, Enseignant, Filiere, Departement
from pedagogie.models import MoyenneEtudiant, Note


def _generer_qr(data):
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0b1e3d", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()


# ════════════════════════════════════════════
# DEMANDES DE STAGE
# ════════════════════════════════════════════

@login_required
def liste_demandes(request):
    statut = request.GET.get('statut', '')
    query  = request.GET.get('q', '')

    qs = DemandeStage.objects.select_related(
        'etudiant', 'encadrant_fsb'
    ).order_by('-date_demande')

    if statut:
        qs = qs.filter(statut=statut)
    if query:
        qs = qs.filter(etudiant__nom__icontains=query) | \
             qs.filter(etudiant__prenom__icontains=query) | \
             qs.filter(etudiant__numero_etudiant__icontains=query) | \
             qs.filter(sujet__icontains=query)

    stats = {
        'en_attente': DemandeStage.objects.filter(statut='en_attente').count(),
        'valide':     DemandeStage.objects.filter(statut='valide').count(),
        'refuse':     DemandeStage.objects.filter(statut='refuse').count(),
        'en_cours':   DemandeStage.objects.filter(statut='en_cours').count(),
        'termine':    DemandeStage.objects.filter(statut='termine').count(),
    }

    return render(request, 'stages/liste.html', {
        'demandes': qs,
        'statut':   statut,
        'query':    query,
        'stats':    stats,
    })


@login_required
def detail_demande(request, pk):
    demande = get_object_or_404(DemandeStage, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'valider':
            demande.statut            = 'valide'
            demande.encadrant_fsb_id  = request.POST.get('encadrant') or None
            demande.commentaire_admin = request.POST.get('commentaire', '')
            demande.save()
            messages.success(request, "Demande de stage validée !")

        elif action == 'refuser':
            demande.statut            = 'refuse'
            demande.commentaire_admin = request.POST.get('commentaire', '')
            demande.save()
            messages.success(request, "Demande de stage refusée.")

        elif action == 'en_cours':
            demande.statut = 'en_cours'
            demande.save()
            messages.success(request, "Stage marqué en cours.")

        elif action == 'terminer':
            note = request.POST.get('note_stage')
            if note:
                demande.note_stage = float(note)
            demande.statut = 'termine'
            demande.save()
            messages.success(request, "Stage terminé et noté.")

        return redirect('stages:detail_demande', pk=pk)

    return render(request, 'stages/detail.html', {
        'demande':     demande,
        'enseignants': Enseignant.objects.filter(actif=True).order_by('nom'),
    })


@login_required
def attestation_stage(request, pk):
    demande = get_object_or_404(DemandeStage, pk=pk)

    if demande.statut not in ['valide', 'en_cours', 'termine']:
        messages.error(request, "Attestation disponible uniquement pour les stages validés.")
        return redirect('stages:detail_demande', pk=pk)

    qr_data = (
        f"FSB-STAGE\n"
        f"Etudiant: {demande.etudiant.get_full_name()}\n"
        f"N: {demande.etudiant.numero_etudiant}\n"
        f"Sujet: {demande.sujet}\n"
        f"Entreprise: {demande.entreprise}\n"
        f"Periode: {demande.date_debut} - {demande.date_fin}\n"
        f"Type: {demande.get_type_stage_display()}\n"
        f"Statut: {demande.get_statut_display()}"
    )
    return render(request, 'stages/attestation_stage.html', {
        'demande': demande,
        'qr_b64':  _generer_qr(qr_data),
    })


# ════════════════════════════════════════════
# DIPLÔMES
# ════════════════════════════════════════════

@login_required
def liste_diplomes(request):
    diplomes = Diplome.objects.select_related('etudiant').order_by('-annee_obtention')
    return render(request, 'stages/diplomes.html', {'diplomes': diplomes})


@login_required
def etudiants_eligibles_diplome(request):
    """
    Affiche les étudiants des niveaux terminaux (L3, M2, Doc)
    qui ont réussi tous leurs semestres ET leur stage PFE >= 10.
    """
    NIVEAUX_TERMINAUX = ['L3', 'M2', 'Doc', 'CI3']

    filieres_terminales = Filiere.objects.filter(niveau__in=NIVEAUX_TERMINAUX)

    etudiants_data = []
    for filiere in filieres_terminales:
        etudiants = Etudiant.objects.filter(filiere=filiere, statut='inscrit')
        for et in etudiants:
            # Vérif : a-t-il des moyennes calculées ?
            moyennes = MoyenneEtudiant.objects.filter(etudiant=et)
            if not moyennes.exists():
                continue

            # Tous les semestres admis ?
            tous_admis = all(m.admis for m in moyennes)

            # Stage PFE terminé avec note >= 10 ?
            stage_pfe = DemandeStage.objects.filter(
                etudiant=et,
                type_stage='pfe',
                statut='termine',
                note_stage__gte=10,
            ).first()

            # Déjà diplômé ?
            deja_diplome = Diplome.objects.filter(etudiant=et).exists()

            etudiants_data.append({
                'etudiant':      et,
                'filiere':       filiere,
                'tous_admis':    tous_admis,
                'stage_pfe':     stage_pfe,
                'eligible':      tous_admis and bool(stage_pfe),
                'deja_diplome':  deja_diplome,
                'moyennes':      moyennes,
            })

    # Filtrer si demandé
    filtre = request.GET.get('filtre', 'tous')
    if filtre == 'eligible':
        etudiants_data = [d for d in etudiants_data if d['eligible'] and not d['deja_diplome']]
    elif filtre == 'non_eligible':
        etudiants_data = [d for d in etudiants_data if not d['eligible']]

    return render(request, 'stages/eligibles_diplome.html', {
        'etudiants_data': etudiants_data,
        'filtre':         filtre,
        'nb_eligibles':   sum(1 for d in etudiants_data if d['eligible'] and not d['deja_diplome']),
    })


@login_required
def generer_diplome(request, etudiant_id):
    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)

    # Vérifications
    moyennes = MoyenneEtudiant.objects.filter(etudiant=etudiant)
    tous_admis = moyennes.exists() and all(m.admis for m in moyennes)
    stage_pfe  = DemandeStage.objects.filter(
        etudiant=etudiant, type_stage='pfe',
        statut='termine', note_stage__gte=10
    ).first()

    if not tous_admis or not stage_pfe:
        messages.error(request, "L'étudiant ne remplit pas toutes les conditions.")
        return redirect('stages:eligibles_diplome')

    if request.method == 'POST':
        try:
            # Calculer la moyenne générale
            moy_gen = sum(m.moyenne for m in moyennes) / moyennes.count()
            mention = MoyenneEtudiant.calculer_mention(moy_gen)

            import random
            num_diplome = f"FSB-{etudiant.filiere.code}-{timezone.now().year}-{etudiant.numero_etudiant}"

            diplome, created = Diplome.objects.get_or_create(
                etudiant=etudiant,
                defaults={
                    'type_diplome':    etudiant.filiere.get_type_formation_display(),
                    'specialite':      etudiant.filiere.nom,
                    'annee_obtention': timezone.now().year,
                    'mention':         mention,
                    'moyenne_generale': round(moy_gen, 2),
                    'numero_diplome':  num_diplome,
                    'date_delivrance': timezone.now().date(),
                }
            )
            if not created:
                messages.warning(request, "Un diplôme existe déjà pour cet étudiant.")
            else:
                # Mettre à jour le statut de l'étudiant
                etudiant.statut = 'diplome'
                etudiant.save()
                messages.success(request, f"Diplôme généré pour {etudiant.get_full_name()} !")

            return redirect('stages:diplome_officiel', pk=diplome.pk)
        except Exception as e:
            messages.error(request, f"Erreur : {e}")

    # GET : confirmation avant génération
    return render(request, 'stages/confirmer_diplome.html', {
        'etudiant':  etudiant,
        'moyennes':  moyennes,
        'stage_pfe': stage_pfe,
    })


@login_required
def diplome_officiel(request, pk):
    diplome  = get_object_or_404(Diplome, pk=pk)
    etudiant = diplome.etudiant

    qr_data = (
        f"FSB-DIPLOME\n"
        f"N: {diplome.numero_diplome}\n"
        f"Etudiant: {etudiant.get_full_name()}\n"
        f"Matricule: {etudiant.numero_etudiant}\n"
        f"Diplome: {diplome.type_diplome}\n"
        f"Specialite: {diplome.specialite}\n"
        f"Mention: {diplome.mention}\n"
        f"Moyenne: {diplome.moyenne_generale}/20\n"
        f"Annee: {diplome.annee_obtention}\n"
        f"Delivre le: {diplome.date_delivrance}"
    )
    return render(request, 'stages/diplome_officiel.html', {
        'diplome': diplome,
        'qr_b64':  _generer_qr(qr_data),
    })


@login_required
def ajouter_diplome(request):
    if request.method == 'POST':
        try:
            Diplome.objects.create(
                etudiant_id     = request.POST['etudiant'],
                type_diplome    = request.POST['type_diplome'],
                specialite      = request.POST['specialite'],
                annee_obtention = request.POST['annee_obtention'],
                mention         = request.POST.get('mention', ''),
                moyenne_generale= request.POST.get('moyenne') or None,
                numero_diplome  = request.POST['numero_diplome'],
                date_delivrance = request.POST.get('date_delivrance') or None,
            )
            messages.success(request, "Diplôme enregistré !")
            return redirect('stages:diplomes')
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return render(request, 'stages/ajouter_diplome.html', {
        'etudiants': Etudiant.objects.filter(statut__in=['inscrit','diplome']),
    })