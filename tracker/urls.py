from django.urls import path
from . import views
app_name = 'tracker'
urlpatterns = [path('projects/new/', views.project_edit, name='create'),path('projects/<int:pk>/edit/', views.project_edit, name='edit'),path('available/', views.available, name='available'),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('projects/', views.project_list, name='projects'),
    path('projects/<int:pk>/', views.project_detail, name='detail'),
    path('developers/', views.developers, name='developers'),
    path('developers/<int:pk>/', views.developer_detail, name='developer'),
    path('technologies/', views.technologies, name='technologies'),
    path('statistics/', views.statistics, name='statistics'),
]
