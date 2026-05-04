from django.urls import path
from . import views

app_name = 'examens'

urlpatterns = [
    path('sessions/',
         views.liste_sessions,
         name='sessions'),
    path('sessions/ajouter/',
         views.ajouter_session,
         name='ajouter_session'),
    path('planning/',
         views.planning_examens,
         name='planning'),
    path('planning/<int:pk>/supprimer/',
         views.supprimer_planning,
         name='supprimer_planning'),
    path('resultats/',
         views.resultats,
         name='resultats'),
]