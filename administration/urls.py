from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    # Dashboard
    path('',                              views.dashboard,            name='dashboard'),

    # Étudiants
    path('etudiants/',                    views.liste_etudiants,      name='liste_etudiants'),
    path('etudiants/ajouter/',            views.ajouter_etudiant,     name='ajouter_etudiant'),
    path('etudiants/<int:pk>/',           views.detail_etudiant,      name='detail_etudiant'),
    path('etudiants/<int:pk>/modifier/',  views.modifier_etudiant,    name='modifier_etudiant'),
    path('etudiants/<int:etudiant_id>/releve/', views.releve_notes,   name='releve_notes'),

    # Enseignants
    path('enseignants/',                  views.liste_enseignants,    name='liste_enseignants'),
    path('enseignants/ajouter/',          views.ajouter_enseignant,   name='ajouter_enseignant'),
    path('enseignants/<int:pk>/',         views.detail_enseignant,    name='detail_enseignant'),
    path('enseignants/<int:pk>/modifier/',views.modifier_enseignant,  name='modifier_enseignant'),

    # Inscriptions & Salles
    path('inscriptions/',                 views.gestion_inscriptions, name='inscriptions'),
    path('inscriptions/<int:pk>/valider/',views.valider_inscription,  name='valider_inscription'),
    path('salles/',                       views.gestion_salles,       name='salles'),
]