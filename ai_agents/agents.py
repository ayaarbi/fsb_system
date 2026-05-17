# -*- coding: utf-8 -*-
"""
FSB Multi-Agent System - CORRIGÉ
"""

import json
import re
from uuid import uuid4
from groq import Groq
from django.conf import settings
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# HELPERS GROQ
# ──────────────────────────────────────────────

def _groq(messages, system, temperature=0.1, max_tokens=700):
    client = Groq(api_key=settings.GROQ_API_KEY)
    messages = messages[-5:]
    full = [{"role": "system", "content": system}] + messages
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=full,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def _groq_json(messages, system):
    text = _groq(
        messages,
        system + "\n\nRéponds UNIQUEMENT avec du JSON valide, sans texte avant ou après.",
        max_tokens=400,
    )
    text = re.sub(r"```json|```", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        return {}


# ──────────────────────────────────────────────
# PARSER AMÉLIORÉ
# ──────────────────────────────────────────────

def extraire_champ(cles, msg, param_val=""):
    """Extrait un champ du message avec plusieurs formats possibles"""
    if param_val and str(param_val).strip():
        return str(param_val).strip()
   
    if not msg:
        return ""
   
    for cle in cles:
        # Format: "clé: valeur" ou "clé = valeur"
        pattern = rf"{cle}\s*[:=]\s*([^\s,;/\n]+(?:\s+[^\s,;/\n=:]+)*)"
        m = re.search(pattern, msg, re.IGNORECASE)
        if m:
            return m.group(1).strip()
       
        # Format: "clé valeur" (sans séparateur explicite)
        pattern2 = rf"{cle}\s+([^\s,;/\n]+(?:\s+[^\s,;/\n]+){{0,2}})"
        m2 = re.search(pattern2, msg, re.IGNORECASE)
        if m2:
            return m2.group(1).strip()
   
    return ""


def extraire_tous_champs(msg):
    """Extrait tous les champs d'un message de création d'étudiant"""
    champs = {
        'nom': '',
        'prenom': '',
        'email': '',
        'filiere': '',
        'numero': ''
    }
   
    # Patterns pour chaque champ
    patterns = {
        'nom': r"(?:nom|name)\s*[:=]\s*([^\s,;]+(?:\s+[^\s,;]+){0,2})",
        'prenom': r"(?:prenom|prénom|firstname)\s*[:=]\s*([^\s,;]+(?:\s+[^\s,;]+){0,2})",
        'email': r"(?:email|mail)\s*[:=]\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        'filiere': r"(?:filiere|filière|classe)\s*[:=]\s*([^\s,;]+(?:\s+[^\s,;]+){0,3})",
        'numero': r"(?:numero|numéro|id)\s*[:=]\s*([^\s,;]+)"
    }
   
    for champ, pattern in patterns.items():
        match = re.search(pattern, msg, re.IGNORECASE)
        if match:
            champs[champ] = match.group(1).strip()
   
    # Si aucun champ trouvé avec les patterns explicites, essayer l'ordre naturel
    if not champs['nom'] and not champs['prenom']:
        # Format: "ajouter l'étudiant Prénom Nom"
        match_nom_complet = re.search(r"ajouter\s+l['']?étudiant\s+(\w+)\s+(\w+)", msg, re.IGNORECASE)
        if match_nom_complet:
            champs['prenom'] = match_nom_complet.group(1)
            champs['nom'] = match_nom_complet.group(2)
   
    return champs


# ──────────────────────────────────────────────
# CONTEXT BUILDER (inchangé)
# ──────────────────────────────────────────────

def build_full_context(user=None):
    from administration.models import Etudiant, Enseignant, Departement, Filiere, Salle
    from pedagogie.models import Absence, Note, MoyenneEtudiant, Matiere, EmploiDuTemps
    from stages.models import DemandeStage, Diplome
    from examens.models import PlanningExamen

    ctx = {}

    ctx["departements"] = [
        {
            "id": d.pk,
            "nom": d.nom,
            "nb_etudiants": Etudiant.objects.filter(
                filiere__departement=d, statut="inscrit"
            ).count(),
        }
        for d in Departement.objects.all()
    ]

    ctx["filieres"] = [
        {"id": f.pk, "nom": f.nom, "code": f.code, "niveau": f.niveau}
        for f in Filiere.objects.all()
    ]

    ctx["etudiants"] = [
        {
            "id": e.pk,
            "nom": e.nom,
            "prenom": e.prenom,
            "numero": e.numero_etudiant,
            "filiere": e.filiere.nom if e.filiere else None,
            "filiere_id": e.filiere.pk if e.filiere else None,
            "statut": e.statut,
        }
        for e in Etudiant.objects.select_related("filiere").all()[:100]
    ]

    ctx["enseignants"] = [
        {
            "id": e.pk,
            "nom": e.nom,
            "prenom": e.prenom,
            "grade": e.grade,
            "specialite": e.specialite,
        }
        for e in Enseignant.objects.filter(actif=True)[:50]
    ]

    ctx["notes"] = [
        {
            "etudiant": f"{n.etudiant.prenom} {n.etudiant.nom}",
            "matiere": n.matiere.nom if n.matiere else "",
            "note": float(n.note),
            "type": n.type_note,
            "semestre": n.semestre,
        }
        for n in Note.objects.select_related("etudiant", "matiere")[:50]
    ]

    ctx["moyennes"] = [
        {
            "etudiant": f"{m.etudiant.prenom} {m.etudiant.nom}",
            "moyenne": float(m.moyenne),
            "mention": m.mention,
            "admis": m.admis,
        }
        for m in MoyenneEtudiant.objects.select_related("etudiant")[:50]
    ]

    ctx["absences"] = [
        {
            "etudiant": f"{a.etudiant.prenom} {a.etudiant.nom}",
            "date": str(a.date),
            "justifiee": a.justifiee,
        }
        for a in Absence.objects.select_related("etudiant")[:50]
    ]

    ctx["stages"] = [
        {
            "id": s.pk,
            "etudiant": f"{s.etudiant.prenom} {s.etudiant.nom}",
            "entreprise": s.entreprise,
            "sujet": s.sujet,
            "statut": s.statut,
        }
        for s in DemandeStage.objects.select_related("etudiant")[:30]
    ]

    ctx["diplomes"] = [
        {
            "id": d.pk,
            "etudiant": f"{d.etudiant.prenom} {d.etudiant.nom}",
            "type": d.type_diplome,
            "specialite": d.specialite,
            "mention": d.mention,
        }
        for d in Diplome.objects.select_related("etudiant")[:30]
    ]

    try:
        ctx["salles"] = [
            {"id": s.pk, "nom": s.nom, "capacite": s.capacite, "type": s.type_salle}
            for s in Salle.objects.all()
        ]
    except Exception:
        ctx["salles"] = []

    try:
        ctx["matieres"] = [
            {
                "id": m.pk,
                "nom": m.nom,
                "code": m.code,
                "filiere": m.filiere.nom if hasattr(m, "filiere") and m.filiere else "",
            }
            for m in Matiere.objects.all()[:50]
        ]
    except Exception:
        ctx["matieres"] = []

    try:
        ctx["planning_examens"] = [
            {
                "date": str(p.date),
                "salle": p.salle.nom if p.salle else "",
                "matiere": p.matiere.nom if p.matiere else "",
            }
            for p in PlanningExamen.objects.select_related("salle", "matiere")[:50]
        ]
    except Exception:
        ctx["planning_examens"] = []

    try:
        ctx["emplois_du_temps"] = [
            {
                "jour": e.jour,
                "heure_debut": str(e.heure_debut),
                "heure_fin": str(e.heure_fin),
                "matiere": e.matiere.nom if e.matiere else "",
                "enseignant": (
                    f"{e.enseignant.prenom} {e.enseignant.nom}" if e.enseignant else ""
                ),
                "filiere": (
                    e.filiere.nom if hasattr(e, "filiere") and e.filiere else ""
                ),
            }
            for e in EmploiDuTemps.objects.select_related("matiere", "enseignant").all()[:50]
        ]
    except Exception:
        ctx["emplois_du_temps"] = []

    ctx["stats"] = {
        "total_etudiants": Etudiant.objects.count(),
        "total_enseignants": Enseignant.objects.count(),
        "total_notes": Note.objects.count(),
        "total_absences": Absence.objects.count(),
        "total_stages": DemandeStage.objects.count(),
        "stages_en_attente": DemandeStage.objects.filter(statut="en_attente").count(),
        "total_diplomes": Diplome.objects.count(),
    }

    if user:
        ctx["agent_connecte"] = {
            "nom": user.get_full_name(),
            "username": user.username,
        }

    return ctx


def compress_context(ctx):
    return {
        "stats": ctx.get("stats", {}),
        "filieres": ctx.get("filieres", []),
        "etudiants": ctx.get("etudiants", [])[:30],
        "enseignants": ctx.get("enseignants", [])[:20],
        "notes": ctx.get("notes", [])[:20],
        "absences": ctx.get("absences", [])[:20],
        "stages": ctx.get("stages", [])[:10],
        "diplomes": ctx.get("diplomes", [])[:10],
        "salles": ctx.get("salles", []),
        "matieres": ctx.get("matieres", [])[:30],
        "planning_examens": ctx.get("planning_examens", [])[:30],
        "emplois_du_temps": ctx.get("emplois_du_temps", [])[:30],
    }


# ──────────────────────────────────────────────
# ROUTER (inchangé)
# ──────────────────────────────────────────────

ROUTER_SYSTEM = """
Tu es le routeur du système FSB (université).
Analyse le dernier message utilisateur et retourne un JSON avec :

{
  "agent": "stat|pedago|stage|admin|action",
  "action": null ou "creer_etudiant|valider_diplome|suggerer_planning_examen|generer_emploi_du_temps",
  "params": {},
  "resume": "..."
}

Règles :
- CRÉER / AJOUTER / INSCRIRE un étudiant → agent="action", action="creer_etudiant"
  params: {"nom":"...", "prenom":"...", "email":"...", "filiere_nom":"...", "numero_etudiant":"..."}
  Extrais UNIQUEMENT les valeurs explicitement mentionnées dans le message. Ne pas inventer.

- PLANIFIER / PROGRAMMER un examen → agent="action", action="suggerer_planning_examen"
  params: {"filiere_nom":"...", "matiere_nom":"...", "date_debut":"YYYY-MM-DD", "date_fin":"YYYY-MM-DD"}

- GÉNÉRER un emploi du temps → agent="action", action="generer_emploi_du_temps"
  params: {"filiere_nom":"...", "matieres":["mat1","mat2"], "enseignants":["ens1","ens2"]}

- VALIDER un diplôme → agent="action", action="valider_diplome"
  params: {"etudiant_nom":"..."}

- Sinon → agent="stat"|"pedago"|"stage"|"admin", action=null

Retourne UNIQUEMENT du JSON valide.
"""


def router_agent(messages, ctx_json):
    system = (
        ROUTER_SYSTEM
        + f"\n\nFILIERES DISPONIBLES: {json.dumps(ctx_json.get('filieres', []), ensure_ascii=False)}"
        + f"\n\nSTATS: {json.dumps(ctx_json.get('stats', {}), ensure_ascii=False)}"
    )
    return _groq_json(messages[-2:], system)


# ──────────────────────────────────────────────
# AGENTS INFORMATIFS (inchangés)
# ──────────────────────────────────────────────

def stat_agent(messages, ctx):
    small_ctx = compress_context(ctx)
    system = "Tu es l'agent statistiques de la FSB. Tu réponds en français. Tu analyses les chiffres et tendances."
    return _groq(messages, system + f"\n\nDONNÉES:\n{json.dumps(small_ctx, ensure_ascii=False)}")


def pedago_agent(messages, ctx):
    small_ctx = compress_context(ctx)
    system = "Tu es l'agent pédagogique de la FSB. Tu réponds en français. Tu aides pour notes, absences, moyennes."
    return _groq(messages, system + f"\n\nDONNÉES:\n{json.dumps(small_ctx, ensure_ascii=False)}")


def stage_agent(messages, ctx):
    small_ctx = compress_context(ctx)
    system = "Tu es l'agent stages de la FSB. Tu réponds en français. Tu aides pour les demandes de stage."
    return _groq(messages, system + f"\n\nDONNÉES:\n{json.dumps(small_ctx, ensure_ascii=False)}")


def admin_agent(messages, ctx):
    small_ctx = compress_context(ctx)
    system = "Tu es l'agent administratif de la FSB. Tu réponds en français. Tu aides pour étudiants, filières, diplômes."
    return _groq(messages, system + f"\n\nDONNÉES:\n{json.dumps(small_ctx, ensure_ascii=False)}")


# ──────────────────────────────────────────────
# ACTION AGENT AMÉLIORÉ
# ──────────────────────────────────────────────

def action_agent(action, params, ctx, dernier_msg=""):
    from administration.models import Etudiant, Filiere
    from pedagogie.models import MoyenneEtudiant
    from stages.models import Diplome
    from django.db import transaction

    try:
        # ─────────────────────────────────────────
        # CRÉER ÉTUDIANT - Version améliorée
        # ─────────────────────────────────────────
        if action == "creer_etudiant":
            logger.info(f"Création d'étudiant - Message: {dernier_msg}")
            logger.info(f"Params reçus: {params}")
           
            # Extraire TOUS les champs du message
            champs = extraire_tous_champs(dernier_msg)
           
            # Utiliser les paramètres du router ou l'extraction directe
            nom = params.get("nom", "") or champs['nom']
            prenom = params.get("prenom", "") or champs['prenom']
            email = params.get("email", "") or champs['email']
            filiere_nom = params.get("filiere_nom", "") or champs['filiere']
            numero = params.get("numero_etudiant", "") or champs['numero']
           
            logger.info(f"Données extraites - Nom: {nom}, Prénom: {prenom}, Email: {email}, Filière: {filiere_nom}")
           
            # Si toujours pas de nom/prénom, demander
            if not nom or not prenom:
                filieres_dispo = ", ".join([f["nom"] for f in ctx.get("filieres", [])])
                return (
                    f"📝 Pour créer un étudiant, veuillez me fournir :\n\n"
                    f"• **Nom** : \n"
                    f"• **Prénom** : \n"
                    f"• **Filière** (disponibles : {filieres_dispo}) : \n"
                    f"• **Email** (optionnel) : \n\n"
                    f"💡 Exemple : *Ajouter l'étudiant: nom=Dupont, prénom=Jean, filière=Informatique*"
                )
           
            # Trouver la filière
            filiere = None
            if filiere_nom:
                filiere = (
                    Filiere.objects.filter(nom__icontains=filiere_nom).first()
                    or Filiere.objects.filter(code__icontains=filiere_nom).first()
                )
                if not filiere:
                    filieres_liste = ", ".join([f["nom"] for f in ctx.get("filieres", [])])
                    return f"❌ Filière '{filiere_nom}' introuvable. Filières disponibles : {filieres_liste}"
           
            # Générer numéro étudiant si absent
            if not numero:
                annee = date.today().year
                dernier_etudiant = Etudiant.objects.order_by('-id').first()
                if dernier_etudiant and dernier_etudiant.numero_etudiant:
                    try:
                        dernier_num = int(dernier_etudiant.numero_etudiant[-4:])
                        count = dernier_num + 1
                    except:
                        count = Etudiant.objects.count() + 1
                else:
                    count = Etudiant.objects.count() + 1
                numero = f"{annee}{count:04d}"
           
            # Éviter les doublons de numéro
            original_numero = numero
            counter = 1
            while Etudiant.objects.filter(numero_etudiant=numero).exists():
                numero = f"{original_numero[:-4]}{counter:04d}"
                counter += 1
           
            # Créer l'étudiant dans une transaction
            with transaction.atomic():
                email_final = email if email else f"{prenom.lower()}.{nom.lower()}@fsb.tn"
               
                etudiant = Etudiant.objects.create(
                    nom=nom.title(),
                    prenom=prenom.title(),
                    email=email_final,
                    filiere=filiere,
                    numero_etudiant=numero,
                    statut="inscrit",
                    annee_inscription=date.today().year,
                    date_naissance=None,
                )
               
                logger.info(f"Étudiant créé avec succès - ID: {etudiant.id}, Numéro: {etudiant.numero_etudiant}")
               
                return (
                    f"✅ **Étudiant créé avec succès !**\n\n"
                    f"👤 **Nom complet** : {etudiant.prenom} {etudiant.nom}\n"
                    f"🔢 **Numéro étudiant** : {etudiant.numero_etudiant}\n"
                    f"📚 **Filière** : {filiere.nom if filiere else 'Non assignée'}\n"
                    f"📧 **Email** : {etudiant.email}\n"
                    f"📅 **Date d'inscription** : {etudiant.annee_inscription}\n\n"
                    f"✨ L'étudiant a été ajouté à la base de données."
                )
       
        # ─────────────────────────────────────────
        # SUGGÉRER PLANNING EXAMEN (inchangé)
        # ─────────────────────────────────────────
        elif action == "suggerer_planning_examen":
            filiere_nom = params.get("filiere_nom", "") or extraire_champ(["filiere", "filière"], dernier_msg)
            matiere_nom = params.get("matiere_nom", "") or extraire_champ(["matiere", "matière"], dernier_msg)
            date_debut_str = params.get("date_debut", str(date.today()))
            date_fin_str = params.get("date_fin", "")

            dates_occupees = set(p["date"] for p in ctx.get("planning_examens", []))
            salles = ctx.get("salles", [])

            try:
                d_debut = date.fromisoformat(date_debut_str)
            except Exception:
                d_debut = date.today()

            try:
                d_fin = date.fromisoformat(date_fin_str) if date_fin_str else d_debut + timedelta(days=14)
            except Exception:
                d_fin = d_debut + timedelta(days=14)

            dates_libres = []
            current = d_debut
            while current <= d_fin and len(dates_libres) < 5:
                if current.weekday() < 5 and str(current) not in dates_occupees:
                    dates_libres.append(str(current))
                current += timedelta(days=1)

            if not dates_libres:
                return "❌ Aucune date libre trouvée dans la période demandée."

            salles_info = "\n".join(
                [f"  🏛️ {s['nom']} (capacité: {s.get('capacite', '?')})" for s in salles[:5]]
            ) if salles else "  ⚠️ Aucune salle enregistrée dans le système."

            dates_info = "\n".join([f"  📅 {d}" for d in dates_libres])

            return (
                f"📋 **Planning suggéré pour l'examen**"
                f"{' de ' + matiere_nom if matiere_nom else ''}"
                f"{' — Filière ' + filiere_nom if filiere_nom else ''}\n\n"
                f"📅 **Dates disponibles :**\n{dates_info}\n\n"
                f"🏛️ **Salles disponibles :**\n{salles_info}\n\n"
                f"💡 **Recommandation** : Le {dates_libres[0]}"
                f"{' en salle ' + salles[0]['nom'] if salles else ''}\n"
                f"Souhaitez-vous que je confirme cette planification ?"
            )

        # ─────────────────────────────────────────
        # GÉNÉRER EMPLOI DU TEMPS (inchangé)
        # ─────────────────────────────────────────
        elif action == "generer_emploi_du_temps":
            filiere_nom = params.get("filiere_nom", "") or extraire_champ(["filiere", "filière"], dernier_msg)
            matieres_demandees = params.get("matieres", [])
            enseignants_demandes = params.get("enseignants", [])

            jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
            creneaux = [
                ("08:00", "10:00"),
                ("10:00", "12:00"),
                ("13:00", "15:00"),
                ("15:00", "17:00"),
            ]

            emplois_existants = ctx.get("emplois_du_temps", [])
            occupes = set(
                (e["jour"], e["heure_debut"], e.get("enseignant", ""))
                for e in emplois_existants
            )

            planning = []
            mat_idx = 0
            total_matieres = len(matieres_demandees) if matieres_demandees else 4

            for jour in jours:
                for debut, fin in creneaux:
                    if mat_idx >= total_matieres:
                        break
                    matiere = matieres_demandees[mat_idx] if matieres_demandees else f"Matière {mat_idx + 1}"
                    enseignant = (
                        enseignants_demandes[mat_idx]
                        if mat_idx < len(enseignants_demandes)
                        else "À assigner"
                    )
                    cle = (jour, debut + ":00", enseignant)
                    if cle not in occupes:
                        planning.append({
                            "jour": jour, "debut": debut, "fin": fin,
                            "matiere": matiere, "enseignant": enseignant,
                        })
                        occupes.add(cle)
                        mat_idx += 1
                if mat_idx >= total_matieres:
                    break

            if not planning:
                return "❌ Impossible de générer l'emploi du temps, conflits détectés sur tous les créneaux."

            lignes = [f"📅 **Emploi du temps — {filiere_nom or 'Classe'}**\n"]
            jour_courant = ""
            for p in planning:
                if p["jour"] != jour_courant:
                    jour_courant = p["jour"]
                    lignes.append(f"\n📌 **{jour_courant}**")
                lignes.append(f"  {p['debut']}–{p['fin']} | {p['matiere']} | 👨‍🏫 {p['enseignant']}")

            lignes.append("\n\n✅ Planning généré sans conflits. Souhaitez-vous que je l'enregistre ?")
            return "\n".join(lignes)

        # ─────────────────────────────────────────
        # VALIDER DIPLÔME (inchangé)
        # ─────────────────────────────────────────
        elif action == "valider_diplome":
            etudiant_nom = params.get("etudiant_nom", "") or extraire_champ(["etudiant", "nom"], dernier_msg)
            from administration.models import Etudiant as Etud
            etudiant = Etud.objects.filter(nom__icontains=etudiant_nom).first()
            if not etudiant:
                return "❌ Étudiant introuvable."

            moy = MoyenneEtudiant.objects.filter(etudiant=etudiant).first()
            moyenne = float(moy.moyenne) if moy else 10.0

            with transaction.atomic():
                Diplome.objects.create(
                    etudiant=etudiant,
                    type_diplome="Licence",
                    specialite=etudiant.filiere.nom if etudiant.filiere else "",
                    annee_obtention=date.today().year,
                    mention="bien",
                    moyenne_generale=moyenne,
                    numero_diplome=f"DIP-{uuid4().hex[:8].upper()}",
                    date_delivrance=date.today(),
                )
                etudiant.statut = "diplome"
                etudiant.save()
           
            return f"🎓 **Diplôme validé** pour {etudiant.prenom} {etudiant.nom} (moyenne: {moyenne}/20)"

        return "❌ Action inconnue."

    except Exception as e:
        logger.error(f"Erreur dans action_agent: {str(e)}", exc_info=True)
        return f"❌ Erreur lors de l'action '{action}': {str(e)}"


# ──────────────────────────────────────────────
# ORCHESTRATEUR AMÉLIORÉ
# ──────────────────────────────────────────────

def orchestrate(messages, user=None):
    ctx = build_full_context(user)
   
    dernier_msg = messages[-1]["content"] if messages else ""
   
    try:
        plan = router_agent(messages, ctx)
        agent = plan.get("agent", "admin")
        action = plan.get("action")
        params = plan.get("params", {}) or {}
       
        logger.info(f"Router décision - Agent: {agent}, Action: {action}, Params: {params}")
       
    except Exception as e:
        logger.error(f"Erreur router: {e}")
        agent = "admin"
        action = None
        params = {}

    # ── Action réelle sur la BD ──
    if agent == "action" and action:
        # Pour la création d'étudiant, on passe directement à l'action
        reply = action_agent(action, params, ctx, dernier_msg=dernier_msg)
        return reply, "action", action

    # ── Agents informatifs ──
    if agent == "stat":
        reply = stat_agent(messages, ctx)
    elif agent == "pedago":
        reply = pedago_agent(messages, ctx)
    elif agent == "stage":
        reply = stage_agent(messages, ctx)
    else:
        reply = admin_agent(messages, ctx)

    return reply, agent, None
