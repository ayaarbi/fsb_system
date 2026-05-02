from django.urls import path
from . import views
app_name = 'administration'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('etudiants/', views.liste_etudiants, name='liste_etudiants'),
    path('etudiants/ajouter/', views.ajouter_etudiant, name='ajouter_etudiant'),
    path('etudiants/<int:pk>/', views.detail_etudiant, name='detail_etudiant'),
    path('enseignants/', views.liste_enseignants, name='liste_enseignants'),
    path('enseignants/ajouter/', views.ajouter_enseignant, name='ajouter_enseignant'),
    path('enseignants/<int:pk>/', views.detail_enseignant, name='detail_enseignant'),
    path('inscriptions/', views.gestion_inscriptions, name='inscriptions'),
    path('salles/', views.gestion_salles, name='salles'),
    path('releve-notes/<int:etudiant_id>/', views.releve_notes, name='releve_notes'),
]