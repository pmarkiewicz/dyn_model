from django.contrib import admin
from . import models

admin.site.register(models.DynamicTable)
admin.site.register(models.DynamicField)
