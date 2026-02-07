from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from stash.models import File


class FileListView(ListView):
	model = File
#	paginate_by = 2

	
	def get_template_names(self):
		template_names = super().get_template_names()

		if self.request.headers.get("HX-Request"):
			return [f"{i}#content-partial" for i in template_names]
		else:
			return template_names

	def get_queryset(self):
		qs = super(FileListView, self).get_queryset()

		sort = self.request.GET.get("sort", default="modified")
		direction = self.request.GET.get("direction", default="desc")

		prefix = '-' if direction == "desc" else ''

		qs = qs.order_by(f"{prefix}{sort}")
		return qs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		sort = self.request.GET.get("sort", default="modified")
		direction = self.request.GET.get("direction", default="desc")

		context["current_sort"] = sort
		context["current_direction"] = direction
		context["next_direction"] = "asc" if direction == "desc" else "desc"		

		print(context["current_direction"], context["next_direction"])

		return context

#	def get(self, request, *args, **kwargs):
#		super().get(request)




class FileDetailView(DetailView):
	model = File

class FileUploadView(LoginRequiredMixin, CreateView):
	model = File
	fields = ["file", "description", "source", "nsfw"]
	redirect_field_name = None
	template_name_suffix = "_upload_form"

	def form_valid(self, form):
		form.instance.added_by = self.request.user
		return super().form_valid(form)

class FileUpdateView(LoginRequiredMixin, UpdateView):
	model = File
	fields = ["file", "description", "source", "nsfw"]
	redirect_field_name = None
	template_name_suffix = "_update_form"