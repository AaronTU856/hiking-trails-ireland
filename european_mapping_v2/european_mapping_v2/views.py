from django.shortcuts import render

def map_view(request):
    return render(request, 'index.html')

def analytics_view(request):
    return render(request, 'analytics.html')

def dashboard_index(request):
    return render(request, 'index.html') 

