from django.http import HttpResponse, Http404
from django.utils.html import escape
from .repository import state

def page(title, body):
    return HttpResponse('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">'
        '<title>'+escape(title)+'</title></head><body class="container"><nav>'
        '<a href="/">Главная</a> | <a href="/projects/">Проекты</a> | '
        '<a href="/developers/">Разработчики</a> | <a href="/technologies/">Технологии</a> | '
        '<a href="/statistics/">Статистика</a> | <a href="/about/">О проекте</a>'
        '</nav><h1>'+escape(title)+'</h1>'+body+'</body></html>')

def home(request):
    return page('Система учета программных проектов', '<p>Проекты, разработчики, технологии и статусы.</p>')

def about(request):
    return page('О проекте', '<p>Семин Матвей Романович, ЭФБО-10-24.</p>')

def project_list(request):
    return page('Проекты', ''.join(f'<p><a href="/projects/{p.id}/">{escape(p.name)}</a> — {escape(p.status.name)}</p>' for p in state()['projects']))

def project_detail(request, pk):
    p = next((p for p in state()['projects'] if p.id == pk), None)
    if p is None:
        raise Http404
    return page(p.name, f'<p>{escape(p.developer.name)} — {p.deadline} — {escape(p.status.name)}</p>')

def developers(request):
    return page('Разработчики', ''.join(f'<p><a href="/developers/{p.id}/">{escape(p.name)}</a></p>' for p in state()['developers']))

def developer_detail(request, pk):
    p = next((p for p in state()['developers'] if p.id == pk), None)
    if p is None:
        raise Http404
    return page(p.name, ''.join(f'<p>{escape(x.name)}</p>' for x in state()['projects'] if x.developer.id == pk))

def technologies(request):
    return page('Технологии', ''.join(f'<p>{escape(p.name)}</p>' for p in state()['technologies']))

def statistics(request):
    return page('Статистика', f"<p>Всего проектов: {len(state()['projects'])}</p>")

def not_found(request, exception):
    response = page('Страница не найдена', '<p>Проверьте адрес.</p>')
    response.status_code = 404
    return response
