from django.db import models

# Create your models here.
class File(models.Model):
	
	file = models.FileField(upload_to="media/")
	description = models.TextField(blank=True)
#	added_by = models.ForeignKey()
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	source = models.CharField(blank=True)
	nsfw = models.BooleanField()
#	related = models.JSONField()

	def get_context_data(self, **kwargs):
		return super().get_context_data(**kwargs)

	def __str__(self):
		return self.file.name