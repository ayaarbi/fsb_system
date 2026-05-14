import json
from groq import Groq
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import ConversationChat, MessageChat
from administration.models import Etudiant, Enseignant, Departement, Filiere
from pedagogie.models import Absence, Note, MoyenneEtudiant
from stages.models import DemandeStage, Diplome

def get_user_context(user):
    

    ctx  = "Tu es un assistant IA de la Faculté des Sciences de Bizerte (FSB).\n"
    ctx += "Tu parles UNIQUEMENT avec des agents administratifs de la FSB.\n"
    ctx += f"Agent connecté : {user.get_full_name()} — Rôle : {user.get_role_display()}\n"
    ctx += f"Département géré : {user.departement or 'Tous les départements'}\n\n"

    # === DÉPARTEMENTS ===
    ctx += "=== DÉPARTEMENTS ===\n"
    for d in Departement.objects.all():
        nb = Etudiant.objects.filter(filiere__departement=d, statut='inscrit').count()
        ctx += f"- {d.nom} : {nb} étudiants inscrits\n"
    ctx += "\n"

    # === FILIÈRES ===
    ctx += "=== FILIÈRES ===\n"
    for f in Filiere.objects.all():
        nb = Etudiant.objects.filter(filiere=f, statut='inscrit').count()
        ctx += f"- {f.nom} ({f.code}) | Niveau: {f.niveau} | {nb} étudiants\n"
    ctx += "\n"

    # === ÉTUDIANTS ===
    ctx += "=== ÉTUDIANTS INSCRITS ===\n"
    for e in Etudiant.objects.filter(statut='inscrit').select_related('filiere')[:300]:
        ctx += (f"- {e.nom} {e.prenom} | N°{e.numero_etudiant} | "
                f"Filière: {e.filiere.nom if e.filiere else 'N/A'}\n")
    ctx += "\n"

    # === ENSEIGNANTS ===
    ctx += "=== ENSEIGNANTS ===\n"
    for e in Enseignant.objects.filter(actif=True).select_related('departement'):
        ctx += (f"- {e.nom} {e.prenom} | Grade: {e.grade} | "
                f"Spécialité: {e.specialite} | Dép: {e.departement}\n")
    ctx += "\n"

    # === NOTES ===
    ctx += "=== NOTES ===\n"
    for n in Note.objects.select_related('etudiant', 'matiere').all()[:300]:
        ctx += (f"- {n.etudiant.nom} {n.etudiant.prenom} | "
                f"Matière: {n.matiere.nom if n.matiere else 'N/A'} | "
                f"Note: {n.note}/20 | Type: {n.type_note} | "
                f"S{n.semestre} {n.annee_universitaire}\n")
    ctx += "\n"

    # === MOYENNES ===
    ctx += "=== MOYENNES ===\n"
    for m in MoyenneEtudiant.objects.select_related('etudiant').all()[:300]:
        ctx += (f"- {m.etudiant.nom} {m.etudiant.prenom} | "
                f"Moyenne: {m.moyenne}/20 | Mention: {m.mention} | "
                f"{'Admis' if m.admis else 'Non admis'} | "
                f"S{m.semestre} {m.annee_universitaire}\n")
    ctx += "\n"

    # === ABSENCES ===
    ctx += "=== ABSENCES ===\n"
    for a in Absence.objects.select_related('etudiant').all()[:300]:
        ctx += (f"- {a.etudiant.nom} {a.etudiant.prenom} | "
                f"Date: {a.date} | "
                f"{'Justifiée' if a.justifiee else 'Non justifiée'} | "
                f"Motif: {a.motif or 'Aucun'}\n")
    ctx += "\n"

    # === DEMANDES DE STAGE ===
    ctx += "=== DEMANDES DE STAGE ===\n"
    for s in DemandeStage.objects.select_related('etudiant').all()[:100]:
        ctx += (f"- {s.etudiant.nom} {s.etudiant.prenom} | "
                f"Entreprise: {s.entreprise} | Sujet: {s.sujet} | "
                f"Statut: {s.statut} | "
                f"Du {s.date_debut} au {s.date_fin}\n")
    ctx += "\n"

    # === DIPLÔMES ===
    ctx += "=== DIPLÔMES ===\n"
    for d in Diplome.objects.select_related('etudiant').all()[:100]:
        ctx += (f"- {d.etudiant.nom} {d.etudiant.prenom} | "
                f"Diplôme: {d.type_diplome} | Spécialité: {d.specialite} | "
                f"Mention: {d.mention} | Moyenne: {d.moyenne_generale}/20 | "
                f"Année: {d.annee_obtention}\n")
    ctx += "\n"

    # === STATISTIQUES ===
    ctx += "=== STATISTIQUES GÉNÉRALES ===\n"
    ctx += f"- Total étudiants inscrits : {Etudiant.objects.filter(statut='inscrit').count()}\n"
    ctx += f"- Total enseignants actifs : {Enseignant.objects.filter(actif=True).count()}\n"
    ctx += f"- Total absences : {Absence.objects.count()}\n"
    ctx += f"- Total notes saisies : {Note.objects.count()}\n"
    ctx += f"- Total demandes de stage : {DemandeStage.objects.count()}\n"
    ctx += f"- Total diplômes délivrés : {Diplome.objects.count()}\n"

    # === CONTACTS FSB ===
    ctx += "\n=== CONTACTS FSB ===\n"
    ctx += "- Adresse : Jarzouna, 7021 Bizerte, Tunisie\n"
    ctx += "- Téléphone : +216 72 591 906\n"
    ctx += "- Email : contact@fsb.rnu.tn\n"
    ctx += "- Site web : www.fsb.rnu.tn\n"
    ctx += "- Horaires : Lundi-Vendredi 8h-17h\n"

    return ctx


