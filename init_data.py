import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fsb_system.settings')
django.setup()

from accounts.models import CustomUser
from administration.models import Departement, Filiere, Enseignant, Etudiant, Salle, Classe

print("=" * 55)
print("  INITIALISATION FSB - Faculte des Sciences de Bizerte")
print("=" * 55)

# ──────────────────────────────────────────
# 1. DEPARTEMENTS
# ──────────────────────────────────────────
print("\n--- 1. Departements ---")
depts_data = [
    ('mathematiques',  'Dr. Hamdi Salah'),
    ('informatique',   'Dr. Ben Ammar Khalil'),
    ('physique',       'Dr. Trabelsi Riadh'),
    ('chimie',         'Dr. Mbarek Sonia'),
    ('sciences_vie',   'Dr. Zouari Leila'),
    ('sciences_terre', 'Dr. Gharbi Nabil'),
]
depts = {}
for nom, chef in depts_data:
    d, created = Departement.objects.get_or_create(
        nom=nom,
        defaults=dict(chef=chef, email=f'{nom}@fsb.rnu.tn', telephone='+216 72 591 906')
    )
    depts[nom] = d
    print(f"  [{'+' if created else '='}] {d.get_nom_display()} — chef: {chef}")

di = depts['informatique']
dm = depts['mathematiques']
dp = depts['physique']
dc = depts['chimie']
db = depts['sciences_vie']
dt = depts['sciences_terre']

# ──────────────────────────────────────────
# 2. FILIERES — LICENCES
# ──────────────────────────────────────────
print("\n--- 2. Filieres Licence ---")
licences = [
    # Informatique
    ('LF-GL',    "Sciences de l'Informatique : Genie Logiciel et Systeme d'Information", di, 'L3'),
    ('LF-SE',    "Ingenierie des Systemes Informatiques : Systemes Embarques et IOT",    di, 'L3'),
    # Mathematiques
    ('LF-MATH',  "Mathematiques",                               dm, 'L3'),
    ('LF-MI',    "Mathematiques Appliquees : Math-Info",        dm, 'L3'),
    # Physique
    ('LF-GE',    "Genie Energetique : Froid et climatisation",  dp, 'L3'),
    ('LF-PE',    "Physique : Physique et energie",              dp, 'L3'),
    ('LF-PC',    "Physique chimie",                             dp, 'L3'),
    ('LF-MAT',   "Physique des Materiaux : Materiaux composites et avances", dp, 'L3'),
    ('LF-EEA',   "Electronique Electrotechnique et Automatique : Automatique et Informatique Industrielle", dp, 'L3'),
    ('LF-TIC',   "Technologie de l'information et de la communication : Communication et systemes embarques", dp, 'L3'),
    ('LF-PCAP',  "Physique : Physique des capteurs",            dp, 'L3'),
    # Chimie
    ('LF-CHIM',  "Chimie",                                      dc, 'L3'),
    ('LF-CI',    "Chimie Industrielle",                         dc, 'L3'),
    ('LF-CF',    "Chimie Fine",                                 dc, 'L3'),
    ('LF-CR',    "Chimie Recherche",                            dc, 'L3'),
    # Sciences de la vie
    ('LF-SVT',   "Sciences de la vie et de la terre",           db, 'L3'),
    ('LF-BIO',   "Sciences du vivant : Biologie moleculaire et cellulaire", db, 'L3'),
    ('LF-ENV',   "Sciences du vivant et de l'environnement : Biosurveillance des ecosystemes", db, 'L3'),
    ('LF-QA',    "Biotechnologie : Controle de Qualite des Aliments et Hygiene", db, 'L3'),
    # Sciences de la Terre
    ('LF-GEO',   "Sciences de la terre : Geo-ressources et environnement", dt, 'L3'),
    ('LF-GEOL',  "Sciences et techniques de geologie",          dt, 'L3'),
]
filieres = {}
for code, nom, dept, niveau in licences:
    f, created = Filiere.objects.get_or_create(
        code=code,
        defaults=dict(nom=nom, departement=dept, niveau=niveau, type_formation='licence')
    )
    filieres[code] = f
    print(f"  [{'+' if created else '='}] {code} — {nom[:55]}...")

