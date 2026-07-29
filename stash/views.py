from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404
from django.core.paginator import InvalidPage

from .models import File, Profile, Collection
from .forms import FileForm

class FileListView(ListView):
	model = File
	paginate_by = 3
	
	def get_template_names(self):
		template_names = super().get_template_names()
		if self.request.headers.get("HX-Request"):
			return [f"{i}#content-partial" for i in template_names]
		else:
			return template_names

	def get_queryset(self):
		qs = super(FileListView, self).get_queryset()

		#check URL request, then user settings if logged in, or default if logged out
		if self.request.user.is_authenticated and self.request.user.socialaccount_set.exists():
			nsfw = self.request.GET.get("nsfw", default=self.request.user.profile.nsfw)
			sort = self.request.GET.get("sort", default=self.request.user.profile.sort)
			direction = self.request.GET.get("direction", default=self.request.user.profile.direction)
		else:
			nsfw = self.request.GET.get("nsfw", default="sfw")
			sort = self.request.GET.get("sort", default="modified")
			direction = self.request.GET.get("direction", default="desc")
		page = self.request.GET.get("page", default=1)
		query = self.request.GET.get("q", default="")


		if nsfw == "nsfw":  qs = qs.filter(nsfw=True)
		elif nsfw == "sfw": qs = qs.filter(nsfw=False)
		#else keep both

		prefix = '-' if direction == "desc" else ''

		qs = qs.order_by(f"{prefix}{sort}")
		if query:
			qs = qs.autocomplete(query)
		return qs

	#Overriding to handle page oob error from switching filters. changing behavior to load last page
	def paginate_queryset(self, queryset, page_size):
		paginator = self.get_paginator(
			queryset,
			page_size,
			orphans=self.get_paginate_orphans(),
			allow_empty_first_page=self.get_allow_empty(),
		)

		page_kwarg = self.page_kwarg
		page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
		
		try:
			page_number = int(page)
		except ValueError:
			if page == "last":
				page_number = paginator.num_pages
			else:
				raise Http404(
					_("Page is not “last”, nor can it be converted to an int.")
				)
		try:
			page = paginator.page(page_number)
		except InvalidPage as e:
			page = paginator.page(paginator.num_pages)

		return (paginator, page, page.object_list, page.has_other_pages())

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		#check URL request, then user settings if logged in, or default if logged out
		if self.request.user.is_authenticated and self.request.user.socialaccount_set.exists():
			nsfw = self.request.GET.get("nsfw", default=self.request.user.profile.nsfw)
			sort = self.request.GET.get("sort", default=self.request.user.profile.sort)
			direction = self.request.GET.get("direction", default=self.request.user.profile.direction)
		else:
			nsfw = self.request.GET.get("nsfw", default="sfw")
			sort = self.request.GET.get("sort", default="modified")
			direction = self.request.GET.get("direction", default="desc")
		page = self.request.GET.get("page", default=1)
		query = self.request.GET.get("q", default="")

		filters = {
			"sort" : sort,
			"direction" : direction,
			"nsfw" : nsfw,
			"page" : page,
			"q" : query,
		}
		context["filters"] = filters
		return context


class FileDetailView(DetailView):
	model = File

class FileUploadView(LoginRequiredMixin, CreateView):
	model = File
	form_class = FileForm
	redirect_field_name = None
	template_name_suffix = "_upload_form"

	def form_valid(self, form):
		form.instance.added_by = self.request.user
		return super().form_valid(form)

class FileUpdateView(LoginRequiredMixin, UpdateView):
	model = File
	form_class = FileForm
	redirect_field_name = None
	template_name_suffix = "_update_form"


class CollectionsView(ListView):
	model = Collection
#	paginate_by = 2


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