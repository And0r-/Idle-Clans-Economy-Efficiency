from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # return HttpResponse("Hello world, this is the Idle Clans tracker!")
    return render(request, 'idleclans/index.html')

def gold_efficiency(request):
    return render(request, "gold_efficiency.html")