from django.urls import path
from . import views

urlpatterns = [
	path("", views.FileListView.as_view(), name="file_list"),
	path("view/<pk>", views.FileDetailView.as_view(), name="file_view"),
	path("create/", views.FileCreateView.as_view(), name="file_create"),
	path("update/<pk>", views.FileUpdateView.as_view(), name="file_update"),
]