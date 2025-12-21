import os
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class File(models.Model):

	file = models.FileField() #move to temp folder if model is deleted (acts as recycle bin, isnt fully deleted until admin confirms)
	description = models.TextField(blank=True)
	added_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	source = models.CharField(blank=True)
	nsfw = models.BooleanField(default=False, verbose_name="NSFW")
#	related = models.JSONField()

	def file_type(self):
		extension = os.path.splitext(self.file.name)[1].lower()
		if extension in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".mp4", ".mkv", ".avi", ".mov", ".webm"):
			return "visual"
		elif extension in (".mp3", ".wav", ".ogg", ".m4a"):
			return "audio"
		else:
			return "other"

	def get_absolute_url(self):
		return reverse("file_view", kwargs={"pk": self.pk})

	def __str__(self):
		return self.file.name
