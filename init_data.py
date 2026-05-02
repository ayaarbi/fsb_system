import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fsb_system.settings')
django.setup()

from accounts.models import CustomUser
from administration.models import Departement, Filiere, Enseignant, Etudiant, Salle

print("--- Creation des departements FSB ---")
departements = [
    'mathematiques',
    'informatique',
    'physique',
    'chimie',
    'sciences_vie',
    'sciences_terre',
]
for nom in departements:
    obj, created = Departement.objects.get_or_create(nom=nom)
    status = "cree" if created else "existe deja"
    print(f"  Departement {nom}: {status}")

print("--- Creation des filieres ---")
dept_info = Departement.objects.get(nom='informatique')
dept_math = Departement.objects.get(nom='mathematiques')
dept_bio  = Departement.objects.get(nom='sciences_vie')
dept_phys = Departement.objects.get(nom='physique')
dept_chim = Departement.objects.get(nom='chimie')

filieres = [
    ('LF-INFO', 'Licence Fondamentale Informatique',       dept_info, 'L3', 'fondamentale'),
    ('LF-MATH', 'Licence Fondamentale Mathematiques',      dept_math, 'L3', 'fondamentale'),
    ('LF-SVT',  'Licence Fondamentale Sciences de la Vie', dept_bio,  'L3', 'fondamentale'),
    ('LF-PHYS', 'Licence Fondamentale Physique',           dept_phys, 'L3', 'fondamentale'),
    ('LF-CHIM', 'Licence Fondamentale Chimie',             dept_chim, 'L3', 'fondamentale'),
    ('M-INFO',  'Master Informatique',                     dept_info, 'M2', 'fondamentale'),
    ('M-MATH',  'Master Mathematiques',                    dept_math, 'M2', 'fondamentale'),
    ('M-BIO',   'Master Biologie',                         dept_bio,  'M2', 'fondamentale'),
]
for code, nom, dept, niveau, type_f in filieres:
    obj, created = Filiere.objects.get_or_create(
        code=code,
        defaults=dict(nom=nom, departement=dept, niveau=niveau, type_formation=type_f)
    )
    status = "cree" if created else "existe deja"
    print(f"  Filiere {code}: {status}")

print("--- Creation des salles ---")
salles = [
    ('Amphi A',        'amphi', 400, 'Bat. Principal'),
    ('Amphi B',        'amphi', 300, 'Bat. Principal'),
    ('Amphi C',        'amphi', 250, 'Bat. Principal'),
    ('Salle 101',      'salle',  50, 'Bat. A'),
    ('Salle 102',      'salle',  50, 'Bat. A'),
    ('Salle 201',      'salle',  40, 'Bat. B'),
    ('Salle TP Info',  'info',   30, 'Bat. B'),
    ('Salle TP Chimie','tp',     25, 'Bat. C'),
    ('Salle TP Bio',   'tp',     25, 'Bat. C'),
]
for nom, type_s, cap, bat in salles:
    obj, created = Salle.objects.get_or_create(
        nom=nom,
        defaults=dict(type_salle=type_s, capacite=cap, batiment=bat)
    )
    status = "cree" if created else "existe deja"
    print(f"  Salle {nom}: {status}")

print("--- Creation des enseignants ---")
enseignants_data = [
    ('prof001', 'Mohamed',  'Ben Ali',    'prof@fsb.ucar.tn',    'PROF001', dept_info, 'maitre_conf',    'Bases de Donnees'),
    ('prof002', 'Sonia',    'Mbarek',     'sonia@fsb.ucar.tn',   'PROF002', dept_math, 'professeur',     'Analyse'),
    ('prof003', 'Karim',    'Hadj',       'karim@fsb.ucar.tn',   'PROF003', dept_phys, 'maitre_conf',    'Mecanique'),
    ('prof004', 'Leila',    'Zouari',     'leila@fsb.ucar.tn',   'PROF004', dept_bio,  'maitre_assistant','Biologie Cellulaire'),
    ('prof005', 'Ahmed',    'Gharbi',     'ahmed@fsb.ucar.tn',   'PROF005', dept_info, 'assistant',      'Reseaux'),
]
for username, prenom, nom, email, matricule, dept, grade, specialite in enseignants_data:
    if not CustomUser.objects.filter(username=username).exists():
        u = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=username,
            first_name=prenom,
            last_name=nom,
            role='enseignant',
        )
        Enseignant.objects.create(
            user=u,
            matricule=matricule,
            departement=dept,
            grade=grade,
            specialite=specialite,
        )
        print(f"  Enseignant {username} cree (mdp: {username})")
    else:
        print(f"  Enseignant {username}: existe deja")

print("--- Creation des etudiants ---")
f_info = Filiere.objects.get(code='LF-INFO')
f_math = Filiere.objects.get(code='LF-MATH')
f_bio  = Filiere.objects.get(code='LF-SVT')

etudiants_data = [
    ('20241001', 'Fatma',    'Trabelsi', 'fatma@fsb.ucar.tn',   '12345678', f_info),
    ('20241002', 'Ali',      'Hamdi',    'ali@fsb.ucar.tn',     '23456789', f_info),
    ('20241003', 'Mariem',   'Saidi',    'mariem@fsb.ucar.tn',  '34567890', f_math),
    ('20241004', 'Youssef',  'Brahim',   'youssef@fsb.ucar.tn', '45678901', f_bio),
    ('20241005', 'Amira',    'Chaabane', 'amira@fsb.ucar.tn',   '56789012', f_info),
    ('20241006', 'Sami',     'Jelassi',  'sami@fsb.ucar.tn',    '67890123', f_math),
]
for numero, prenom, nom, email, cin, filiere in etudiants_data:
    if not CustomUser.objects.filter(username=numero).exists():
        u = CustomUser.objects.create_user(
            username=numero,
            email=email,
            password=numero,
            first_name=prenom,
            last_name=nom,
            role='etudiant',
        )
        Etudiant.objects.create(
            user=u,
            numero_etudiant=numero,
            cin=cin,
            filiere=filiere,
            annee_inscription=2024,
        )
        print(f"  Etudiant {numero} ({prenom} {nom}) cree (mdp: {numero})")
    else:
        print(f"  Etudiant {numero}: existe deja")

print("")
print("================================================")
print("Donnees FSB initialisees avec succes!")
print("================================================")
print("")
print("Comptes disponibles:")
print("  Admin      : admin       / (votre mdp createsuperuser)")
print("  Enseignant : prof001     / prof001")
print("  Enseignant : prof002     / prof002")
print("  Etudiant   : 20241001    / 20241001")
print("  Etudiant   : 20241002    / 20241002")
print("  Etudiant   : 20241003    / 20241003")
print("================================================")