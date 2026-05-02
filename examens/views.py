from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SessionExamen, PlanningExamen, ResultatExamen
from administration.models import Salle
from pedagogie.models import Matiere

@login_required
def liste_sessions(request):
    return render(request, 'examens/sessions.html',
                  {'sessions': SessionExamen.objects.order_by('-date_debut')})

@login_required
def ajouter_session(request):
    if request.method == 'POST':
        SessionExamen.objects.create(
            nom=request.POST['nom'],
            type_session=request.POST['type_session'],
            annee_universitaire=request.POST['annee_univ'],
            semestre=request.POST['semestre'],
            date_debut=request.POST['date_debut'],
            date_fin=request.POST['date_fin'],
        )
        messages.success(request, "Session créée!")
        return redirect('examens:sessions')
    return render(request, 'examens/ajouter_session.html')

@login_required
def planning_examens(request):
    session_id = request.GET.get('session')
    plannings = PlanningExamen.objects.select_related('matiere', 'salle', 'session')
    if session_id:
        plannings = plannings.filter(session_id=session_id)
    if request.method == 'POST':
        PlanningExamen.objects.create(
            session_id=request.POST['session'],
            matiere_id=request.POST['matiere'],
            salle_id=request.POST['salle'],
            date=request.POST['date'],
            heure_debut=request.POST['heure_debut'],
            heure_fin=request.POST['heure_fin'],
        )
        messages.success(request, "Examen planifié!")
    return render(request, 'examens/planning.html', {
        'plannings': plannings,
        'sessions': SessionExamen.objects.all(),
        'matieres': Matiere.objects.all(),
        'salles': Salle.objects.all(),
    })

@login_required
def resultats(request):
    session_id = request.GET.get('session')
    resultats = ResultatExamen.objects.select_related(
        'etudiant__user', 'matiere', 'session')
    if session_id:
        resultats = resultats.filter(session_id=session_id)
    return render(request, 'examens/resultats.html', {
        'resultats': resultats, 'sessions': SessionExamen.objects.all(),
    })