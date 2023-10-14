from django.contrib import admin
from .models import AppUser, Property, Property_Transfer_Contract, RentalsContract, PropertyApplications
# from .models import Property
# Register your models here.

admin.site.register(AppUser)
admin.site.register(Property)
admin.site.register(PropertyApplications)
admin.site.register(Property_Transfer_Contract)
admin.site.register(RentalsContract)