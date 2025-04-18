from django.db import models
from users.models import User  # Assuming your user model is custom

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    room_name = models.CharField(max_length=100)  # e.g., "14-15"
    message = models.TextField(blank=True, null=True)
    
    attachment = models.TextField(blank=True, null=True)  # base64 string or uploaded file URL
    attachment_name = models.CharField(max_length=255, blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} : {self.room_name}"
