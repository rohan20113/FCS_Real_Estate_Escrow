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