# mec/urls.py
from django.urls import path
from . import views
app_name = "mec"
urlpatterns = [ path("", views.home, name="home") ]
