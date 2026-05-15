# -*- coding: utf-8 -*-
"""
FSB Multi-Agent System
Agents disponibles :
  - RouterAgent      : analyse l'intention et dispatche
  - AdminAgent       : inscriptions, documents, scolarité
  - PedagoAgent      : notes, absences, moyennes, emplois du temps
  - StageAgent       : demandes de stage, validation, conventions
  - StatAgent        : statistiques, rapports, tableaux de bord
  - ActionAgent      : exécute les actions réelles sur la BD
"""
# -*- coding: utf-8 -*-
"""
FSB Multi-Agent System (OPTIMISÉ & STABLE)
Version optimisée anti-rate-limit Groq
"""

import json
import re
from uuid import uuid4
from groq import Groq
from django.conf import settings
from datetime import date


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def _groq(messages, system, temperature=0.1, max_tokens=700):
    """
    Appel Groq optimisé.
    """

    client = Groq(api_key=settings.GROQ_API_KEY)

    # garder seulement les derniers messages
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
    """
    Appel Groq JSON optimisé.
    """

    text = _groq(
        messages,
        system + "\n\nRéponds UNIQUEMENT avec du JSON valide.",
        max_tokens=300,
    )

    text = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(text)
    except Exception:
        return {}


# ──────────────────────────────────────────────
# CONTEXT BUILDER
# ──────────────────────────────────────────────

def build_full_context(user=None):

    from administration.models import (
        Etudiant,
        Enseignant,
        Departement,
        Filiere,
    )

    from pedagogie.models import (
        Absence,
        Note,
        MoyenneEtudiant,
    )

    from stages.models import (
        DemandeStage,
        Diplome,
    )

    ctx = {}

    # ─────────────────────────
    # Départements
    # ─────────────────────────

    ctx["departements"] = [
        {
            "id": d.pk,
            "nom": d.nom,
            "nb_etudiants": Etudiant.objects.filter(
                filiere__departement=d,
                statut="inscrit"
            ).count()
        }
        for d in Departement.objects.all()
    ]

    # ─────────────────────────
    # Filières
    # ─────────────────────────

    ctx["filieres"] = [
        {
            "id": f.pk,
            "nom": f.nom,
            "code": f.code,
            "niveau": f.niveau,
        }
        for f in Filiere.objects.all()
    ]

    # ─────────────────────────
    # Étudiants
    # ─────────────────────────

    ctx["etudiants"] = [
        {
            "id": e.pk,
            "nom": e.nom,
            "prenom": e.prenom,
            "numero": e.numero_etudiant,
            "filiere": e.filiere.nom if e.filiere else None,
            "statut": e.statut,
        }
        for e in Etudiant.objects.select_related("filiere").all()[:100]
    ]

    # ─────────────────────────
    # Enseignants
    # ─────────────────────────

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

    # ─────────────────────────
    # Notes
    # ─────────────────────────

    ctx["notes"] = [
        {
            "etudiant": f"{n.etudiant.prenom} {n.etudiant.nom}",
            "matiere": n.matiere.nom if n.matiere else "",
            "note": float(n.note),
            "type": n.type_note,
            "semestre": n.semestre,
        }
        for n in Note.objects.select_related(
            "etudiant",
            "matiere"
        )[:50]
    ]

    # ─────────────────────────
    # Moyennes
    # ─────────────────────────

    ctx["moyennes"] = [
        {
            "etudiant": f"{m.etudiant.prenom} {m.etudiant.nom}",
            "moyenne": float(m.moyenne),
            "mention": m.mention,
            "admis": m.admis,
        }
        for m in MoyenneEtudiant.objects.select_related(
            "etudiant"
        )[:50]
    ]

    # ─────────────────────────
    # Absences
    # ─────────────────────────

    ctx["absences"] = [
        {
            "etudiant": f"{a.etudiant.prenom} {a.etudiant.nom}",
            "date": str(a.date),
            "justifiee": a.justifiee,
        }
        for a in Absence.objects.select_related(
            "etudiant"
        )[:50]
    ]

    # ─────────────────────────
    # Stages
    # ─────────────────────────

    ctx["stages"] = [
        {
            "id": s.pk,
            "etudiant": f"{s.etudiant.prenom} {s.etudiant.nom}",
            "entreprise": s.entreprise,
            "sujet": s.sujet,
            "statut": s.statut,
        }
        for s in DemandeStage.objects.select_related(
            "etudiant"
        )[:30]
    ]

    # ─────────────────────────
    # Diplômes
    # ─────────────────────────

    ctx["diplomes"] = [
        {
            "id": d.pk,
            "etudiant": f"{d.etudiant.prenom} {d.etudiant.nom}",
            "type": d.type_diplome,
            "specialite": d.specialite,
            "mention": d.mention,
        }
        for d in Diplome.objects.select_related(
            "etudiant"
        )[:30]
    ]

    # ─────────────────────────
    # Stats
    # ─────────────────────────

    ctx["stats"] = {
        "total_etudiants": Etudiant.objects.count(),
        "total_enseignants": Enseignant.objects.count(),
        "total_notes": Note.objects.count(),
        "total_absences": Absence.objects.count(),
        "total_stages": DemandeStage.objects.count(),
        "stages_en_attente": DemandeStage.objects.filter(
            statut="en_attente"
        ).count(),
        "total_diplomes": Diplome.objects.count(),
    }

    if user:
        ctx["agent_connecte"] = {
            "nom": user.get_full_name(),
            "username": user.username,
        }

    return ctx


