from django.db import models
from accounts.models import CustomUser

class Departement(models.Model):
    NOM_CHOICES = [
        ('mathematiques', 'Mathématiques'),
        ('informatique', 'Informatique'),
        ('physique', 'Physique'),
        ('chimie', 'Chimie'),
        ('sciences_vie', 'Sciences de la Vie'),
        ('sciences_terre', 'Sciences de la Terre'),
    ]
    nom = models.CharField(max_length=50, choices=NOM_CHOICES, unique=True)
    chef = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='dept_dirige')
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.get_nom_display()


class Filiere(models.Model):
    NIVEAU_CHOICES = [
        ('L1','Licence 1'),('L2','Licence 2'),('L3','Licence 3'),
        ('M1','Master 1'),('M2','Master 2'),('Doc','Doctorat'),
    ]
    TYPE_CHOICES = [
        ('fondamentale','Fondamentale'),
        ('appliquee','Appliquée'),
        ('professionnelle','Professionnelle'),
    ]
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE,
                                    related_name='filieres')
    niveau = models.CharField(max_length=5, choices=NIVEAU_CHOICES)
    type_formation = models.CharField(max_length=20, choices=TYPE_CHOICES,
                                      default='fondamentale')

    def __str__(self):
        return f"{self.code} - {self.nom}"


class Enseignant(models.Model):
    GRADE_CHOICES = [
        ('assistant', 'Assistant'),
        ('maitre_assistant', 'Maître Assistant'),
        ('maitre_conf', 'Maître de Conférences'),
        ('professeur', 'Professeur'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,
                                related_name='enseignant_profile')
    matricule = models.CharField(max_length=20, unique=True)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True)
    grade = models.CharField(max_length=30, choices=GRADE_CHOICES)
    specialite = models.CharField(max_length=100)
    date_recrutement = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_grade_display()} {self.user.get_full_name()}"


class Etudiant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,
                                related_name='etudiant_profile')
    numero_etudiant = models.CharField(max_length=20, unique=True)
    cin = models.CharField(max_length=20, unique=True, blank=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.SET_NULL, null=True)
    annee_inscription = models.IntegerField()
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=100, blank=True)
    adresse = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=[
        ('inscrit','Inscrit'),('suspendu','Suspendu'),
        ('diplome','Diplômé'),('abandonne','Abandonné'),
    ], default='inscrit')

    def __str__(self):
        return f"{self.numero_etudiant} - {self.user.get_full_name()}"


class Salle(models.Model):
    TYPE_CHOICES = [
        ('amphi','Amphithéâtre'),('salle','Salle'),
        ('tp','Salle TP'),('info','Salle Informatique'),
    ]
    nom = models.CharField(max_length=50)
    type_salle = models.CharField(max_length=10, choices=TYPE_CHOICES)
    capacite = models.IntegerField()
    batiment = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.get_type_salle_display()}, cap: {self.capacite})"


class Inscription(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    annee_universitaire = models.CharField(max_length=9)
    date_inscription = models.DateField(auto_now_add=True)
    valide = models.BooleanField(default=False)

    class Meta:
        unique_together = ['etudiant', 'annee_universitaire']

    def __str__(self):
        return f"{self.etudiant} - {self.annee_universitaire}"