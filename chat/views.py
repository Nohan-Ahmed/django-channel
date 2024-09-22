from django.shortcuts import render
from . import models
# Create your views here.
def index(request, room_name):
    
    return render(request, './chat/index.html',{'room_name':room_name})