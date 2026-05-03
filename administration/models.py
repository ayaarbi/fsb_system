from django.db import models

# ──────────────────────────────────────────
# DÉPARTEMENTS & FILIÈRES
# ──────────────────────────────────────────

class Departement(models.Model):
    NOM_CHOICES = [
        ('mathematiques',  'Mathématiques'),
        ('informatique',   'Informatique'),
        ('physique',       'Physique'),
        ('chimie',         'Chimie'),
        ('biologie',   'Biologie'),
        ('geologie', 'Géologie'),
    ]
    nom         = models.CharField(max_length=50, choices=NOM_CHOICES, unique=True)
    chef        = models.CharField(max_length=100, blank=True, null=True, help_text="Nom du chef de département")
    email       = models.EmailField(blank=True)
    telephone   = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.get_nom_display()


class Filiere(models.Model):
    NIVEAU_CHOICES = [
        ('L1','Licence 1'), ('L2','Licence 2'), ('L3','Licence 3'),
        ('M1','Master 1'),  ('M2','Master 2'),  ('Doc','Doctorat'),
        ('CPI','Cycle Préparatoire Intégré'), ('CI','Cycle Ingénieur'),
    ]
    TYPE_CHOICES = [
        ('licence',    'Licence'),
        ('master',     'Master'),
        ('doctorat',   'Doctorat'),
        ('cpi',        'CPI'),
        ('ci',         'CI'),
    ]
    nom            = models.CharField(max_length=100)
    code           = models.CharField(max_length=20, unique=True)
    departement    = models.ForeignKey(
        Departement, on_delete=models.CASCADE, related_name='filieres'
    )
    niveau         = models.CharField(max_length=5, choices=NIVEAU_CHOICES)
    type_formation = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='licence'
    )
    description    = models.TextField(blank=True, default='')

    def nb_etudiants(self):
        return Etudiant.objects.filter(filiere=self, statut='inscrit').count()

    def nb_enseignants(self):
        return Enseignant.objects.filter(
            departement=self.departement, actif=True
        ).count()

    def __str__(self):
        return f"{self.code} — {self.nom}"


class Classe(models.Model):
    NIVEAU_CHOICES = [
        ('L1', 'Licence 1'), ('L2', 'Licence 2'), ('L3', 'Licence 3'),
        ('M1', 'Master 1'),  ('M2', 'Master 2'),
        ('Doc1', 'Doctorat 1'), ('Doc2', 'Doctorat 2'), ('Doc3', 'Doctorat 3'),
        ('CPI1', 'Cycle Préparatoire Intégré 1'), ('CPI2', 'Cycle Préparatoire Intégré 2'),
        ('CI1', 'Cycle Ingénieur 1'),   ('CI2', 'Cycle Ingénieur 2'), ('CI3', 'Cycle Ingénieur 3'),
    ]
    nom      = models.CharField(max_length=100)
    code     = models.CharField(max_length=20, unique=True)
    filiere  = models.ForeignKey(
        Filiere, on_delete=models.CASCADE, related_name='classes'
    )
    niveau   = models.CharField(max_length=10, choices=NIVEAU_CHOICES)
    annee_universitaire = models.CharField(max_length=9, default='2024-2025')
    capacite = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.code} — {self.nom}"

    def nb_etudiants(self):
        return Etudiant.objects.filter(
            filiere=self.filiere, statut='inscrit'
        ).count()

# ──────────────────────────────────────────
# ENSEIGNANTS  (données gérées par l'admin)
# ──────────────────────────────────────────

class Enseignant(models.Model):
    GRADE_CHOICES = [
        ('assistant',        'Assistant'),
        ('maitre_assistant', 'Maître Assistant'),
        ('maitre_conf',      'Maître de Conférences'),
        ('professeur',       'Professeur'),
    ]
    nom              = models.CharField(max_length=100,null=True, blank=True)
    prenom           = models.CharField(max_length=100,null=True, blank=True)
    matricule        = models.CharField(max_length=20, unique=True)
    email            = models.EmailField(blank=True)
    telephone        = models.CharField(max_length=20, blank=True)
    departement      = models.ForeignKey(Departement, on_delete=models.SET_NULL,
                                         null=True, related_name='enseignants')
    grade            = models.CharField(max_length=30, choices=GRADE_CHOICES)
    specialite       = models.CharField(max_length=100, blank=True)
    date_recrutement = models.DateField(null=True, blank=True)
    actif            = models.BooleanField(default=True)

    def get_full_name(self):
        return f"{self.prenom} {self.nom}"

    def __str__(self):
        return f"{self.get_grade_display()} {self.get_full_name()}"


# ──────────────────────────────────────────
# ÉTUDIANTS  (données gérées par l'admin)
# ──────────────────────────────────────────

class Etudiant(models.Model):
    STATUT_CHOICES = [
        ('inscrit',   'Inscrit'),
        ('suspendu',  'Suspendu'),
        ('diplome',   'Diplômé'),
        ('abandonne', 'Abandonné'),
    ]
    nom               = models.CharField(max_length=100,null=True, blank=True)
    prenom            = models.CharField(max_length=100,null=True, blank=True)
    numero_etudiant   = models.CharField(max_length=20, unique=True)
    cin               = models.CharField(max_length=20, blank=True)
    email             = models.EmailField(blank=True)
    telephone         = models.CharField(max_length=20, blank=True)
    filiere           = models.ForeignKey(Filiere, on_delete=models.SET_NULL,
                                          null=True, related_name='etudiants')
    annee_inscription = models.IntegerField()
    date_naissance    = models.DateField(null=True, blank=True)
    lieu_naissance    = models.CharField(max_length=100, blank=True)
    adresse           = models.TextField(blank=True)
    statut            = models.CharField(max_length=20, choices=STATUT_CHOICES,
                                         default='inscrit')

    def get_full_name(self):
        return f"{self.prenom} {self.nom}"

    def __str__(self):
        return f"{self.numero_etudiant} — {self.get_full_name()}"


class Salle(models.Model):
    TYPE_CHOICES = [
        ('amphi', 'Amphithéâtre'),
        ('salle', 'Salle de Cours'),
        ('tp',    'Salle TP'),
        ('info',  'Salle Informatique'),
    ]
    nom        = models.CharField(max_length=50)
    type_salle = models.CharField(max_length=10, choices=TYPE_CHOICES)
    capacite   = models.IntegerField()
    batiment   = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.get_type_salle_display()}, {self.capacite} pl.)"


class Inscription(models.Model):
    etudiant            = models.ForeignKey(Etudiant, on_delete=models.CASCADE,
                                            related_name='inscriptions')
    filiere             = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    annee_universitaire = models.CharField(max_length=9)
    date_inscription    = models.DateField(auto_now_add=True)
    valide              = models.BooleanField(default=False)

    class Meta:
        unique_together = ['etudiant', 'annee_universitaire']

    def __str__(self):
        return f"{self.etudiant} — {self.annee_universitaire}"