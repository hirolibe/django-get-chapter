from django.urls import path
from app import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:page>", views.IndexView.as_view(), name="index"),
    path("update/", views.UpdateView.as_view(), name="update"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("search/<int:page>", views.SearchView.as_view(), name="search"),
]