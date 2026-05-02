import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fsb_system.settings')
django.setup()

from accounts.models import CustomUser
from administration.models import Departement, Filiere, Enseignant, Etudiant, Salle

print("--- Creation des departements ---")
for nom in ['mathematiques','informatique','physique','chimie','biologie','geologie']:
    d, c = Departement.objects.get_or_create(nom=nom)
    print(f"  {d} : {'cree' if c else 'existe'}")

print("--- Creation des filieres ---")
di = Departement.objects.get(nom='informatique')
dm = Departement.objects.get(nom='mathematiques')
db = Departement.objects.get(nom='biologie')
dp = Departement.objects.get(nom='physique')

filieres = [
    ('LF-INFO','Licence Fondamentale Informatique',di,'L3','fondamentale'),
    ('LF-MATH','Licence Fondamentale Mathematiques',dm,'L3','fondamentale'),
    ('LF-SVT', 'Licence Fondamentale Sciences de la Vie',db,'L3','fondamentale'),
    ('LF-PHYS','Licence Fondamentale Physique',dp,'L3','fondamentale'),
    ('M-INFO', 'Master Informatique',di,'M2','fondamentale'),
    ('M-MATH', 'Master Mathematiques',dm,'M2','fondamentale'),
]
for code, nom, dept, niveau, tf in filieres:
    f, c = Filiere.objects.get_or_create(code=code, defaults=dict(nom=nom,departement=dept,niveau=niveau,type_formation=tf))
    print(f"  {f.code} : {'cree' if c else 'existe'}")

print("--- Creation des salles ---")
for nom, ts, cap, bat in [
    ('Amphi A','amphi',400,'Bat. Principal'),
    ('Amphi B','amphi',250,'Bat. Principal'),
    ('Salle 101','salle',50,'Bat. A'),
    ('Salle TP Info','info',30,'Bat. B'),
    ('Salle TP Chimie','tp',25,'Bat. C'),
]:
    s, c = Salle.objects.get_or_create(nom=nom, defaults=dict(type_salle=ts,capacite=cap,batiment=bat))
    print(f"  {s} : {'cree' if c else 'existe'}")

print("--- Creation des enseignants (donnees seulement, sans compte) ---")
enseignants = [
    ('Mohamed','Ben Ali','PROF001',di,'maitre_conf','Bases de Donnees'),
    ('Sonia','Mbarek','PROF002',dm,'professeur','Analyse Mathematique'),
    ('Karim','Hadj','PROF003',dp,'maitre_conf','Mecanique'),
    ('Leila','Zouari','PROF004',db,'maitre_assistant','Biologie Cellulaire'),
    ('Ahmed','Gharbi','PROF005',di,'assistant','Reseaux Informatiques'),
]
for prenom, nom, matricule, dept, grade, spec in enseignants:
    e, c = Enseignant.objects.get_or_create(matricule=matricule, defaults=dict(prenom=prenom,nom=nom,departement=dept,grade=grade,specialite=spec))
    print(f"  {e} : {'cree' if c else 'existe'}")

print("--- Creation des etudiants (donnees seulement, sans compte) ---")
f_info = Filiere.objects.get(code='LF-INFO')
f_math = Filiere.objects.get(code='LF-MATH')
etudiants = [
    ('Fatma','Trabelsi','20241001','12345678',f_info),
    ('Ali','Hamdi','20241002','23456789',f_info),
    ('Mariem','Saidi','20241003','34567890',f_math),
    ('Youssef','Brahim','20241004','45678901',f_info),
    ('Amira','Chaabane','20241005','56789012',f_math),
]
for prenom, nom, num, cin, filiere in etudiants:
    et, c = Etudiant.objects.get_or_create(numero_etudiant=num, defaults=dict(prenom=prenom,nom=nom,cin=cin,filiere=filiere,annee_inscription=2024))
    print(f"  {et} : {'cree' if c else 'existe'}")

print("--- Creation des agents administratifs ---")
agents = [
    ('admin','admin123','Admin','Systeme','super_admin'),
    ('scolarite1','scolarite123','Mouna','Rekik','scolarite'),
    ('scolarite2','scolarite123','Tarek','Bouaziz','scolarite'),
    ('chef_info','chef123','Directeur','Informatique','chef_dept'),
]
for username, pwd, first, last, role in agents:
    if not CustomUser.objects.filter(username=username).exists():
        u = CustomUser.objects.create_user(username=username,password=pwd,
            first_name=first,last_name=last,role=role)
        print(f"  Agent {username} cree (mdp: {pwd})")
    else:
        print(f"  Agent {username} : existe deja")

print("\n================================================")
print("Initialisation terminee !")
print("Comptes agents admin disponibles :")
print("  super_admin : admin       / admin123")
print("  scolarite   : scolarite1  / scolarite123")
print("  scolarite   : scolarite2  / scolarite123")
print("  chef_dept   : chef_info   / chef123")
print("================================================")
print("IMPORTANT: Les etudiants et enseignants sont")
print("des DONNEES gerees par les agents, pas des utilisateurs.")
print("================================================")