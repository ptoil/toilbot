from django import forms
from easy_select2.widgets import Select2Multiple
from .models import File

class FileForm(forms.ModelForm):
	class Meta:
		model = File
		fields = ["file", "description", "source", "nsfw", "collections"]
		widgets = {
			"collections": Select2Multiple
		}
