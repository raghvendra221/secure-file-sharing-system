from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download/<uuid:file_id>/', views.download_file, name='download'),
    path("delete/<uuid:file_id>/", views.delete_file, name="delete"),
]