# ──────────────────────────────────────────
# 3. FILIERES — MASTERS
# ──────────────────────────────────────────
print("\n--- 3. Filieres Master ---")
masters = [
    ('M-INFO',   "Master Informatique",                          di, 'M2'),
    ('M-MATH',   "Master Mathematiques",                         dm, 'M2'),
    ('M-PHYS',   "Master Physique",                              dp, 'M2'),
    ('M-CHIM',   "Master Chimie",                                dc, 'M2'),
    ('M-BIO',    "Master Biologie",                              db, 'M2'),
    ('M-GEO',    "Master Geosciences",                           dt, 'M2'),
]
for code, nom, dept, niveau in masters:
    f, created = Filiere.objects.get_or_create(
        code=code,
        defaults=dict(nom=nom, departement=dept, niveau=niveau, type_formation='master')
    )
    filieres[code] = f
    print(f"  [{'+' if created else '='}] {code} — {nom}")

# ──────────────────────────────────────────
# 4. FILIERES — DOCTORAT
# ──────────────────────────────────────────
print("\n--- 4. Filieres Doctorat ---")
doctorats = [
    ('DOC-INFO',  "Doctorat Informatique",   di, 'Doc'),
    ('DOC-MATH',  "Doctorat Mathematiques",  dm, 'Doc'),
    ('DOC-PHYS',  "Doctorat Physique",       dp, 'Doc'),
    ('DOC-CHIM',  "Doctorat Chimie",         dc, 'Doc'),
    ('DOC-BIO',   "Doctorat Biologie",       db, 'Doc'),
]
for code, nom, dept, niveau in doctorats:
    f, created = Filiere.objects.get_or_create(
        code=code,
        defaults=dict(nom=nom, departement=dept, niveau=niveau, type_formation='doctorat')
    )
    filieres[code] = f
    print(f"  [{'+' if created else '='}] {code} — {nom}")

# ──────────────────────────────────────────
# 5. FILIERES — CPI
# ──────────────────────────────────────────
print("\n--- 5. Filieres CPI ---")
cpis = [
    ('CPI-1',  "Cycle Preparatoire Integre 1ere annee", di, 'CPI'),
    ('CPI-2',  "Cycle Preparatoire Integre 2eme annee", di, 'CPI'),
]
for code, nom, dept, niveau in cpis:
    f, created = Filiere.objects.get_or_create(
        code=code,
        defaults=dict(nom=nom, departement=dept, niveau=niveau, type_formation='cpi')
    )
    filieres[code] = f
    print(f"  [{'+' if created else '='}] {code} — {nom}")

# ──────────────────────────────────────────
# 6. FILIERES — CI
# ──────────────────────────────────────────
print("\n--- 6. Filieres CI ---")
cis = [
    ('CI-1',  "Cycle Ingenieur 1ere annee", di, 'CI'),
    ('CI-2',  "Cycle Ingenieur 2eme annee", di, 'CI'),
    ('CI-3',  "Cycle Ingenieur 3eme annee", di, 'CI'),
]
for code, nom, dept, niveau in cis:
    f, created = Filiere.objects.get_or_create(
        code=code,
        defaults=dict(nom=nom, departement=dept, niveau=niveau, type_formation='ci')
    )
    filieres[code] = f
    print(f"  [{'+' if created else '='}] {code} — {nom}")

# ──────────────────────────────────────────
# 7. SALLES
# ──────────────────────────────────────────
print("\n--- 7. Salles ---")
salles_data = [
    ('Amphi A',         'amphi', 400, 'Bat. Principal'),
    ('Amphi B',         'amphi', 300, 'Bat. Principal'),
    ('Amphi C',         'amphi', 200, 'Bat. Principal'),
    ('Salle 101',       'salle',  50, 'Bat. A'),
    ('Salle 102',       'salle',  50, 'Bat. A'),
    ('Salle 201',       'salle',  40, 'Bat. B'),
    ('Salle 202',       'salle',  40, 'Bat. B'),
    ('Salle TP Info 1', 'info',   30, 'Bat. Info'),
    ('Salle TP Info 2', 'info',   30, 'Bat. Info'),
    ('Salle TP Chimie', 'tp',     25, 'Bat. Chimie'),
    ('Salle TP Bio',    'tp',     25, 'Bat. Bio'),
    ('Salle TP Phys',   'tp',     25, 'Bat. Physique'),
]
for nom, ts, cap, bat in salles_data:
    s, created = Salle.objects.get_or_create(
        nom=nom,
        defaults=dict(type_salle=ts, capacite=cap, batiment=bat)
    )
    print(f"  [{'+' if created else '='}] {s}")

