from django.urls import path
from . import views
app_name = 'tracker'
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('projects/', views.project_list, name='projects'),
    path('projects/<int:pk>/', views.project_detail, name='detail'),
    path('developers/', views.developers, name='developers'),
    path('developers/<int:pk>/', views.developer_detail, name='developer'),
    path('technologies/', views.technologies, name='technologies'),
    path('statistics/', views.statistics, name='statistics'),
]
