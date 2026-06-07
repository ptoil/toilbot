from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from stash.models import File, Profile


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

		#check URL request, then user settings if logged in, then default
		if self.request.user.is_authenticated:
			nsfw = self.request.GET.get("nsfw", default=self.request.user.profile.nsfw)
			sort = self.request.GET.get("sort", default=self.request.user.profile.sort)
			direction = self.request.GET.get("direction", default=self.request.user.profile.direction)
		else:
			nsfw = self.request.GET.get("nsfw", default="sfw")
			sort = self.request.GET.get("sort", default="modified")
			direction = self.request.GET.get("direction", default="desc")

		if nsfw == "nsfw":  qs = qs.filter(nsfw=True)
		elif nsfw == "sfw": qs = qs.filter(nsfw=False)
		#else keep both

		prefix = '-' if direction == "desc" else ''

		qs = qs.order_by(f"{prefix}{sort}")
		return qs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		#check URL request, then user settings if logged in, then default
		if self.request.user.is_authenticated:
			nsfw = self.request.GET.get("nsfw", default=self.request.user.profile.nsfw)
			sort = self.request.GET.get("sort", default=self.request.user.profile.sort)
			direction = self.request.GET.get("direction", default=self.request.user.profile.direction)
		else:
			nsfw = self.request.GET.get("nsfw", default="sfw")
			sort = self.request.GET.get("sort", default="modified")
			direction = self.request.GET.get("direction", default="desc")

		filters = {
			"sort" : sort,
			"direction" : direction,
			"nsfw" : nsfw
		}
		context["filters"] = filters
		return context


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


class ProfileView(LoginRequiredMixin, TemplateView):
	template_name = "stash/profile.html"

	"""
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		profile = self.request.user.profile
		context["filters"] = {
			"sort" : profile.sort,
			"direction" : profile.direction,
			"nsfw" : profile.nsfw
		}
		return context
	"""

class JsonableResponseMixin:
	def form_invalid(self, form):
		response = super().form_invalid(form)
		return JsonResponse(form.errors, status=400)

	def form_valid(self, form):
		response = super().form_valid(form)
		data = {'status': 'success', 'message': 'Profile updated!'}
		return JsonResponse(data)

class ProfileUpdateView(LoginRequiredMixin, JsonableResponseMixin, UpdateView):
	model = Profile
	fields = ["nsfw", "sort", "direction"]

	def get_object(self, queryset=None):
		return self.request.user.profile

	def get_success_url(self):
		return '#'