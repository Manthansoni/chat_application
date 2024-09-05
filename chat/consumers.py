import json
from channels.generic.websocket import WebsocketConsumer
from user.models import MyUser as User
from .models import Message
from asgiref.sync import async_to_sync
import datetime
from django.core.files.base import ContentFile
import base64

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        if self.scope["user"].is_anonymous:
            self.close()
        else:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f"chat_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        print(self.room_group_name)
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(e)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        eventType = text_data_json.get('type')
        if "receiver_id" in text_data_json:
            user_id = text_data_json["receiver_id"]
            recipient = User.objects.get(id=user_id)
            sender = self.scope['user']

            image_data = text_data_json.get('image_data')
            file_name = text_data_json.get('file_name')
            binary_image = None

            if file_name:
                file_name = self.room_name+ "_" + file_name

            if image_data and file_name:
                print("Inside images")
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]  # Extract the file extension (e.g., png, jpeg)
                # Decode the image and save it as binary data
                binary_image = base64.b64decode(imgstr)
                Message.objects.create(sender=sender, receiver=recipient, media=binary_image)


            message = ''
            if text_data_json.get("message") is not None:
                message = text_data_json["message"]
                msg = Message.objects.create(sender=sender, receiver=recipient, content=message)

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {
                    'type': 'chat_message',
                    'media': binary_image,
                    'message': message,
                    'sender': sender.username,
                })

        # Video Call
        if eventType == 'login':
            name = text_data_json['data']['name']

            # we will use this as room name as well
            self.my_name = name

            # Join room
            async_to_sync(self.channel_layer.group_add)(
                self.my_name,
                self.channel_name
            )

        if eventType == 'call':
            name = text_data_json['data']['name']

            # to notify the callee we sent an event to the group name and their group name is the name
            async_to_sync(self.channel_layer.group_send)(
                name,
                {
                    'type': 'call_received',
                    'data': {
                        'caller': self.my_name,
                        'rtcMessage': text_data_json['data']['rtcMessage']
                    }
                }
            )

        if eventType == 'answer_call':
            # has received call from someone now notify the calling user
            # we can notify to the group with the caller name

            caller = text_data_json['data']['caller']

            async_to_sync(self.channel_layer.group_send)(
                caller,
                {
                    'type': 'call_answered',
                    'data': {
                        'rtcMessage': text_data_json['data']['rtcMessage']
                    }
                }
            )

        if eventType == 'ICEcandidate':
            user = text_data_json['data']['user']

            async_to_sync(self.channel_layer.group_send)(
                user,
                {
                    'type': 'ICEcandidate',
                    'data': {
                        'rtcMessage': text_data_json['data']['rtcMessage']
                    }
                }
            )

    def call_received(self, event):

        self.send(text_data=json.dumps({
            'type': 'call_received',
            'data': event['data']
        }))

    def call_answered(self, event):

        self.send(text_data=json.dumps({
            'type': 'call_answered',
            'data': event['data']
        }))

    def ICEcandidate(self, event):
        self.send(text_data=json.dumps({
            'type': 'ICEcandidate',
            'data': event['data']
        }))


    def chat_message(self, event):
        media = event['media']
        message = event['message']
        sender = event['sender']
        dt = datetime.datetime.now()
        timestamp = dt.strftime('%b. %d, %Y, %-I:%M %p')

        self.send(text_data=json.dumps({
            'media': media,
            'message': message,
            'sender': sender,
            'timestamp': timestamp,
        }))
