import os
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class File(models.Model):
	
	#User editable
	file = models.FileField() #move to temp folder if model is deleted (acts as recycle bin, isnt fully deleted until admin confirms)
	description = models.TextField(blank=True)
	source = models.CharField(blank=True)
	nsfw = models.BooleanField(default=False, verbose_name="NSFW")
#	related = models.JSONField()

	#Automatic
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	added_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	file_size_bytes = models.PositiveIntegerField()
	file_video_length = models.DurationField()


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
