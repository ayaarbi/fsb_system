import json
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import ConversationChat, MessageChat
from pedagogie.models import Note, Absence


def get_user_context(user):
    """
    Contexte pour l'agent IA.
    user = agent admin connecté (pas un étudiant).
    """
    from administration.models import Etudiant, Enseignant, Departement

    ctx  = "Tu es un assistant IA de la Faculté des Sciences de Bizerte (FSB), "
    ctx += "Université de Carthage, Tunisie.\n"
    ctx += "Tu parles UNIQUEMENT avec des agents administratifs de la FSB. "
    ctx += "Ces agents gèrent les étudiants, enseignants, notes, stages et diplômes.\n"
    ctx += f"Agent connecté : {user.get_full_name()} — Rôle : {user.get_role_display()}\n"
    ctx += f"Département géré : {user.departement or 'Tous les départements'}\n\n"

    # Statistiques globales pour contexte
    ctx += f"Statistiques FSB actuelles :\n"
    ctx += f"- Étudiants inscrits : {Etudiant.objects.filter(statut='inscrit').count()}\n"
    ctx += f"- Enseignants actifs : {Enseignant.objects.filter(actif=True).count()}\n"
    ctx += f"- Départements : Mathématiques, Informatique, Physique, Chimie, Sciences de la Vie, Sciences de la Terre\n"

    return ctx

def call_anthropic_agent(messages_history, user_context, agent_type):
    """Agent 1 — Claude Haiku via Anthropic API"""
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key:
        return call_fsb_offline_agent(messages_history[-1]['content'], agent_type)

    if agent_type == 'assistant_admin':
        system = (user_context +
                  "\nTu es l'Assistant Administratif FSB. Tu aides avec les "
                  "inscriptions, demandes de documents, stages et procédures. "
                  "Réponds en français, de façon claire et professionnelle.")
    else:
        system = (user_context +
                  "\nTu es l'Assistant Pédagogique FSB. Tu aides avec les cours, "
                  "notes, absences, emplois du temps et l'orientation académique. "
                  "Réponds en français.")
    try:
        resp = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': 'claude-haiku-4-5-20251001',
                'max_tokens': 800,
                'system': system,
                'messages': messages_history,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()['content'][0]['text']
    except Exception:
        pass
    return call_fsb_offline_agent(messages_history[-1]['content'], agent_type)