# ──────────────────────────────────────────────
# CONTEXT COMPRESSOR
# ──────────────────────────────────────────────

def compress_context(ctx):

    return {
        "stats": ctx.get("stats", {}),
        "etudiants": ctx.get("etudiants", [])[:20],
        "notes": ctx.get("notes", [])[:20],
        "absences": ctx.get("absences", [])[:20],
        "stages": ctx.get("stages", [])[:10],
        "diplomes": ctx.get("diplomes", [])[:10],
    }


# ──────────────────────────────────────────────
# ROUTER
# ──────────────────────────────────────────────

ROUTER_SYSTEM = """
Tu es le routeur du système FSB.

Tu dois choisir l'agent approprié.

Retourne uniquement :

{
  "agent": "...",
  "action": null,
  "params": {},
  "resume": "..."
}

Agents :
- stat
- pedago
- stage
- admin
"""


def router_agent(messages, ctx_json):

    system = (
        ROUTER_SYSTEM
        + f"\n\nSTATS:\n{json.dumps(ctx_json.get('stats', {}), ensure_ascii=False)}"
    )

    return _groq_json(messages[-1:], system)


# ──────────────────────────────────────────────
# AGENTS
# ──────────────────────────────────────────────

def stat_agent(messages, ctx):

    small_ctx = compress_context(ctx)

    system = """
Tu es l'agent statistiques de la FSB.
Tu réponds en français.
Tu analyses les chiffres et tendances.
"""

    return _groq(
        messages,
        system + f"\n\nDONNÉES:\n{json.dumps(small_ctx, ensure_ascii=False)}"
    )


def pedago_agent(messages, ctx):

    small_ctx = compress_context(ctx)

    system = """
Tu es l'agent pédagogique de la FSB.
Tu réponds en français.
Tu aides pour notes, absences, moyennes.
"""

    return _groq(
        messages,
        system + f"\n\nDONNÉES:\n{json.dumps(small_ctx, ensure_ascii=False)}"
    )


def stage_agent(messages, ctx):

    small_ctx = compress_context(ctx)

    system = """
Tu es l'agent stages de la FSB.
Tu réponds en français.
Tu aides pour les demandes de stage.
"""

    return _groq(
        messages,
        system + f"\n\nDONNÉES:\n{json.dumps(small_ctx, ensure_ascii=False)}"
    )


def admin_agent(messages, ctx):

    small_ctx = compress_context(ctx)

    system = """
Tu es l'agent administratif de la FSB.
Tu réponds en français.
Tu aides pour les étudiants, filières, diplômes.
"""

    return _groq(
        messages,
        system + f"\n\nDONNÉES:\n{json.dumps(small_ctx, ensure_ascii=False)}"
    )


# ──────────────────────────────────────────────
# ACTION AGENT
# ──────────────────────────────────────────────

def action_agent(action, params):

    from administration.models import Etudiant
    from pedagogie.models import MoyenneEtudiant
    from stages.models import Diplome

    try:

        # ─────────────────────────
        # VALIDER DIPLÔME
        # ─────────────────────────

        if action == "valider_diplome":

            etudiant_nom = params.get("etudiant_nom", "")

            etudiant = Etudiant.objects.filter(
                nom__icontains=etudiant_nom
            ).first()

            if not etudiant:
                return "❌ Étudiant introuvable."

            moy = MoyenneEtudiant.objects.filter(
                etudiant=etudiant
            ).first()

            moyenne = float(moy.moyenne) if moy else 10

            diplome = Diplome.objects.create(
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

            return (
                f"🎓 Diplôme validé pour "
                f"{etudiant.prenom} {etudiant.nom}"
            )

        return "❌ Action inconnue."

    except Exception as e:
        return f"❌ Erreur : {str(e)}"


# ──────────────────────────────────────────────
# ORCHESTRATEUR
# ──────────────────────────────────────────────

def orchestrate(messages, user=None):

    ctx = build_full_context(user)

    try:

        plan = router_agent(messages, ctx)

        agent = plan.get("agent", "admin")

    except Exception:
        agent = "admin"

    if agent == "stat":
        reply = stat_agent(messages, ctx)

    elif agent == "pedago":
        reply = pedago_agent(messages, ctx)

    elif agent == "stage":
        reply = stage_agent(messages, ctx)

    else:
        reply = admin_agent(messages, ctx)

    return reply, agent, None