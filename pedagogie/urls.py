from django.urls import path
from . import views

app_name = 'pedagogie'

urlpatterns = [
    # Matières — navigation
    path('matieres/',
         views.matieres_departements,
         name='matieres'),
    path('matieres/departement/<int:dept_id>/',
         views.matieres_filieres,
         name='matieres_filieres'),
    path('matieres/departement/<int:dept_id>/filiere/<int:filiere_id>/',
         views.matieres_liste,
         name='matieres_liste'),
    path('matieres/ajouter/',
         views.ajouter_matiere,
         name='ajouter_matiere'),
    path('matieres/<int:pk>/modifier/',
         views.modifier_matiere,
         name='modifier_matiere'),
    path('matieres/<int:pk>/supprimer/',
         views.supprimer_matiere,
         name='supprimer_matiere'),

    # Emploi du temps
    path('emploi-du-temps/',
         views.emploi_du_temps,
         name='emploi_du_temps'),

    # Absences
    path('absences/',
         views.gestion_absences,
         name='absences'),

    # Notes
    path('notes/',
         views.saisie_notes,
         name='notes'),
    path('notes/liste/',
         views.liste_notes,
         name='liste_notes'),
]