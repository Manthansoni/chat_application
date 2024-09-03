from django.shortcuts import render
from .models import MyUser as User

# Create your views here.

def user_list(request, ):
    users = User.objects.all().order_by('username')
    return users.data
