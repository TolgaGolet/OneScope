from django.contrib import admin
from .models import UserSource
from .models import Source

admin.site.register(Source)
admin.site.register(UserSource)
