from django.db import models
from django.conf import settings

# Create your models here.

class Conversation(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="convo_starter"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="convo_participant"
    )
    room_name = models.TextField(default="r")

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, default=0, related_name='sender')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, default=0, related_name='receiver')
    content = models.TextField(null=True)
    media = models.BinaryField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, related_name='conversation')

    class Meta:
        ordering = ('-timestamp',)
