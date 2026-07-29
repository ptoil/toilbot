import os
from django.db import models
from django.urls import reverse
from django.conf import settings

from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added, social_account_updated
from modelsearch import index
from modelsearch.queryset import SearchableQuerySetMixin

class Collection(models.Model):

	name = models.CharField()
	nsfw = models.BooleanField(default=False, verbose_name="NSFW")

	def __str__(self):
		return self.name


class FileQuerySet(SearchableQuerySetMixin, models.QuerySet):
	pass

class File(index.Indexed, models.Model):
	
	#User editable
	file = models.FileField() #move to temp folder if model is deleted (acts as recycle bin, isnt fully deleted until admin confirms)
	description = models.TextField(blank=True)
	source = models.CharField(blank=True)
#	author = models.CharField(blank=True)
	nsfw = models.BooleanField(default=False, verbose_name="NSFW")
#	related = models.JSONField()
	collections = models.ManyToManyField(Collection, blank=True)

	#Automatic
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
	link = models.URLField(blank=True)
#	link_updated = models.DateTimeField()
#	file_size_bytes = models.PositiveIntegerField()
#	file_video_length = models.DurationField()

	objects = FileQuerySet.as_manager()
	search_fields = [
		index.AutocompleteField("file"),
		index.AutocompleteField("description"),

		index.FilterField("nsfw")
	]

	def file_type(self):
		extension = os.path.splitext(self.file.name)[1].lower()
		if extension in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"):
			return "image"
		elif extension in (".mp4", ".mkv", ".avi", ".mov", ".webm"):
			return "video"
		elif extension in (".mp3", ".wav", ".ogg", ".m4a"):
			return "audio"
		else:
			return "other"

	def get_absolute_url(self):
		return reverse("file_view", kwargs={"pk": self.pk})

	def __str__(self):
		return self.file.name


class Profile(models.Model):

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	#Filters
	nsfw = models.CharField(default="sfw")
	sort = models.CharField(default="modified")
	direction = models.CharField(default="desc")


@receiver(social_account_added)
def create_profile(request, sociallogin, **kwargs):
	Profile.objects.get_or_create(user=sociallogin.user)

@receiver(social_account_updated)
def create_profile(request, sociallogin, **kwargs):
	Profile.objects.get_or_create(user=sociallogin.user)