# ──────────────────────────────────────────
# 8. CLASSES
# ──────────────────────────────────────────
print("\n--- 8. Classes ---")
classes_data = [
    ('GL-L3-A',  "GL L3 Groupe A",   filieres.get('LF-GL'),   'L3', 35),
    ('GL-L3-B',  "GL L3 Groupe B",   filieres.get('LF-GL'),   'L3', 35),
    ('SE-L3-A',  "SE L3 Groupe A",   filieres.get('LF-SE'),   'L3', 30),
    ('MI-L3-A',  "MI L3 Groupe A",   filieres.get('LF-MI'),   'L3', 30),
    ('SVT-L3-A', "SVT L3 Groupe A",  filieres.get('LF-SVT'),  'L3', 40),
    ('CHIM-L3',  "Chimie L3",        filieres.get('LF-CHIM'), 'L3', 35),
    ('M-INFO-A', "Master Info A",    filieres.get('M-INFO'),  'M2', 25),
    ('M-MATH-A', "Master Math A",    filieres.get('M-MATH'),  'M2', 20),
]
for code, nom, filiere, niveau, cap in classes_data:
    if filiere:
        cl, created = Classe.objects.get_or_create(
            code=code,
            defaults=dict(nom=nom, filiere=filiere, niveau=niveau,
                          annee_universitaire='2024-2025', capacite=cap)
        )
        print(f"  [{'+' if created else '='}] {code} — {nom}")
    else:
        print(f"  [!] Filiere introuvable pour {code}, ignoree")

# ──────────────────────────────────────────
# 9. ENSEIGNANTS
# ──────────────────────────────────────────
print("\n--- 9. Enseignants ---")
enseignants_data = [
    # Informatique
    ('PROF-INFO-01', 'Mohamed',  'Ben Ali',      di, 'maitre_conf',      'Bases de Donnees'),
    ('PROF-INFO-02', 'Ahmed',    'Gharbi',        di, 'assistant',        'Reseaux Informatiques'),
    ('PROF-INFO-03', 'Nadia',    'Boukadida',     di, 'maitre_assistant', 'Intelligence Artificielle'),
    ('PROF-INFO-04', 'Tarek',    'Mansour',       di, 'professeur',       'Genie Logiciel'),
    # Mathematiques
    ('PROF-MATH-01', 'Sonia',    'Mbarek',        dm, 'professeur',       'Analyse Mathematique'),
    ('PROF-MATH-02', 'Hatem',    'Triki',         dm, 'maitre_conf',      'Algebre'),
    ('PROF-MATH-03', 'Ines',     'Slama',         dm, 'maitre_assistant', 'Probabilites et Statistiques'),
    # Physique
    ('PROF-PHYS-01', 'Karim',    'Hadj',          dp, 'maitre_conf',      'Mecanique'),
    ('PROF-PHYS-02', 'Rania',    'Feki',          dp, 'assistant',        'Electronique'),
    ('PROF-PHYS-03', 'Slim',     'Ben Salah',     dp, 'professeur',       'Optique'),
    # Chimie
    ('PROF-CHIM-01', 'Leila',    'Zouari',        dc, 'maitre_assistant', 'Chimie Organique'),
    ('PROF-CHIM-02', 'Farouk',   'Dridi',         dc, 'maitre_conf',      'Chimie Analytique'),
    # Sciences de la Vie
    ('PROF-BIO-01',  'Marwa',    'Hammami',       db, 'maitre_assistant', 'Biologie Cellulaire'),
    ('PROF-BIO-02',  'Yassine',  'Jarray',        db, 'assistant',        'Biochimie'),
    # Sciences de la Terre
    ('PROF-GEO-01',  'Nabil',    'Gharbi',        dt, 'professeur',       'Geologie'),
    ('PROF-GEO-02',  'Amira',    'Chaabane',      dt, 'maitre_conf',      'Mineralogie'),
]
for matricule, prenom, nom, dept, grade, spec in enseignants_data:
    e, created = Enseignant.objects.get_or_create(
        matricule=matricule,
        defaults=dict(prenom=prenom, nom=nom, departement=dept,
                      grade=grade, specialite=spec,
                      email=f'{matricule.lower()}@fsb.rnu.tn')
    )
    print(f"  [{'+' if created else '='}] {e.get_grade_display()} {prenom} {nom} — {dept}")

