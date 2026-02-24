from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download/<uuid:file_id>/', views.download_file, name='download'),
    path("delete/<uuid:file_id>/", views.delete_file, name="delete"),
    path("share/generate/<uuid:file_id>/", views.generate_share_token, name="generate_token"),
    path("share/<str:token>/", views.token_download, name="token_download"),
]