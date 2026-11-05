from django.urls import include, path
urlpatterns = [path('', include('tracker.urls'))]
handler404 = 'tracker.views.not_found'