# ──────────────────────────────────────────
# 10. ETUDIANTS
# ──────────────────────────────────────────
print("\n--- 10. Etudiants ---")
etudiants_data = [
    # Informatique GL
    ('20241001', 'Fatma',    'Trabelsi',  '12345678', filieres.get('LF-GL'),   2024),
    ('20241002', 'Ali',      'Hamdi',     '23456789', filieres.get('LF-GL'),   2024),
    ('20241003', 'Rim',      'Bouaziz',   '34567890', filieres.get('LF-GL'),   2024),
    ('20241004', 'Omar',     'Sfar',      '45678901', filieres.get('LF-SE'),   2024),
    ('20241005', 'Hana',     'Masmoudi',  '56789012', filieres.get('LF-SE'),   2024),
    # Mathematiques
    ('20241006', 'Mariem',   'Saidi',     '67890123', filieres.get('LF-MATH'), 2024),
    ('20241007', 'Youssef',  'Brahim',    '78901234', filieres.get('LF-MI'),   2024),
    ('20241008', 'Sarra',    'Jebali',    '89012345', filieres.get('LF-MI'),   2024),
    # Physique
    ('20241009', 'Mehdi',    'Ghariani',  '90123456', filieres.get('LF-GE'),   2024),
    ('20241010', 'Aya',      'Rekik',     '01234567', filieres.get('LF-PE'),   2024),
    # Chimie
    ('20241011', 'Sami',     'Jelassi',   '11223344', filieres.get('LF-CHIM'), 2024),
    ('20241012', 'Nour',     'Khelifi',   '22334455', filieres.get('LF-CHIM'), 2024),
    # Sciences de la Vie
    ('20241013', 'Ines',     'Ben Amor',  '33445566', filieres.get('LF-SVT'),  2024),
    ('20241014', 'Tarek',    'Mansouri',  '44556677', filieres.get('LF-BIO'),  2024),
    # Master
    ('20231001', 'Khaled',   'Ayari',     '55667788', filieres.get('M-INFO'),  2023),
    ('20231002', 'Amina',    'Dridi',     '66778899', filieres.get('M-MATH'),  2023),
]
for num, prenom, nom, cin, filiere, annee in etudiants_data:
    if filiere:
        et, created = Etudiant.objects.get_or_create(
            numero_etudiant=num,
            defaults=dict(prenom=prenom, nom=nom, cin=cin,
                          filiere=filiere, annee_inscription=annee,
                          email=f'{num}@fsb.rnu.tn')
        )
        print(f"  [{'+' if created else '='}] {num} — {prenom} {nom} ({filiere.code})")
    else:
        print(f"  [!] Filiere introuvable pour etudiant {num}, ignore")

# ──────────────────────────────────────────
# 11. AGENTS ADMINISTRATIFS
# ──────────────────────────────────────────
print("\n--- 11. Agents Administratifs ---")
agents_data = [
    ('admin',       'admin123',      'Admin',     'Systeme',    'super_admin', ''),
    ('scolarite1',  'scolarite123',  'Mouna',     'Rekik',      'scolarite',   'Tous'),
    ('scolarite2',  'scolarite123',  'Tarek',     'Bouaziz',    'scolarite',   'Tous'),
    ('chef_info',   'chef123',       'Khalil',    'Ben Ammar',  'chef_dept',   'Informatique'),
    ('chef_math',   'chef123',       'Salah',     'Hamdi',      'chef_dept',   'Mathematiques'),
    ('doyen',       'doyen123',      'Directeur', 'FSB',        'doyen',       ''),
]
for username, pwd, first, last, role, dept in agents_data:
    if not CustomUser.objects.filter(username=username).exists():
        u = CustomUser.objects.create_user(
            username=username, password=pwd,
            first_name=first, last_name=last,
            role=role, departement=dept
        )
        print(f"  [+] {username} cree (mdp: {pwd}) — role: {role}")
    else:
        print(f"  [=] {username} existe deja")

# ──────────────────────────────────────────
# RESUME FINAL
# ──────────────────────────────────────────
print("\n" + "=" * 55)
print("  INITIALISATION TERMINEE !")
print("=" * 55)
print(f"  Departements : {Departement.objects.count()}")
print(f"  Filieres     : {Filiere.objects.count()}")
print(f"    Licences   : {Filiere.objects.filter(type_formation='licence').count()}")
print(f"    Masters    : {Filiere.objects.filter(type_formation='master').count()}")
print(f"    Doctorats  : {Filiere.objects.filter(type_formation='doctorat').count()}")
print(f"    CPI        : {Filiere.objects.filter(type_formation='cpi').count()}")
print(f"    CI         : {Filiere.objects.filter(type_formation='ci').count()}")
print(f"  Classes      : {Classe.objects.count()}")
print(f"  Enseignants  : {Enseignant.objects.count()}")
print(f"  Etudiants    : {Etudiant.objects.count()}")
print(f"  Salles       : {Salle.objects.count()}")
print(f"  Agents admin : {CustomUser.objects.count()}")
print("=" * 55)
print("\n  COMPTES AGENTS :")
print("  super_admin : admin      / admin123")
print("  scolarite   : scolarite1 / scolarite123")
print("  scolarite   : scolarite2 / scolarite123")
print("  chef_dept   : chef_info  / chef123")
print("  chef_dept   : chef_math  / chef123")
print("  doyen       : doyen      / doyen123")
print("=" * 55)