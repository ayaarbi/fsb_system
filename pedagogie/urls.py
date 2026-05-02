from django.urls import path
from . import views
app_name = 'pedagogie'
urlpatterns = [
    path('matieres/', views.liste_matieres, name='matieres'),
    path('emploi-du-temps/', views.emploi_du_temps, name='emploi_du_temps'),
    path('absences/', views.gestion_absences, name='absences'),
    path('notes/', views.saisie_notes, name='notes'),
    path('notes/liste/', views.liste_notes, name='liste_notes'),
]