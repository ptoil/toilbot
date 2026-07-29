from django.urls import path
from . import views

urlpatterns = [
	path("", views.FileListView.as_view(), name="file_list"),
	path("view/<pk>", views.FileDetailView.as_view(), name="file_view"),
	path("upload/", views.FileUploadView.as_view(), name="file_upload"),
	path("update/<pk>", views.FileUpdateView.as_view(), name="file_update"),
	path("profile/", views.ProfileView.as_view(), name="profile"),
	path("profile/update/", views.ProfileUpdateView.as_view(), name="profile_update"),
	path("collections/", views.CollectionsView.as_view(), name="collection_list")
]