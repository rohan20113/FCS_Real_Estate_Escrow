from django.contrib import admin
from .models import AppUser, Property, Property_Transfer_Contract, RentalsContract, PropertyApplications, OTP, ReportedBuyer, ReportedListing
# from .models import Property
# Register your models here.

admin.site.register(AppUser)
admin.site.register(Property)
admin.site.register(PropertyApplications)
admin.site.register(Property_Transfer_Contract)
admin.site.register(RentalsContract)
admin.site.register(OTP)
admin.site.register(ReportedBuyer)
admin.site.register(ReportedListing)