from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path('', views.HomeView.as_view(), name="home_view"),
    path('execute-permit/', views.ExecutePermitView.as_view(), name="permit_execute_view"),
]
