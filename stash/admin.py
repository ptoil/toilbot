from django.contrib import admin

from .models import File, Collection, Profile

# Register your models here.
admin.site.register(File)
admin.site.register(Collection)
admin.site.register(Profile)