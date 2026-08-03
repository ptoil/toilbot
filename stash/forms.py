from django import forms
from easy_select2.widgets import Select2Multiple
from .models import File, Collection

class CollectionsModelMultipleChoiceField(forms.ModelMultipleChoiceField):
	def clean(self, value):
		values = value or []
		PKs = []
		for raw in values:
			if raw.isdigit() and self.queryset.filter(pk=raw).exists():
				PKs.append(raw)
			else:
				new_collection, _ = Collection.objects.get_or_create(name=raw)
				PKs.append(new_collection.pk)
		return super().clean(PKs)


class FileForm(forms.ModelForm):
	collections = CollectionsModelMultipleChoiceField(
		queryset=Collection.objects.all(),
		widget=Select2Multiple(select2attrs={"tags": "true"})
	)

	class Meta:
		model = File
		fields = ["file", "description", "source", "nsfw", "collections"]