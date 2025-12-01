from django.contrib import admin
from import_export import resources
from .models import *
from .forms import *

admin.site.register(Version)
admin.site.register(CurrentVersion)
admin.site.register(Method)
admin.site.register(Master)
admin.site.register(Lookup)
