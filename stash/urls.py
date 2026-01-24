from django.urls import path
from . import views

urlpatterns = [
	path("", views.FileListView.as_view(), name="file_list"),
	path("view/<pk>", views.FileDetailView.as_view(), name="file_view"),
	path("upload/", views.FileUploadView.as_view(), name="file_upload"),
	path("update/<pk>", views.FileUpdateView.as_view(), name="file_update"),
]