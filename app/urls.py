from django.urls import path
from app import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:page>", views.IndexView.as_view(), name="index"),
    path("update/", views.UpdateView.as_view(), name="update"),
    path("chapter/", views.ChapterView.as_view(), name="chapter"),
    path("chapter/<int:page>", views.ChapterView.as_view(), name="chapter"),
]