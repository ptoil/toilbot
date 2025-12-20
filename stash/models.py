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

	def get_absolute_url(self):
		return reverse("file_view", kwargs={"pk": self.pk})

	def __str__(self):
		return self.file.name
