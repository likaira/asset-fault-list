from django.contrib import admin

from . models import PVSystem, ErrorLog

# Register your models here.
admin.site.register(PVSystem)
admin.site.register(ErrorLog)