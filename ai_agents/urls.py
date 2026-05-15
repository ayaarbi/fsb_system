from django.urls import path
from . import views
app_name = 'ai_agents'
urlpatterns = [
    path('chat/', views.chat_interface, name='chat'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/history/', views.chat_history, name='chat_history'),
    path('chat/delete/<int:conv_id>/', views.delete_conversation, name='delete_conversation'),
    path('chat/clear/',        views.clear_all_conversations, name='clear_all'),
]
 