# init_data.py
# -*- coding: utf-8 -*-

import os
import django

from datetime import date, timedelta, time

from django.db import transaction
from django.db.models import Count, Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fsb_system.settings")
django.setup()

from accounts.models import CustomUser

from administration.models import (
    Departement,
    Filiere,
    Enseignant,
    Etudiant,
    Salle,
    Classe,
)

from pedagogie.models import (
    Matiere,
    EmploiDuTemps,
    Absence,
    Note,
    MoyenneEtudiant,
)

from examens.models import SessionExamen

from stages.models import (
    DemandeStage,
    Diplome,
)

ANNEE = "2024-2025"

JOURS = {
    "lundi": 1,
    "mardi": 2,
    "mercredi": 3,
    "jeudi": 4,
    "vendredi": 5,
    "samedi": 6,
}


@transaction.atomic
def run():

    print("=" * 60)
    print("INITIALISATION FSB")
    print("=" * 60)

    # =========================================================
    # DEPARTEMENTS
    # =========================================================

    print("\n--- DEPARTEMENTS ---")

    depts_data = [
        ("mathematiques", "Khelifi Abdesattar"),
        ("informatique", "Kacem Fedi"),
        ("physique", "Dhifaoui Belgacem"),
        ("chimie", "Mahnaoui Mohamed"),
        ("biologie", "Ben Rhouma Khemais"),
        ("geologie", "Boughdiri Mabrouk"),
    ]

    depts = {}

    for nom, chef in depts_data:

        d, _ = Departement.objects.update_or_create(
            nom=nom,
            defaults={
                "chef": chef,
                "email": f"{nom}@fsb.tn",
                "telephone": "+21672591906",
            },
        )

        depts[nom] = d

    di = depts["informatique"]
    dm = depts["mathematiques"]
    dp = depts["physique"]
    dc = depts["chimie"]
    db = depts["biologie"]

    # =========================================================
    # FILIERES
    # =========================================================

    print("\n--- FILIERES ---")

    filieres_data = [
        ("LF-GL", "Génie Logiciel", di, "L3", "licence"),
        ("LF-SE", "Systèmes Embarqués", di, "L3", "licence"),
        ("LF-MI", "Math Info", dm, "L3", "licence"),
        ("LF-MATH", "Mathématiques", dm, "L3", "licence"),
        ("LF-PE", "Physique Énergie", dp, "L3", "licence"),
        ("LF-CHIM", "Chimie", dc, "L3", "licence"),
        ("LF-SVT", "Sciences de la Vie", db, "L3", "licence"),
        ("M-INFO", "Master Informatique", di, "M2", "master"),
    ]

    filieres = {}

    for code, nom, dept, niveau, tf in filieres_data:

        f, _ = Filiere.objects.update_or_create(
            code=code,
            defaults={
                "nom": nom,
                "departement": dept,
                "niveau": niveau,
                "type_formation": tf,
            },
        )

        filieres[code] = f

    # =========================================================
    # SALLES
    # =========================================================

    print("\n--- SALLES ---")

    salles_data = [
        ("Amphi A", "amphi", 300, "Bloc A"),
        ("Salle 101", "salle", 40, "Bloc B"),
        ("Salle 102", "salle", 40, "Bloc B"),
        ("Salle TP Info", "info", 25, "Bloc Info"),
        ("Salle TP Chimie", "tp", 20, "Bloc Chimie"),
    ]

    salles = {}

    for nom, ts, cap, bat in salles_data:

        s, _ = Salle.objects.update_or_create(
            nom=nom,
            defaults={
                "type_salle": ts,
                "capacite": cap,
                "batiment": bat,
            },
        )

        salles[nom] = s

    # =========================================================
    # CLASSES
    # =========================================================

    print("\n--- CLASSES ---")

    classes_data = [
        ("GL-L3-A", "GL L3 A", filieres["LF-GL"], "L3"),
        ("SE-L3-A", "SE L3 A", filieres["LF-SE"], "L3"),
        ("MI-L3-A", "MI L3 A", filieres["LF-MI"], "L3"),
        ("MINFO-A", "Master Info A", filieres["M-INFO"], "M2"),
    ]

    classes = {}

    for code, nom, filiere, niveau in classes_data:

        c, _ = Classe.objects.update_or_create(
            code=code,
            defaults={
                "nom": nom,
                "filiere": filiere,
                "niveau": niveau,
                "annee_universitaire": ANNEE,
                "capacite": 40,
            },
        )

        classes[code] = c

    # =========================================================
    # ENSEIGNANTS
    # =========================================================

    print("\n--- ENSEIGNANTS ---")

    enseignants_data = [
        (
            "PROF-INFO-01",
            "Mohamed",
            "Ben Ali",
            di,
            "maitre_conf",
            "Bases de Données",
        ),
        (
            "PROF-INFO-02",
            "Ahmed",
            "Gharbi",
            di,
            "assistant",
            "Réseaux",
        ),
        (
            "PROF-MATH-01",
            "Sonia",
            "Mbarek",
            dm,
            "professeur",
            "Mathématiques",
        ),
        (
            "PROF-CHIM-01",
            "Leila",
            "Zouari",
            dc,
            "maitre_assistant",
            "Chimie",
        ),
    ]

    enseignants = {}

    for mat, prenom, nom, dept, grade, spec in enseignants_data:

        e, _ = Enseignant.objects.update_or_create(
            matricule=mat,
            defaults={
                "prenom": prenom,
                "nom": nom,
                "departement": dept,
                "grade": grade,
                "specialite": spec,
                "email": f"{mat.lower()}@fsb.tn",
                "actif": True,
            },
        )

        enseignants[mat] = e

    # =========================================================
    # ETUDIANTS
    # =========================================================

    print("\n--- ETUDIANTS ---")

    etudiants_data = [
        ("20241001", "Fatma", "Trabelsi", filieres["LF-GL"]),
        ("20241002", "Ali", "Hamdi", filieres["LF-GL"]),
        ("20241003", "Rim", "Bouaziz", filieres["LF-GL"]),
        ("20241004", "Omar", "Sfar", filieres["LF-SE"]),
        ("20241005", "Hana", "Masmoudi", filieres["LF-SE"]),
        ("20241006", "Mariem", "Saidi", filieres["LF-MI"]),
        ("20241007", "Khaled", "Ayari", filieres["M-INFO"]),
        ("20241008", "Youssef", "Jaziri", filieres["LF-GL"]),
        ("20241009", "Amira", "Ben Salem", filieres["LF-GL"]),
        ("20241010", "Nour", "Khalfallah", filieres["LF-SE"]),
        ("20241011", "Skander", "Mnif", filieres["LF-SE"]),
        ("20241012", "Ala", "Brahmi", filieres["LF-MI"]),
        ("20241013", "Sarra", "Gharbi", filieres["M-INFO"]),
        ("20241014", "Ahmed", "Dridi", filieres["M-INFO"]),
    ]

    etudiants = {}

    for num, prenom, nom, filiere in etudiants_data:

        e, _ = Etudiant.objects.update_or_create(
            numero_etudiant=num,
            defaults={
                "prenom": prenom,
                "nom": nom,
                "filiere": filiere,
                "annee_inscription": 2024,
                "email": f"{num}@fsb.tn",
                "statut": "inscrit",
            },
        )

        etudiants[num] = e

    # =========================================================
    # MATIERES
    # =========================================================

    print("\n--- MATIERES ---")

    matieres_data = [
        ("INFO101", "Programmation Python", filieres["LF-GL"], 1, 3),
        ("INFO102", "Bases de Données", filieres["LF-GL"], 2, 3),
        ("INFO201", "Réseaux", filieres["LF-SE"], 1, 3),
        ("MATH101", "Analyse", filieres["LF-MI"], 1, 2),
        ("IA101", "Intelligence Artificielle", filieres["M-INFO"], 1, 3),
    ]

    matieres = {}

    for code, nom, filiere, sem, coeff in matieres_data:

        m, _ = Matiere.objects.update_or_create(
            code=code,
            defaults={
                "nom": nom,
                "filiere": filiere,
                "semestre": sem,
                "coefficient": coeff,
                "credits": 3,
                "heures_cours": 20,
                "heures_td": 10,
                "heures_tp": 10,
            },
        )

        matieres[code] = m

    # =========================================================
    # EMPLOI DU TEMPS
    # =========================================================

    print("\n--- EMPLOI DU TEMPS ---")

    edt_data = [
        (
            classes["GL-L3-A"],
            matieres["INFO101"],
            enseignants["PROF-INFO-01"],
            salles["Amphi A"],
            "lundi",
            time(8, 0),
            time(10, 0),
            "cours",
            1,
        ),
        (
            classes["GL-L3-A"],
            matieres["INFO102"],
            enseignants["PROF-INFO-02"],
            salles["Salle TP Info"],
            "mercredi",
            time(10, 0),
            time(12, 0),
            "tp",
            2,
        ),
        (
            classes["MI-L3-A"],
            matieres["MATH101"],
            enseignants["PROF-MATH-01"],
            salles["Salle 101"],
            "mardi",
            time(8, 0),
            time(10, 0),
            "cours",
            1,
        ),
    ]

    seances = []

    for (
        classe,
        matiere,
        enseignant,
        salle,
        jour,
        h_debut,
        h_fin,
        type_seance,
        sem,
    ) in edt_data:

        edt, _ = EmploiDuTemps.objects.update_or_create(
            classe=classe,
            matiere=matiere,
            jour=JOURS[jour],
            heure_debut=h_debut,
            defaults={
                "enseignant": enseignant,
                "salle": salle,
                "heure_fin": h_fin,
                "type_seance": type_seance,
                "annee_universitaire": ANNEE,
                "semestre": sem,
            },
        )

        seances.append(edt)

    # =========================================================
    # NOTES
    # =========================================================

    print("\n--- NOTES ---")

    notes_data = [
        ("20241001", "INFO101", 14, 15, 1),
        ("20241002", "INFO101", 8, 7, 1),
        ("20241003", "INFO101", 17, 18, 1),
        ("20241004", "INFO201", 13, 14, 1),
        ("20241006", "MATH101", 15, 16, 1),
        ("20241007", "IA101", 18, 17, 1),
        ("20241008", "INFO101", 5, 6, 1),
        ("20241009", "INFO101", 12, 11, 1),
        ("20241010", "INFO201", 9, 8, 1),
        ("20241011", "INFO201", 16, 15, 1),
        ("20241012", "MATH101", 18, 17, 1),
        ("20241013", "IA101", 19, 18, 1),
        ("20241014", "IA101", 7, 6, 1),
    ]

    for num, code, ds, exam, sem in notes_data:

        et = etudiants[num]
        mat = matieres[code]

        Note.objects.update_or_create(
            etudiant=et,
            matiere=mat,
            type_note="ds",
            annee_universitaire=ANNEE,
            semestre=sem,
            defaults={
                "note": ds,
            },
        )

        Note.objects.update_or_create(
            etudiant=et,
            matiere=mat,
            type_note="exam",
            annee_universitaire=ANNEE,
            semestre=sem,
            defaults={
                "note": exam,
            },
        )

    # =========================================================
    # MOYENNES
    # =========================================================

    print("\n--- MOYENNES ---")

    def calcul_mention(m):

        if m >= 18:
            return "excellent"

        if m >= 16:
            return "tres_bien"

        if m >= 14:
            return "bien"

        if m >= 12:
            return "assez_bien"

        if m >= 10:
            return "passable"

        return ""

    moyennes_data = [
        ("20241001", 14.5, 1),
        ("20241002", 7.5, 1),
        ("20241003", 17.5, 1),
        ("20241004", 13.5, 1),
        ("20241006", 15.5, 1),
        ("20241007", 18.0, 1),
        ("20241008", 5.5, 1),
        ("20241009", 11.5, 1),
        ("20241010", 8.5, 1),
        ("20241011", 15.5, 1),
        ("20241012", 17.5, 1),
        ("20241013", 18.5, 1),
        ("20241014", 6.0, 1),
    ]

    for num, moyenne, sem in moyennes_data:

        et = etudiants[num]

        classe = Classe.objects.filter(
            filiere=et.filiere
        ).first()

        if not classe:
            continue

        MoyenneEtudiant.objects.update_or_create(
            etudiant=et,
            classe=classe,
            annee_universitaire=ANNEE,
            semestre=sem,
            defaults={
                "moyenne": moyenne,
                "mention": calcul_mention(moyenne),
                "admis": moyenne >= 10,
            },
        )

    # =========================================================
    # ABSENCES
    # =========================================================

    print("\n--- ABSENCES ---")

    today = date.today()

    absences_data = [
        ("20241002", 0, -5, False, ""),
        ("20241002", 0, -10, False, ""),
        ("20241002", 0, -15, False, ""),
        ("20241001", 0, -3, True, "Maladie"),
        ("20241004", 0, -4, False, ""),
        ("20241008", 0, -2, False, ""),
        ("20241008", 0, -4, False, ""),
        ("20241008", 0, -6, False, ""),
        ("20241008", 0, -8, False, ""),
        ("20241010", 0, -3, False, ""),
        ("20241010", 0, -5, False, ""),
        ("20241014", 0, -1, False, ""),
        ("20241014", 0, -2, False, ""),
        ("20241014", 0, -3, False, ""),
        ("20241014", 0, -4, False, ""),
        ("20241014", 0, -5, False, ""),
    ]

    for num, seance_index, offset, justifiee, motif in absences_data:

        et = etudiants[num]

        if not seances:
            continue

        seance = seances[seance_index]

        Absence.objects.update_or_create(
            etudiant=et,
            seance=seance,
            date=today + timedelta(days=offset),
            defaults={
                "justifiee": justifiee,
                "motif": motif,
            },
        )

    # =========================================================
    # STAGES
    # =========================================================

    print("\n--- STAGES ---")

    stages_data = [
        (
            "20241007",
            "pfe",
            "Vermeg",
            "Plateforme IA pour analyse pédagogique",
            "Développement d’un système intelligent multi-agent.",
            date(2025, 2, 1),
            date(2025, 6, 1),
            "PROF-INFO-01",
            "Sami Khelifi",
            "en_cours",
            17.5,
        ),

        (
            "20241013",
            "pfe",
            "Sopra HR",
            "Application RH intelligente",
            "Développement Full Stack Django + React.",
            date(2025, 2, 15),
            date(2025, 6, 15),
            "PROF-INFO-02",
            "Nadia Ben Amor",
            "valide",
            18.0,
        ),

        (
            "20241001",
            "initiation",
            "Telnet",
            "Application web de gestion universitaire",
            "Mini ERP universitaire.",
            date(2025, 7, 1),
            date(2025, 8, 1),
            "PROF-INFO-01",
            "Mohamed Ayadi",
            "en_attente",
            None,
        ),

        (
            "20241004",
            "observation",
            "Tunisie Telecom",
            "Découverte infrastructure réseau",
            "Observation du fonctionnement réseau.",
            date(2025, 6, 15),
            date(2025, 7, 15),
            "PROF-INFO-02",
            "Hichem Triki",
            "refuse",
            None,
        ),

        (
            "20241011",
            "initiation",
            "Cynoia",
            "Application collaborative",
            "Développement backend API.",
            date(2025, 7, 1),
            date(2025, 8, 15),
            "PROF-INFO-01",
            "Walid Ben Salah",
            "termine",
            14.5,
        ),
    ]

    for (
        num,
        type_stage,
        entreprise,
        sujet,
        description,
        debut,
        fin,
        encadrant,
        enc_entreprise,
        statut,
        note_stage,
    ) in stages_data:

        DemandeStage.objects.update_or_create(
            etudiant=etudiants[num],
            sujet=sujet,
            defaults={
                "type_stage": type_stage,
                "entreprise": entreprise,
                "description": description,
                "date_debut": debut,
                "date_fin": fin,
                "encadrant_fsb": enseignants[encadrant],
                "encadrant_entreprise": enc_entreprise,
                "statut": statut,
                "note_stage": note_stage,
                "commentaire_admin": (
                    "Très bon dossier."
                    if statut in ["valide", "termine"]
                    else ""
                ),
            },
        )

    # =========================================================
    # DIPLOMES
    # =========================================================

    print("\n--- DIPLOMES ---")

    diplomes_data = [
        (
            "20241007",
            "Master Recherche",
            "Master Informatique",
            2025,
            "tres_bien",
            17.8,
            "MINFO-2025-001",
            date(2025, 7, 10),
        ),

        (
            "20241013",
            "Master Professionnel",
            "Intelligence Artificielle",
            2025,
            "tres_bien",
            18.4,
            "MINFO-2025-002",
            date(2025, 7, 10),
        ),

        (
            "20241003",
            "Licence",
            "Génie Logiciel",
            2025,
            "bien",
            15.2,
            "LICGL-2025-001",
            date(2025, 7, 5),
        ),

        (
            "20241006",
            "Licence",
            "Mathématiques Informatique",
            2025,
            "assez_bien",
            13.7,
            "LICMI-2025-001",
            date(2025, 7, 5),
        ),
    ]

    for (
        num,
        type_diplome,
        specialite,
        annee,
        mention,
        moyenne,
        numero,
        date_delivrance,
    ) in diplomes_data:

        Diplome.objects.update_or_create(
            numero_diplome=numero,
            defaults={
                "etudiant": etudiants[num],
                "type_diplome": type_diplome,
                "specialite": specialite,
                "annee_obtention": annee,
                "mention": mention,
                "moyenne_generale": moyenne,
                "date_delivrance": date_delivrance,
            },
        )

        etudiants[num].statut = "diplome"
        etudiants[num].save()

    # =========================================================
    # SESSIONS EXAMENS
    # =========================================================

    print("\n--- SESSIONS EXAMENS ---")

    sessions_data = [
        (
            "Session Principale S1",
            "principale",
            1,
            date(2025, 1, 10),
            date(2025, 1, 20),
        ),
        (
            "Session Rattrapage S1",
            "rattrapage",
            1,
            date(2025, 2, 1),
            date(2025, 2, 10),
        ),
    ]

    for nom, ts, sem, debut, fin in sessions_data:

        SessionExamen.objects.update_or_create(
            nom=nom,
            annee_universitaire=ANNEE,
            defaults={
                "type_session": ts,
                "semestre": sem,
                "date_debut": debut,
                "date_fin": fin,
            },
        )

    # =========================================================
    # ADMIN USER
    # =========================================================

    print("\n--- ADMIN ---")

    if not CustomUser.objects.filter(username="admin").exists():

        CustomUser.objects.create_superuser(
            username="admin",
            password="admin",
            role="super_admin",
        )

    # =========================================================
    # RESUME
    # =========================================================

    print("\n" + "=" * 60)
    print("SEED TERMINÉ")
    print("=" * 60)

    print("Départements :", Departement.objects.count())
    print("Filières     :", Filiere.objects.count())
    print("Classes      :", Classe.objects.count())
    print("Enseignants  :", Enseignant.objects.count())
    print("Étudiants    :", Etudiant.objects.count())
    print("Matières     :", Matiere.objects.count())
    print("EDT          :", EmploiDuTemps.objects.count())
    print("Notes        :", Note.objects.count())
    print("Moyennes     :", MoyenneEtudiant.objects.count())
    print("Absences     :", Absence.objects.count())
    print("Stages       :", DemandeStage.objects.count())
    print("Diplômes     :", Diplome.objects.count())
    print("Sessions     :", SessionExamen.objects.count())

    print("\nÉtudiants à risque :")

    risque = (
        Etudiant.objects.annotate(
            nb_nj=Count(
                "absences",
                filter=Q(absences__justifiee=False),
            )
        )
        .filter(nb_nj__gte=3)
    )

    for e in risque:

        print(
            f"⛔ {e.prenom} {e.nom} -> {e.nb_nj} absences NJ"
        )

    print("=" * 60)


if __name__ == "__main__":
    run()