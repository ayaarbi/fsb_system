from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('doyen', 'Doyen'),
        ('chef_dept', 'Chef de Département'),
        ('enseignant', 'Enseignant'),
        ('etudiant', 'Étudiant'),
        ('scolarite', 'Service Scolarité'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    telephone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_etudiant(self):
        return self.role == 'etudiant'

    @property
    def is_enseignant(self):
        return self.role == 'enseignant'

    @property
    def is_admin_staff(self):
        return self.role in ['admin', 'doyen', 'scolarite', 'chef_dept']