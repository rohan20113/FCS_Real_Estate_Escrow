from django.db import models

# Create your models here.
class AppUser(models.Model):
    first_name = models.CharField(max_length=30, null= False, blank=False, default = None)
    second_name = models.CharField(max_length=30, default= None)
    username = models.CharField(max_length=30, null= False, blank=False, default = None)
    password = models.CharField(max_length=30, null= False, blank=False, default = None)
    email = models.CharField(max_length=30, null= False, blank=False, default = None)
    contact = models.CharField(max_length=30, null= False, blank=False, default = None)

    def __str__(self):
        return f"{self.first_name} {self.second_name} {self.username} {self.password} {self.email} {self.contact}"

# appname_modelName
class Property(models.Model):
    owner = models.CharField(max_length=30,  null= False, blank=False, default = None)
    address_line_1 = models.CharField(max_length=30,  null= False, blank=False, default = None)
    address_line_2 = models.CharField(max_length=30,  null= False, blank=True, default = '')
    state = models.CharField(max_length=30,  null= False, blank=False, default = None)
    city = models.CharField(max_length=30,  null= False, blank=False, default = None)
    pincode = models.CharField(max_length=6,  null= False, blank=False, default = None)
    type = models.CharField(max_length=4,  null= False, blank=False, default = None)
    # YYYY-MM-DD
    starting_date = models.DateField(null = True, blank = True, default= None)
    ending_date = models.DateField(null = True, blank = True, default= None)
    price = models.DecimalField(decimal_places=0, max_digits=12, null = True, blank = True, default= 0)
    facilities = models.CharField(max_length=20,  null= False, blank=False, default = None)

    def __str__(self):
        return f"{self.owner} {self.address_line_1} {self.address_line_2} {self.state} {self.city} {self.pincode} {self.type} {self.starting_date} {self.ending_date} Rs{self.price} {self.facilities}" 