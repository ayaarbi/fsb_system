# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import ConversationChat, MessageChat
from .agents import orchestrate   # ← le système multi-agent


@login_required
def chat_interface(request):
    conversations = ConversationChat.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    conv_id = request.GET.get('conv')
    current_conv, conv_messages = None, []

    if conv_id:
        try:
            current_conv = ConversationChat.objects.get(pk=conv_id, user=request.user)
            conv_messages = MessageChat.objects.filter(
                conversation=current_conv
            ).order_by('timestamp')
        except ConversationChat.DoesNotExist:
            pass

    return render(request, 'ai_agents/chat.html', {
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
        conv_id = data.get('conversation_id')

        if not user_msg:
            return JsonResponse({'error': 'Message vide'}, status=400)

        # ── Conversation ──────────────────────────────────
        if conv_id:
            try:
                conv = ConversationChat.objects.get(pk=conv_id, user=request.user)
            except ConversationChat.DoesNotExist:
                conv = ConversationChat.objects.create(
                    user=request.user,
                    agent_type='multi',
                    titre=user_msg[:60]
                )
        else:
            conv = ConversationChat.objects.create(
                user=request.user,
                agent_type='multi',
                titre=user_msg[:60]
            )

        # Sauvegarder le message utilisateur
        MessageChat.objects.create(conversation=conv, role='user', contenu=user_msg)

        # Historique complet pour le contexte
        prev = MessageChat.objects.filter(conversation=conv).order_by('timestamp')
        history = [{'role': m.role, 'content': m.contenu} for m in prev]

        # ── Orchestration multi-agent ─────────────────────
        reply, agent_used, action_taken = orchestrate(history, user=request.user)

        # Sauvegarder la réponse
        MessageChat.objects.create(conversation=conv, role='assistant', contenu=reply)

        return JsonResponse({
            'response': reply,
            'conversation_id': conv.pk,
            'agent_used': agent_used,
            'action_taken': action_taken,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def chat_history(request):
    conversations = ConversationChat.objects.filter(
        user=request.user
    ).order_by('-created_at')
    return render(request, 'ai_agents/history.html', {'conversations': conversations})


@login_required
def delete_conversation(request, conv_id):
    """Supprimer une conversation."""
    if request.method == 'POST':
        conv = get_object_or_404(ConversationChat, pk=conv_id, user=request.user)
        conv.delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def clear_all_conversations(request):
    """Supprimer toutes les conversations de l'utilisateur."""
    if request.method == 'POST':
        ConversationChat.objects.filter(user=request.user).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)