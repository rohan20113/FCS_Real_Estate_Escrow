from django.db import models
from django.core.validators import MaxValueValidator

# Create your models here.
class AppUser(models.Model):
    first_name = models.CharField(max_length=30, null= False, blank=False, default = None)
    second_name = models.CharField(max_length=30, default= None)
    username = models.CharField(max_length=30, null= False, blank=False, default = None)
    password = models.CharField(max_length=256, null= False, blank=False, default = None)
    email = models.CharField(max_length=30, null= False, blank=False, default = None)
    contact = models.CharField(max_length=30, null= False, blank=False, default = None)
    public_key = models.CharField(max_length=300, null = True, blank = True, default = None)
    balance = models.DecimalField(decimal_places=0, max_digits=15, null = True, blank = True, default= 0)
    dv = models.BooleanField(null = False, blank = False, default= False)

    def __str__(self):
        return f"{self.id} {self.first_name} {self.second_name} {self.username} {self.password} {self.email} {self.contact} {self.balance} {self.public_key}"

# appname_modelName
class Property(models.Model):
    owner = models.CharField(max_length=30,  null= False, blank=False, default = None)
    address_line_1 = models.CharField(max_length=30,  null= False, blank=False, default = None)
    address_line_2 = models.CharField(max_length=30,  null= False, blank=True, default = '')
    state = models.CharField(max_length=30,  null= False, blank=False, default = None)
    city = models.CharField(max_length=30,  null= False, blank=False, default = None)
    pincode = models.CharField(max_length=6,  null= False, blank=False, default = None)
    type = models.CharField(max_length=4,  null= False, blank=False, default = None)
    duration = models.DecimalField(decimal_places=0, max_digits=3, validators=[MaxValueValidator(limit_value=240)], null = True, blank = True, default = None)
    # YYYY-MM-DD
    # starting_date = models.DateField(null = True, blank = True, default= None)
    # ending_date = models.DateField(null = True, blank = True, default= None)
    price = models.DecimalField(decimal_places=0, max_digits=10, null = True, blank = True, default= 0)
    facilities = models.CharField(max_length=20,  null= False, blank=False, default = None)

    def __str__(self):
        return f"{self.owner} {self.address_line_1} {self.address_line_2} {self.state} {self.city} {self.pincode} {self.type} {self.duration} Rs{self.price} {self.facilities}" 


class Property_Transfer_Contract(models.Model):
    id = models.AutoField(primary_key=True)
    application_id = models.DecimalField(decimal_places=0, max_digits=10, null = False, blank = False, default = None)
    property_id = models.DecimalField(decimal_places=0, max_digits=10, null = False, blank = False, default = None)
    property_address_line_1 = models.CharField(max_length=30,  null= False, blank=False, default = None)
    property_address_line_2 = models.CharField(max_length=30,  null= False, blank=True, default = '')
    property_state = models.CharField(max_length=30,  null= False, blank=False, default = None)
    property_city = models.CharField(max_length=30,  null= False, blank=False, default = None)
    property_pincode = models.CharField(max_length=6,  null= False, blank=False, default = None) 
    buyer = models.CharField(max_length=30,  null= False, blank=False, default = None)
    first_name_buyer = models.CharField(max_length=30, null= False, blank=False, default = None)
    second_name_buyer = models.CharField(max_length=30, default= None)
    seller = models.CharField(max_length=30,  null= False, blank=False, default = None)
    first_name_seller = models.CharField(max_length=30, null= False, blank=False, default = None)
    second_name_seller = models.CharField(max_length=30, default= None)
    price = models.DecimalField(decimal_places=0, max_digits= 10, null = False, blank = False, default = None)
    date_of_agreement = models.DateField(null = False, blank = False, default= None)
    token = models.CharField(max_length=2000, null= False, blank=False, default = None)

    def __str__(self):
        return f"{self.application_id} {self.property_id} {self.buyer} {self.seller} {self.price} {self.date_of_agreement} "

class RentalsContract(models.Model):
    contract_id = models.DecimalField(decimal_places=0, max_digits=10, null = False, blank = False, default = False)
    party_user_name = models.CharField(max_length=30,  null= False, blank=False, default = False)
    first_name = models.CharField(max_length=30, null= False, blank=False, default = None)
    second_name = models.CharField(max_length=30, default= None)
    party_type = models.CharField(max_length=1, null = False, blank = False, default = False)
    # 0-> owner & 1-> other_party
    property_id = models.DecimalField(decimal_places=0, max_digits=10, null = False, blank = False, default = False) 
    duration = models.DecimalField(decimal_places=0, max_digits=3, null = False, blank = False, default = False)
    price = models.DecimalField(decimal_places=0, max_digits=7, null = False, blank = False, default = False)
    date_of_contract = models.DateField(null = False, blank = False, default= False)

    def __str__(self):
        return f"{self.contract_id} {self.property_id} {self.party_user_name} {self.party_type} {self.duration} {self.price} {self.date_of_contract}"
    
class PropertyApplications(models.Model):
    property_id = models.DecimalField(decimal_places=0, max_digits=10, null = False, blank = False, default = False) 
    property_owner = models.CharField(max_length=30,  null= False, blank=False, default = False)
    interested_user = models.CharField(max_length=30,  null= False, blank=False, default = False)
    status = models.CharField(max_length=15, null = False, blank = False, default = "PENDING")