from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from stash.models import File

# Create your views here.
class FileListView(ListView):
	model = File
#	paginate_by = 10

class FileDetailView(DetailView):
	model = File

class FileCreateView(LoginRequiredMixin, CreateView):
	model = File
	fields = ["file", "description", "source", "nsfw"]
	redirect_field_name = None

	def form_valid(self, form):
		form.instance.added_by = self.request.user
		return super().form_valid(form)

class FileUpdateView(UpdateView):
	model = File
	fields = ["file", "description", "source", "nsfw"]