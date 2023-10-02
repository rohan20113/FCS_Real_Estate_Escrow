from django.contrib import admin
from .models import AppUser
from .models import Property
# Register your models here.

admin.site.register(AppUser)
admin.site.register(Property)