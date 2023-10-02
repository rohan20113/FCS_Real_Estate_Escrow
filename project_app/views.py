from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import AppUser, Property
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.views.decorators.csrf import csrf_exempt
import hashlib
from django.core import serializers
# from django.shortcuts import render, redirect

# Create your views here.
# @csrf_exempt
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Calculating the hash
        hash = hashlib.sha256()
        hash.update(password.encode())
        password = hash.hexdigest()
        application_users = AppUser.objects.all()
        user_flag = False
        pass_flag = False
        for users in application_users:
            # print(users.username, users.password)
            if (username == users.username):
                user_flag = True
                # print("STATUS:", verified)
                if(password == users.password):
                    # print("STATUS:", verified)
                    pass_flag = True
        if user_flag and pass_flag:
            request.session['username'] = username
            if username in ['chirag20047']:
                return redirect('admin_dashboard_page')
            else:
                return redirect('dashboard_page')
        else:
            if user_flag == False:
                messages.info(request, 'Invalid Username')
                return redirect('login_page')
                # return render(request, 'login.html')
            elif pass_flag == False:
                messages.info(request, 'Invalid Password')
                # return render(request, 'login.html')
                return redirect('login_page')
    else:
        return render(request, 'login.html')
    
# @csrf_exempt
def register_user(request):
    if request.method == 'POST':
        input_first_name = request.POST['firstname']
        input_last_name = request.POST['lastname']
        input_username = request.POST['username']
        input_email = request.POST['email']
        input_contact = request.POST['contact']
        input_password = request.POST['password']
        input_confirm_password = request.POST['confirm_password']
        if input_password==input_confirm_password:
            # Passwords matched
            if AppUser.objects.filter(username=input_username).exists():
                messages.info(request, 'Username already EXISTS.')
                return redirect(register_user)
            elif AppUser.objects.filter(email=input_email).exists():
                messages.info(request, 'Email already EXISTS.')
                return redirect(register_user)
            else:
                # print("ROHAN AAGAYA YAHA")
                hash = hashlib.sha256()
                hash.update(input_password.encode())
                input_password = hash.hexdigest()
                user = AppUser.objects.create(username=input_username, password=input_password, 
                                        email=input_email, first_name=input_first_name, second_name=input_last_name, contact=input_contact)
                user.save()
                return redirect('login_page')
        # Passwords unmatched.
        else:
            messages.info(request, 'Passwords UNMATCHED')
            return redirect(register_user)
            
    else:
        return render(request, 'signup.html')
    
def dashboard_admin(request):
    if request.method == "POST":
        pass
    else:
        username = request.session.get('username')
        # print(username)
        current_user = []
        users = AppUser.objects.all()
        for x in users:
            if x.username == username:
                current_user = x
                break
        return render(request, 'admin_dashboard.html', {'user': current_user}) 

def dashboard_user(request):
    if request.method == "POST":
        # username = request.session.get('username')
        # request.session['username'] = username
        pass
    else:
        username = request.session.get('username')
        request.session['username'] = username
        # print(username)
        current_user = []
        users = AppUser.objects.all()
        for x in users:
            if x.username == username:
                current_user = x
                break
        return render(request, 'dashboard.html', {'user': current_user})
        
def dashboard_user_list(request):
    users = AppUser.objects.all()
    return render(request, 'user_list.html', {'users':users})

def add_property(request):
    username = request.session.get('username')
    # print(username)
    if request.method == "POST":
        input_addr_l1 = request.POST['address-line-1']
        input_addr_l2 = request.POST['address-line-2']
        input_city = request.POST['city']
        input_pin_code = request.POST['pin-code']
        input_state = request.POST['state']
        input_contract_type = request.POST['contract-type']
        input_facilities = request.POST['facilities']
        input_contract_type = request.POST['contract-type']
        input_price = request.POST['price']
        input_availability_from = request.POST['availability-from']
        input_availability_till = request.POST['availability-till']
        # print(type(input_availability_till))
        # print((input_availability_till), (input_availability_till).reverse())
        if(input_contract_type == 'RENT' and (input_availability_from == '' or input_availability_till == '')):
            messages.info(request, 'PLEASE FILL AVAILABILITY DATES')
            return redirect('add_property_page')
        # print(input_availability_from, input_availability_till, input_contract_type, input_state, input_facilities)

        # Date fields
        if(input_contract_type == 'RENT'):
            # date = input_availability_till.split('-')
            # input_availability_till = date[2] + '-' +  date[1] + '-' + date[0]
            # date = input_availability_from.split('-')
            # input_availability_from = date[2] + '-' + date[1] + '-' + date[0]
            # print(input_availability_from, input_availability_till)
            property_to_be_added = Property.objects.create(owner = username, address_line_1 = input_addr_l1, address_line_2 = input_addr_l2, state = input_state,
            city = input_city, pincode = input_pin_code, type = input_contract_type, starting_date = input_availability_from, ending_date = input_availability_till,
            price = input_price, facilities = input_facilities)
            property_to_be_added.save()
            return redirect('dashboard_page')   
        # print(input_availability_from, input_availability_till)
        # Creating the object
        else:
            property_to_be_added = Property.objects.create(owner = username, address_line_1 = input_addr_l1, address_line_2 = input_addr_l2, state = input_state,
            city = input_city, pincode = input_pin_code, type = input_contract_type, price = input_price, facilities = input_facilities)
            property_to_be_added.save()
            return redirect('dashboard_page')   
    else:
        return render(request, 'add_property.html')
    
def my_properties(request):
    username = request.session.get('username')
    if(request.method == 'POST'):
        pass
    else:
        my_properties_list = []
        properties = Property.objects.all()
        for p in properties:
            if username == p.owner:
                my_properties_list.append(p)
        # print("NUMBER_OF_PROPERTIES:",len(my_properties_list))
        return render(request, 'my_properties.html', {'properties':my_properties_list})
    
def search_properties(request):
    username = request.session.get('username')
    # print(request)
    if(request.method == 'POST'):
        pass
    else:
        my_properties_list = []
        properties = list(Property.objects.values())
        # print(properties)
        for i in range(len(properties)):
            if(properties[i]['owner'] !=username):
                my_properties_list.append(properties[i])
        # print("LENGTH:", len(my_properties_list))
        # print("SELECTED LIST:\n", (my_properties_list))
        return render(request, 'search_properties.html', {'properties':my_properties_list})

