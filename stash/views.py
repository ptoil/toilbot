from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from stash.models import File

# Create your views here.
class FileListView(ListView):
	model = File
#	paginate_by = 10

class FileDetailView(DetailView):
	model = File

class FileCreateView(CreateView):
	model = File
	fields = ["file", "description"]