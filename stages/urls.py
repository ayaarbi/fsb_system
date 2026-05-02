from django.urls import path
from . import views

app_name = 'stages'

urlpatterns = [
    path('demandes/',              views.liste_demandes,  name='demandes'),
    path('demandes/nouvelle/',     views.nouvelle_demande,name='nouvelle_demande'),
    path('demandes/<int:pk>/',     views.detail_demande,  name='detail_demande'),
    path('diplomes/',              views.liste_diplomes,  name='diplomes'),
    path('diplomes/ajouter/',      views.ajouter_diplome, name='ajouter_diplome'),
]