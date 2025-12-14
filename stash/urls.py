from django.urls import path
from . import views

urlpatterns = [
	path("", views.FileListView.as_view(), name="stash"),
	path("view/<pk>", views.FileDetailView.as_view(), name="file_view"),
	path("create/", views.FileCreateView.as_view(), name="file_create")
]