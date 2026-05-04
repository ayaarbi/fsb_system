from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SessionExamen, PlanningExamen, ResultatExamen
from administration.models import Salle, Classe
from pedagogie.models import Matiere
from itertools import groupby
from operator import attrgetter


@login_required
def liste_sessions(request):
    sessions = SessionExamen.objects.order_by('-date_debut')
    return render(request, 'examens/sessions.html', {'sessions': sessions})


@login_required
def ajouter_session(request):
    if request.method == 'POST':
        try:
            SessionExamen.objects.create(
                nom                 = request.POST['nom'],
                type_session        = request.POST['type_session'],
                annee_universitaire = request.POST['annee_univ'],
                semestre            = request.POST['semestre'],
                date_debut          = request.POST['date_debut'],
                date_fin            = request.POST['date_fin'],
            )
            messages.success(request, "Session créée avec succès !")
            return redirect('examens:sessions')
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return render(request, 'examens/ajouter_session.html')


@login_required
def planning_examens(request):
    session_id = request.GET.get('session', '')
    session    = None

    if session_id:
        try:
            session = SessionExamen.objects.get(pk=session_id)
        except SessionExamen.DoesNotExist:
            pass

    # ── POST : Créer un planning ──
    if request.method == 'POST':
        try:
            salle_id   = request.POST.get('salle') or None
            classe_id  = request.POST.get('classe') or None
            date_exam  = request.POST['date']
            heure_deb  = request.POST['heure_debut']
            heure_fin  = request.POST['heure_fin']
            matiere_id = request.POST['matiere']
            sess_id    = request.POST['session']

            # ── Vérification contrainte SALLE ──
            if salle_id:
                conflit_salle = PlanningExamen.objects.filter(
                    salle_id=salle_id,
                    date=date_exam,
                    heure_debut__lt=heure_fin,
                    heure_fin__gt=heure_deb,
                )
                if conflit_salle.exists():
                    ex = conflit_salle.first()
                    messages.error(
                        request,
                        f"⚠️ Conflit salle : cette salle est déjà occupée le {date_exam} "
                        f"de {ex.heure_debut.strftime('%H:%M')} à {ex.heure_fin.strftime('%H:%M')} "
                        f"pour '{ex.matiere.nom}'."
                    )
                    return redirect(f"{request.path}?session={sess_id}")

            # ── Vérification contrainte CLASSE ──
            if classe_id:
                conflit_classe = PlanningExamen.objects.filter(
                    classe_id=classe_id,
                    date=date_exam,
                    heure_debut__lt=heure_fin,
                    heure_fin__gt=heure_deb,
                )
                if conflit_classe.exists():
                    ex = conflit_classe.first()
                    messages.error(
                        request,
                        f"⚠️ Conflit classe : cette classe a déjà un examen le {date_exam} "
                        f"de {ex.heure_debut.strftime('%H:%M')} à {ex.heure_fin.strftime('%H:%M')} "
                        f"pour '{ex.matiere.nom}'."
                    )
                    return redirect(f"{request.path}?session={sess_id}")

            PlanningExamen.objects.create(
                session_id  = sess_id,
                matiere_id  = matiere_id,
                salle_id    = salle_id,
                classe_id   = classe_id,
                date        = date_exam,
                heure_debut = heure_deb,
                heure_fin   = heure_fin,
            )
            messages.success(request, "Examen planifié avec succès !")
            return redirect(f"{request.path}?session={sess_id}")

        except Exception as e:
            messages.error(request, f"Erreur : {e}")

    # ── GET : Afficher le planning ──
    plannings = PlanningExamen.objects.filter(
        session=session
    ).select_related(
        'matiere', 'salle', 'session', 'classe'
    ).order_by('date', 'heure_debut') if session else []

    # Grouper par date pour l'affichage tableau par jour
    planning_par_jour = {}
    for p in plannings:
        key = p.date
        if key not in planning_par_jour:
            planning_par_jour[key] = []
        planning_par_jour[key].append(p)

    return render(request, 'examens/planning.html', {
        'session':          session,
        'sessions':         SessionExamen.objects.order_by('-date_debut'),
        'matieres':         Matiere.objects.all(),
        'salles':           Salle.objects.all(),
        'classes':          Classe.objects.all().order_by('nom'),
        'planning_par_jour': planning_par_jour,
        'plannings_count':  len(plannings),
    })
@login_required
def supprimer_planning(request, pk):
    planning   = get_object_or_404(PlanningExamen, pk=pk)
    session_pk = planning.session.pk
    planning.delete()
    messages.success(request, "Examen supprimé du planning.")
    return redirect(f"{'/examens/planning/'}?session={session_pk}")

@login_required
def resultats(request):
    session_id = request.GET.get('session', '')
    resultats  = ResultatExamen.objects.select_related(
        'etudiant', 'matiere', 'session'
    ).all()
    if session_id:
        resultats = resultats.filter(session_id=session_id)
    return render(request, 'examens/resultats.html', {
        'resultats': resultats,
        'sessions':  SessionExamen.objects.all(),
    })