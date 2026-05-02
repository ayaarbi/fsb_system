from django.urls import path
from . import views
app_name = 'ai_agents'
urlpatterns = [
    path('chat/', views.chat_interface, name='chat'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/history/', views.chat_history, name='chat_history'),
]