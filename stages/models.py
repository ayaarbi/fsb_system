from django.db import models
from administration.models import Etudiant, Enseignant

class DemandeStage(models.Model):
    TYPE_CHOICES = [
        ('observation','Stage Observation'),
        ('pfe','PFE'),
        ('initiation','Stage Initiation'),
    ]
    STATUT_CHOICES = [
        ('en_attente','En Attente'),('valide','Validé'),
        ('refuse','Refusé'),('en_cours','En Cours'),('termine','Terminé'),
    ]
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    type_stage = models.CharField(max_length=20, choices=TYPE_CHOICES)
    entreprise = models.CharField(max_length=200)
    sujet = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    encadrant_fsb = models.ForeignKey(Enseignant, on_delete=models.SET_NULL,
                                      null=True, blank=True)
    encadrant_entreprise = models.CharField(max_length=100, blank=True)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES,
                              default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)
    rapport = models.FileField(upload_to='rapports_stage/', blank=True, null=True)
    note_stage = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.etudiant} - {self.sujet[:50]}"


class Diplome(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    type_diplome = models.CharField(max_length=50)
    specialite = models.CharField(max_length=100)
    annee_obtention = models.IntegerField()
    mention = models.CharField(max_length=30, choices=[
        ('passable','Passable'),('assez_bien','Assez Bien'),
        ('bien','Bien'),('tres_bien','Très Bien'),
    ], blank=True)
    moyenne_generale = models.FloatField(null=True, blank=True)
    numero_diplome = models.CharField(max_length=50, unique=True)
    date_delivrance = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Diplôme {self.type_diplome} - {self.etudiant}"