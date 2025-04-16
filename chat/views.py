from rest_framework import generics
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class MessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return ChatMessage.objects.filter(sender_id=user_id) | ChatMessage.objects.filter(receiver_id=user_id)