def call_fsb_offline_agent(user_message, agent_type):
    """Agent 2 — Agent FSB hors-ligne (règles métier)"""
    msg = user_message.lower()

    # Base de connaissances FSB
    knowledge = {
        'note': "Pour consulter vos notes, allez dans Pédagogie > Notes. "
                "Pour toute réclamation, adressez-vous au secrétariat de votre département "
                "dans les 72h suivant la publication.",
        'absence': "Après 3 absences non justifiées par matière, vous pouvez être convoqué "
                   "par le chef de département. Justificatifs à déposer au secrétariat "
                   "dans les 48h de votre retour.",
        'inscription': ("Inscriptions au service scolarité, Bât. A, RDC.\n"
                        "📋 Documents requis:\n• CIN originale + copie\n• Baccalauréat\n"
                        "• 4 photos d'identité\n• Attestation de résidence\n"
                        "📞 Tél: +216 72 591 906"),
        'stage': ("Remplissez le formulaire en ligne dans Stages > Nouvelle Demande.\n"
                  "📋 Pièces:\n• Lettre de motivation\n• CV\n• Convention signée\n"
                  "Délai de validation: 5 à 7 jours ouvrables."),
        'examen': ("Sessions d'examens:\n• Principale S1: Janvier\n• Principale S2: Juin\n"
                   "• Rattrapage S1: Février\n• Rattrapage S2: Juillet\n"
                   "Planning disponible dans Examens > Planning."),
        'diplome': ("Demande au service scolarité.\n"
                    "📋 Documents:\n• Photocopie CIN\n• Photo d'identité\n"
                    "• Quittance des frais universitaires\n"
                    "⏱️ Délai: 15 à 30 jours."),
        'departement': ("La FSB compte 6 départements:\n"
                        "💻 Informatique\n📐 Mathématiques\n🔭 Physique\n"
                        "⚗️ Chimie\n🔬 Sciences de la Vie\n🌍 Sciences de la Terre\n"
                        "Site: www.fsb.rnu.tn"),
        'contact': ("📍 FSB, Jarzouna, 7021 Bizerte\n"
                    "📞 +216 72 591 906\n📧 contact@fsb.rnu.tn\n"
                    "🌐 www.fsb.rnu.tn\n⏰ Lun-Ven 8h-17h"),
        'emploi': "Votre emploi du temps est dans Pédagogie > Emploi du temps. "
                  "Filtrez par filière pour voir vos créneaux.",
        'bourse': "Pour les bourses universitaires, contactez le service social "
                  "(Bât. B) ou le CROUS. Dossiers à déposer en octobre.",
        'bibliotheque': "La bibliothèque FSB est ouverte Lun-Ven 8h-18h. "
                        "Carte étudiante obligatoire pour emprunter.",
    }

    for key, response in knowledge.items():
        keywords = {
            'note': ['note', 'résultat', 'score', 'moyenne', 'résultats'],
            'absence': ['absence', 'présence', 'séance', 'manqué'],
            'inscription': ['inscription', 'inscrire', 'réinscription', 'scolarité'],
            'stage': ['stage', 'pfe', 'entreprise', 'convention'],
            'examen': ['examen', 'session', 'rattrapage', 'épreuve'],
            'diplome': ['diplome', 'diplôme', 'attestation', 'relevé'],
            'departement': ['département', 'departement', 'filière', 'filiere'],
            'contact': ['contact', 'téléphone', 'adresse', 'localisation'],
            'emploi': ['horaire', 'emploi du temps', 'cours', 'créneaux'],
            'bourse': ['bourse', 'aide', 'social', 'crous'],
            'bibliotheque': ['bibliothèque', 'bibliotheque', 'livre', 'emprunter'],
        }.get(key, [key])
        if any(kw in msg for kw in keywords):
            return response

    return ("Bonjour! Je suis l'assistant IA de la FSB. Je peux vous aider avec:\n"
            "📋 Inscriptions et scolarité\n📊 Notes et résultats\n"
            "❌ Absences\n💼 Stages et PFE\n📅 Examens et planning\n"
            "🎓 Diplômes\n🏛️ Informations sur les départements\n\n"
            "Que puis-je faire pour vous?")


@login_required
def chat_interface(request):
    agent_type = request.GET.get('agent', 'assistant_admin')
    conversations = ConversationChat.objects.filter(
        user=request.user).order_by('-created_at')[:5]
    conv_id = request.GET.get('conv')
    current_conv, conv_messages = None, []
    if conv_id:
        try:
            current_conv = ConversationChat.objects.get(pk=conv_id, user=request.user)
            conv_messages = MessageChat.objects.filter(
                conversation=current_conv).order_by('timestamp')
        except ConversationChat.DoesNotExist:
            pass
    return render(request, 'ai_agents/chat.html', {
        'agent_type': agent_type,
        'conversations': conversations,
        'current_conv': current_conv,
        'conv_messages': conv_messages,
        'has_api_key': bool(settings.ANTHROPIC_API_KEY),
    })


@login_required
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        user_msg = data.get('message', '').strip()
        agent_type = data.get('agent_type', 'assistant_admin')
        conv_id = data.get('conversation_id')
        if not user_msg:
            return JsonResponse({'error': 'Message vide'}, status=400)

        if conv_id:
            try:
                conv = ConversationChat.objects.get(pk=conv_id, user=request.user)
            except ConversationChat.DoesNotExist:
                conv = ConversationChat.objects.create(
                    user=request.user, agent_type=agent_type, titre=user_msg[:60])
        else:
            conv = ConversationChat.objects.create(
                user=request.user, agent_type=agent_type, titre=user_msg[:60])

        MessageChat.objects.create(conversation=conv, role='user', contenu=user_msg)

        prev = MessageChat.objects.filter(conversation=conv).order_by('timestamp')
        history = [{'role': m.role, 'content': m.contenu} for m in prev]

        ctx = get_user_context(request.user)
        reply = call_anthropic_agent(history, ctx, agent_type)
        MessageChat.objects.create(conversation=conv, role='assistant', contenu=reply)

        return JsonResponse({'response': reply, 'conversation_id': conv.pk})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def chat_history(request):
    conversations = ConversationChat.objects.filter(
        user=request.user).order_by('-created_at')
    return render(request, 'ai_agents/history.html', {'conversations': conversations})