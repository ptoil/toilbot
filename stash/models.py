from django.db import models
from django.urls import reverse

# Create your models here.
class File(models.Model):
	
	file = models.FileField(upload_to="media/", blank=True)
	description = models.TextField(blank=True)
#	added_by = models.ForeignKey()
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	source = models.CharField(blank=True)
	nsfw = models.BooleanField(default=False)
#	related = models.JSONField()

	def get_absolute_url(self):
		return reverse("file_view", kwargs={"pk": self.pk})

	def __str__(self):
		return self.file.name