def call_gemini_agent(messages_history, user_context, agent_type):
    

    api_key = settings.GROQ_API_KEY
    if not api_key:
        return call_fsb_offline_agent(messages_history[-1]['content'], agent_type)

    if agent_type == 'assistant_admin':
        role = ("Tu es l'Assistant Administratif FSB. "
                "Tu aides avec les inscriptions, documents, stages et procedures. "
                "Reponds en francais, de facon claire et professionnelle.")
    else:
        role = ("Tu es l'Assistant Pedagogique FSB. "
                "Tu aides avec les cours, notes, absences et orientation. "
                "Reponds en francais.")

    system = (
        role + "\n\n"
        "INSTRUCTIONS IMPORTANTES:\n"
        "- Utilise UNIQUEMENT les donnees ci-dessous pour repondre.\n"
        "- Ne invente JAMAIS de donnees fictives.\n"
        "- Si une information n'existe pas dans les donnees, dis-le clairement.\n"
        "- Reponds toujours en francais.\n\n"
        "=== DONNEES REELLES DE L'APPLICATION ===\n"
        + user_context
    )

    try:
        client = Groq(api_key=api_key)
        messages = [{'role': 'system', 'content': system}]
        for m in messages_history:
            messages.append({'role': m['role'], 'content': m['content']})

        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=messages,
            max_tokens=1000,
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq error: {e}")
        return call_fsb_offline_agent(messages_history[-1]['content'], agent_type)


def call_fsb_offline_agent(user_message, agent_type):
    msg = user_message.lower()
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
        'has_api_key': bool(settings.GROQ_API_KEY),
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
        reply = call_gemini_agent(history, ctx, agent_type)
        MessageChat.objects.create(conversation=conv, role='assistant', contenu=reply)
        return JsonResponse({'response': reply, 'conversation_id': conv.pk})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def chat_history(request):
    conversations = ConversationChat.objects.filter(
        user=request.user).order_by('-created_at')
    return render(request, 'ai_agents/history.html', {'conversations': conversations})

