from datetime import date
from django.http import Http404
from django.shortcuts import render
from .repository import state

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def project_list(request):
    from db.queries import list_projects
    return render(request, 'sql_projects.html', {'projects': list_projects(request.GET.get('q',''))})

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
    from db.queries import statistics as sql_statistics
    return render(request, 'statistics.html', {'stats': {r['name']:r['total'] for r in sql_statistics()}})

def not_found(request, exception):
    return render(request, '404.html', status=404)

def available(request):
    from db.queries import available_developers
    value = request.GET.get('date', date.today().isoformat())
    try:
        date.fromisoformat(value)
    except ValueError:
        return render(request, 'available.html', {'error': 'Некорректная дата'}, status=400)
    return render(request, 'available.html', {'items': available_developers(value), 'date': value})
