from django.urls import path
from . import views

urlpatterns = [
	path("", views.FileListView.as_view()),
	path("view/<pk>/", views.FileDetailView.as_view())
]