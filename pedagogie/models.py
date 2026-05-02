from django.db import models
from administration.models import Enseignant, Filiere, Salle, Etudiant


class Matiere(models.Model):
    nom         = models.CharField(max_length=100)
    code        = models.CharField(max_length=20, unique=True)
    filiere     = models.ForeignKey(Filiere, on_delete=models.CASCADE,
                                    related_name='matieres')
    credits     = models.IntegerField(default=3)
    coefficient = models.FloatField(default=1.0)
    heures_cours= models.IntegerField(default=0)
    heures_td   = models.IntegerField(default=0)
    heures_tp   = models.IntegerField(default=0)
    semestre    = models.IntegerField(choices=[(1,'S1'),(2,'S2')])

    def __str__(self):
        return f"{self.code} — {self.nom}"


class EmploiDuTemps(models.Model):
    JOUR_CHOICES = [
        (1,'Lundi'),(2,'Mardi'),(3,'Mercredi'),
        (4,'Jeudi'),(5,'Vendredi'),(6,'Samedi'),
    ]
    TYPE_CHOICES = [('cours','Cours'),('td','TD'),('tp','TP')]

    matiere             = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    enseignant          = models.ForeignKey(Enseignant, on_delete=models.SET_NULL,
                                            null=True, blank=True)
    salle               = models.ForeignKey(Salle, on_delete=models.SET_NULL,
                                            null=True, blank=True)
    jour                = models.IntegerField(choices=JOUR_CHOICES)
    heure_debut         = models.TimeField()
    heure_fin           = models.TimeField()
    type_seance         = models.CharField(max_length=10, choices=TYPE_CHOICES)
    annee_universitaire = models.CharField(max_length=9)
    semestre            = models.IntegerField(choices=[(1,'S1'),(2,'S2')])

    def __str__(self):
        return f"{self.matiere} — {self.get_jour_display()} {self.heure_debut}"


class Absence(models.Model):
    etudiant  = models.ForeignKey(Etudiant, on_delete=models.CASCADE,
                                  related_name='absences')
    seance    = models.ForeignKey(EmploiDuTemps, on_delete=models.CASCADE)
    date      = models.DateField()
    justifiee = models.BooleanField(default=False)
    motif     = models.TextField(blank=True)

    class Meta:
        unique_together = ['etudiant', 'seance', 'date']

    def __str__(self):
        return f"{self.etudiant} absent le {self.date}"


class Note(models.Model):
    TYPE_CHOICES = [
        ('ds',         'DS'),
        ('exam',       'Examen'),
        ('tp',         'TP'),
        ('expose',     'Exposé'),
        ('rattrapage', 'Rattrapage'),
    ]
    etudiant            = models.ForeignKey(Etudiant, on_delete=models.CASCADE,
                                            related_name='notes')
    matiere             = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    type_note           = models.CharField(max_length=15, choices=TYPE_CHOICES)
    note                = models.FloatField()
    annee_universitaire = models.CharField(max_length=9)
    semestre            = models.IntegerField(choices=[(1,'S1'),(2,'S2')])
    date_saisie         = models.DateField(auto_now_add=True)
    enseignant          = models.ForeignKey(Enseignant, on_delete=models.SET_NULL,
                                            null=True, blank=True)
    saisie_par          = models.CharField(max_length=100, blank=True,
                                           help_text="Agent qui a saisi la note")

    class Meta:
        unique_together = ['etudiant','matiere','type_note',
                           'annee_universitaire','semestre']

    def __str__(self):
        return f"{self.etudiant} — {self.matiere}: {self.note}"