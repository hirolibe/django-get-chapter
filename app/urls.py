from django.urls import path
from app import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("update/", views.UpdateView.as_view(), name="update"),
    path("gakuchofather/", views.GakuchoFatherView.as_view(), name="gakuchofather"),
]