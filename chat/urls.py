from django.urls import path
from chat import views as chat_views


urlpatterns = [
    path("register/", chat_views.register_user, name='videocall'),
    path("", chat_views.my_chats, name="my-chats"),
    path("new_chat/", chat_views.start_new_chat, name="new-chat"),
    path("chat/", chat_views.chat_page, name="chat-page"),
    path("chat/videocall/", chat_views.video_call, name='videocall'),

]
