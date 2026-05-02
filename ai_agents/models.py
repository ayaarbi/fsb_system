from django.db import models
from accounts.models import CustomUser

class ConversationChat(models.Model):
    AGENT_CHOICES = [
        ('assistant_admin', 'Assistant Administratif'),
        ('assistant_pedagogique', 'Assistant Pédagogique'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    agent_type = models.CharField(max_length=30, choices=AGENT_CHOICES)
    titre = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.agent_type} - {self.user} ({self.created_at.date()})"


class MessageChat(models.Model):
    conversation = models.ForeignKey(ConversationChat, on_delete=models.CASCADE,
                                     related_name='messages')
    role = models.CharField(max_length=10,
                            choices=[('user','Utilisateur'),('assistant','Assistant')])
    contenu = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.contenu[:60]}"