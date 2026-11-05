from datetime import date
from django.http import Http404
from django.shortcuts import render
from service import statistics as calculate
from .repository import state

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def project_list(request):
    return render(request, 'projects.html', {'projects': state()['projects']})

def project_detail(request, pk):
    p = next((p for p in state()['projects'] if p.id == pk), None)
    if p is None:
        raise Http404
    return render(request, 'detail.html', {'p': p, 'technologies': p.technologies})

def developers(request):
    return render(request, 'references.html', {'title': 'Разработчики', 'items': state()['developers']})

def developer_detail(request, pk):
    data = state()
    p = next((p for p in data['developers'] if p.id == pk), None)
    if p is None:
        raise Http404
    return render(request, 'developer.html', {'developer': p, 'projects': [x for x in data['projects'] if x.developer.id == pk]})

def technologies(request):
    return render(request, 'references.html', {'title': 'Технологии', 'items': state()['technologies']})

def statistics(request):
    return render(request, 'statistics.html', {'stats': calculate(state(), date.today())})

def not_found(request, exception):
    return render(request, '404.html', status=404)
