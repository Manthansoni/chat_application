from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import MyUser as User
from .models import Message, Conversation

def register_user(request):
    if request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects.filter(username=username).exists()
        if not user:
            user1 = User.objects.create_user(username=username, password=password)
            user1.save()
            redirect("chat")
        else:
            messages.error(request, "Error: Username already exists ")
    return render(request, "chat/RegistrationPage.html")

@login_required(login_url='login-user')
def chat_page(request):
    if request.POST.get('content'):
        recipient_username = request.POST.get('recipient')
        content = request.POST.get('content')
        recipient = User.objects.get(username=recipient_username)
        username = request.POST.get('recipient')
        Message.objects.create(sender=request.user, receiver=recipient, content=content)
    else:
        username = request.POST.get('username')
    userid = request.POST.get('userid')
    room_name = request.POST.get('room_name')
    msg = Message.objects.select_related("sender","receiver").filter(Q(sender_id=request.user.id, receiver_id = userid) | Q(receiver_id=request.user.id, sender_id = userid)).order_by("timestamp")
    timestamp = ''
    for message in msg:
        if not message.read:
            message.read = True
            message.save()
        timestamp = message.timestamp
    return render(request, "chat/chatPage.html", {"userid": userid, "username": username, "messages" : msg, "room_name": room_name, "timestamp":timestamp})

@login_required(login_url='login-user')
def video_call(request):
    receiver = request.POST.get('receiver')
    sender = request.POST.get('sender')
    roomName = request.POST.get('roomName')
    return render(request, "chat/video_call.html",{'sender':sender, "receiver":receiver, "roomName":roomName})

@login_required(login_url='login-user')
def my_chats(request):
    if not request.user.is_authenticated:
        return redirect("login-user")
    chats = Conversation.objects.select_related("sender","receiver").filter(Q(sender=request.user) | Q(receiver=request.user))
    val = {}
    for i in chats:
        if i.sender.id != request.user.id :
            val[i.sender] = i.room_name
        elif i.receiver.id != request.user.id:
            val[i.receiver] = i.room_name
    return render(request, "chat/MyChats.html", {'chats': val})

@login_required(login_url='login-user')
def start_new_chat(request):
    if request.method == "POST":
        recipient_username = request.POST['recipient']
        try:
            recipient = User.objects.get(username=recipient_username)
            if request.user.id < recipient.id :
                room_name = "room_" + str(request.user.id) + str(recipient.id)
            else :
                room_name = "room_" + str(recipient.id) + str(request.user.id)
            already_room = Conversation.objects.filter(Q(sender_id=request.user.id, receiver_id=recipient.id) | Q(receiver_id=request.user.id, sender_id=recipient.id)).count()
            if already_room == 0:
                Conversation.objects.create(sender=request.user, receiver=recipient, room_name = room_name)
            return redirect('my-chats')
        except ObjectDoesNotExist:
            messages.error(request, "Error: Please enter valid username")
    return render(request, 'chat/new_chat.html')
