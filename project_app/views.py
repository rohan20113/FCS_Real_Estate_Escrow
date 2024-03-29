from django.shortcuts import render, redirect, reverse
from .models import AppUser, Property, PropertyApplications, Property_Transfer_Contract, RentalsContract, OTP, ReportedBuyer, ReportedListing
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import JsonResponse
import hashlib, json, requests, random
from django.shortcuts import get_object_or_404
from datetime import date, datetime, timedelta 
import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from django.core.mail import send_mail
from django.utils import timezone


def valid_email(str):
    allowed_characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*.'
    for i in str:
        if i not in allowed_characters:
            return False
    
    if '@' not in str or '.' not in str:
        return False
    return True

# Validate an output
def valid_text(str):
    allowed_characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
    for i in str:
        if i not in allowed_characters:
            return False
    lowered_string = str.lower()
    restricted_keywords = ['select', 'insert', 'update', 'delete', 'union', 'onload', 'onmouseover', 'script']
    for i in restricted_keywords:
        if i in lowered_string:
            return False
    return True

# Create your views here.
# @csrf_exempt
def login_user(request):
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')
    
    if request.session.get('username') is not None:
        if request.session.get('username') == 'chirag20047':
            return redirect('admin_dashboard_page')
        return redirect('dashboard_page')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Validating the input. 
        if (valid_text(username) ==False or valid_text(password) == False):
            messages.error(request, "Please enter fields in valid format.")
            return redirect('login_page')
        # Calculating the hash
        hash = hashlib.sha256()
        hash.update(password.encode())
        password = hash.hexdigest()
        application_users = AppUser.objects.all()
        user_flag = False
        pass_flag = False
        user_id = None
        dv_flag = False
        for users in application_users:
            # print(users.username, users.password)
            if (username == users.username):
                user_flag = True
                # print("STATUS:", verified)
                if(password == users.password):
                    # print("STATUS:", verified)
                    pass_flag = True
                    user_id = users.id
                    dv_flag = users.dv
        if user_flag and pass_flag:
            request.session['username'] = username
            if username in ['chirag20047']:
                return redirect('admin_dashboard_page')
            else:
                if(dv_flag is False):
                    # messages.info(request, "Document Verification Pending")
                    return redirect('user_document_verification_page', id=user_id)
                else:
                    messages.success(request, 'Successfully Logged in.')
                    return redirect('dashboard_page')
        else:
            if user_flag == False:
                messages.error(request, 'Invalid Username')
                return redirect('login_page')
                # return render(request, 'login.html')
            elif pass_flag == False:
                messages.error(request, 'Invalid Password')
                # return render(request, 'login.html')
                return redirect('login_page')
    else:
        return render(request, 'login.html')

def valid_num(contact):
    digits = "0123456789"
    for i in contact:
        if i not in digits:
            return False
    return True

# @csrf_exempt
def register_user(request):
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')
    if request.method == 'POST':
        input_first_name = request.POST['firstname']
        input_last_name = request.POST['lastname']
        input_username = request.POST['username']
        # input_email = request.POST['email']
        input_contact = request.POST['contact']
        input_password = request.POST['password']
        input_confirm_password = request.POST['confirm_password']
        if input_password==input_confirm_password:
            # Input Validation: 
            if(valid_text(input_first_name) == False or valid_text(input_last_name)==False or valid_text(input_username) == False or valid_num(input_contact) == False or valid_text(input_password) == False):
                messages.error(request, 'Please follow valid input format.')
                return redirect('signup_page')
            if(len(input_first_name) == 0 or len(input_username) == 0 or len(input_first_name) > 30 or len(input_last_name) > 30 or len(input_username) > 30  or len(input_contact)!= 10 ):
                messages.error(request, 'Please adhere to the characters length for input fields.')
                return redirect('signup_page')
            if(len(input_password) <= 5 or len(input_password) > 30):
                messages.info(request, 'Passwords should be in the range of [6,30] characters (both inclusive).')
                return redirect('signup_page')
            # Passwords matched
            if AppUser.objects.filter(username=input_username).exists():
                messages.error(request, 'Username already EXISTS.')
                return redirect(register_user)
            # elif AppUser.objects.filter(email=input_email).exists():
            #     messages.info(request, 'Email already EXISTS.')
            #     return redirect(register_user)
            else:
                hash = hashlib.sha256()
                hash.update(input_password.encode())
                input_password = hash.hexdigest()
                try:
                    user = AppUser.objects.create(username=input_username, password=input_password, 
                                            email=request.session.get('email_kyc'), first_name=input_first_name, second_name=input_last_name, contact=input_contact, balance = 10000000, public_key = None, dv = False)
                    user.save()
                    # Obtaining the user's id.
                    user_id = user.id
                    # print("ID:", user_id)
                    return redirect('user_mail_verification_page', id = user_id)
                except:
                    messages.error(request, 'Unexpected error because of invalid format.')
                    return redirect('signup_page')
        # Passwords unmatched.
        else:
            messages.error(request, 'Passwords UNMATCHED')
            return redirect(register_user)
            
    else:
        return render(request, 'signup.html')

def user_mail_verification(request, id):
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')

    current_user = AppUser.objects.get(id = id)
    if(current_user.dv):
        if request.session.get('username') is not None:
            return redirect('dashboard_page')
        else:
            return redirect('login_page')
        
    # if (valid_num(id) == False):
    #     messages.error(request, "Invalid Request")
    #     return redirect('login_page')

    if (request.session.get('otp_verification') == id):
        return redirect('user_document_verification_page', id = id)
    
    if request.method == 'POST':
        otp = request.POST['otp']
        # Input Validation:
        if(len(otp) != 6 or valid_num(otp) == False):
            messages.error(request, 'Invalid format (length/characters) of OTP.')
            return redirect('user_mail_verification_page', id= id)
        try:
            otp_object = OTP.objects.get(user = AppUser.objects.get(id = id).username)
            if otp_object.valid == False:
                messages.error(request, 'OTP already used before in some old transaction.')
                return redirect('user_mail_verification_page', id =id)
            if otp_object.expiry_time < timezone.now():
                messages.error(request, 'OTP expired. Please check your mail again.')
                return redirect('user_mail_verification_page', id =id)
            if otp != otp_object.otp:
                messages.error(request, 'OTP did not match.')
                return redirect('user_mail_verification_page', id =id)
            request.session['otp_verification'] = id
            # OTP matched. 
            messages.success(request, 'OTP Verification Successful.')
            return redirect('user_document_verification_page', id= id)
        except:
            messages.error(request, 'Invalid Request. Please Try Again Later.')
            return redirect('user_mail_verification_page', id = id)
    elif request.method == 'GET':
        try:
            generateOtpEmail(AppUser.objects.get(id = id).username)
            messages.info(request, f'OTP has been sent to {current_user.email}.')
            return render(request, 'user_mail_verification.html')
        except:
            messages.info(request, 'Unexpected Error')
            return redirect('login_page')

def user_document_verification(request, id):
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')
    
    try:
        current_user = AppUser.objects.get(id = id)
        if(current_user.email != request.session.get('email_kyc')):
            return redirect('logout_page')
        
        if request.session.get('otp_verification') != id:
            request.session['otp_verification'] = None
            messages.error(request, 'User Verification needs to be performed first.')
            return redirect('user_mail_verification_page', id = id)

        # Check if already document verified: 
        if(current_user.dv):
            if request.session.get('username') is not None:
                return redirect('dashboard_page')
            else:
                return redirect('login_page')
        
        if request.method == 'POST':
            data = json.loads(request.body)
            public_key_pem = data.get('publicKey', None)
            originalFileContents = data.get('originalFile', None)
            signature = data.get('signedFile', None)
            # public_key_pem = request.POST['publicKey']
            # originalFileContents = request.POST['originalFile']
            # signature = request.POST['signedFile']
            # hash = request.POST['hashed']
            # print(id)
            # verification_result = 'FAIL'
            # print(originalFileContents) #--> Verified, same content.
            # print(signature)  #--> Verified, same content.
            try:
                # print('ENCODED HASH:',hash)
                # hash = base64.b64decode(hash)
                # print('\nDECODED HASH:',hash)
                public_key_pem = base64.b64decode(public_key_pem)
                # print(originalFileContents)
                originalFileContents = base64.b64decode(originalFileContents)
                # print("\nDecoded",originalFileContents)
                # print(signature)    
                signature = base64.b64decode(signature)
                # print(signature)    
                public_key = RSA.import_key(public_key_pem)
                # Create a hash of the original file contents
                h = SHA256.new(originalFileContents)
                # calculated_hash = h.hexdigest()
                # print('Calculated\n', calculated_hash, '\nReceived\n', hash)
                # print(type(calculated_hash), type(hash))
                # print(calculated_hash == str((hash).decode('utf-8')))
                verifier = pkcs1_15.new(public_key)
                if verifier.verify(h, signature) is None:
                    # verification_result = 'PASS'
                    # Update the user's dv boolean_field & store the public_key_pem.
                    current_user = AppUser.objects.get(id = id)
                    current_user.dv = True
                    current_user.public_key = public_key_pem.decode('utf-8')
                    current_user.save()
                messages.success(request, 'Document Verification Successful')
                response_data = {
                    'success': True,
                    'url': '/login'
                }
                request.session['otp_verification'] = None
                return JsonResponse(response_data)
                # messages.info(request, 'Document Verification Failed!\n Please Try Again.')
                # response_data = {
                #     'success': False,
                #     'url': f'/user_document_verification/{id}'
                # }
                # return redirect('login_page')
                # return render(request, 'user_document_verification_result.html', {'public_key_pem':public_key_pem, 'public_key':public_key, 'originalFile':originalFileContents,
                #                                                                 'signature': signature, 'result': verification_result})
        
            except Exception as e:
                # Handle any exceptions that may occur during verification
                # print("Error during verification:", str(e))
                # Print specific details about the data and error
                messages.error(request, 'Document Verification Failed!\n Please Try Again.')
                response_data = {
                    'success': False,
                    'url': f'/user_document_verification/{id}'
                }
                return JsonResponse(response_data)
                # return render(request, 'user_document_verification.html', {'id': id})

        elif request.method == 'GET':
            messages.info(request, 'NOTE: Leaving the verification process in between may hamper user experience.')
            return render(request, 'user_document_verification.html', {'id': id})
    except:
        messages.error(request, 'Unexpected Error')
        return redirect('login_page')

def ekyc(request):
    # status -> success, error
    # message -> Login successful, Invalid password or Invalid email
    if request.method == 'POST':
        email_input = request.POST['email'].lower()
        password_input = request.POST['password']
        if(valid_email(email_input) == False  or valid_text(password_input) == False):
            # print(valid_email(email_input), valid_text(password_input))
            messages.error(request, 'Please follow proper input format.')
            return redirect('ekyc_page')
        # print(type(email_input))
        dictionary = {
            "email": email_input,
            "password":password_input
        }
        if email_input not in ["chirag20047@iiitd.ac.in",
                                "rohan20113@iiitd.ac.in",
                                "pathik20095@iiitd.ac.in"
                                ]:
            messages.info(request, "UNDER MAINTAINANCE, ONLY DEVELOPERS ARE ALLOWED")
            return redirect('ekyc_page')
        # print(email_input, password_input)
        # Will call the API here and set the flag accordingly.
        try:
            api_response = requests.post('https://192.168.3.39:5000/kyc', json = dictionary, verify= False)
            # print(api_response)
            if api_response.status_code == 200:
                response_data = api_response.json()
                # return JsonResponse(response_data)
                if(response_data.get('status') == 'success'):
                    messages.success(request, 'eKYC successful')
                    request.session['email_kyc'] = email_input
                    # request.session['password_kyc'] = password_input  
                    return redirect('login_page')
                elif response_data.get('status') == 'error':
                    messages.error(request, response_data.get('message'))
                    return redirect('/')
            else:
                messages.error(request, 'Error Code: {api_response.stat  us_code}')
                return redirect('/')
        except requests.exceptions.RequestException as e:
            messages.error(request, 'PLEASE TRY AGAIN LATER')
            return redirect('/')
    else:
        # GET REQUEST
        if(request.session.get('email_kyc') is not None):
            if(request.session.get('username') is None):
                return redirect('login_page')
            else:
                if(request.session.get('username') in ['chirag20047']):
                    return redirect('admin_dashboard_page')
                return redirect('dashboard_page')
        return render(request, 'ekyc.html')

def dashboard_admin(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None or username not in ['chirag20047']):
        return redirect('logout_page')
    if request.method == "POST":
        username = request.session.get('username')
        # print(username)
        if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
        if(username is None):
            return redirect('login_page')    
    else:
        username = request.session.get('username')
        if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
        if(username is None):
            return redirect('login_page') 
        current_user = []
        try:
            users = AppUser.objects.all()
            for x in users:
                if x.username == username:
                    current_user = x
                    break
            return render(request, 'admin_dashboard.html', {'user': current_user}) 
        except:
            messages.info(request, 'Unexpected Error(da)')
            return redirect('logout_page')

# @login_required
def dashboard_user(request):
    if request.method == "POST":
        username = request.session.get('username')
        if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
        if(username is None):
            return redirect('login_page')
        # if(username is None):
        # return redirect('/')
        pass
    else:
        try:
            username = request.session.get('username')
            if(request.session.get('email_kyc') is None):
                return redirect('logout_page')
            if(username is None):
                return redirect('login_page')
            # print(username)
            current_user = []
            users = AppUser.objects.all()
            for x in users:
                if x.username == username:
                    current_user = x
                    break
            return render(request, 'dashboard.html', {'user': current_user})
        
        except:
                messages.info(request, 'Unexpected Error(du)')
                return redirect('logout_page')
        
def dashboard_user_list(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('email_kyc').lower() != 'chirag20047@iiitd.ac.in'):
            return redirect('logout_page')
    if(username is None or username not in ['chirag20047']):
        return redirect('logout_page')
    users = list(AppUser.objects.values())
    user_list = []
    for i in range(len(users)):
        if(users[i]['username'] != request.session.get('username')):
            # print(users[i])
            user_list.append(users[i])
    return render(request, 'user_list.html', {'users':user_list})

def valid_address(str):
    allowed_characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*.,- '
    for i in str:
        if i not in allowed_characters:
            return False
    lowered_string = str.lower()
    restricted_keywords = ['select', 'insert', 'update', 'delete', 'union', 'onload', 'onmouseover', 'script']
    for i in restricted_keywords:
        if i in lowered_string:
            return False
    return True

def add_property(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    # print(username)
    if request.method == "POST":
        if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
        if(username is None):
            return redirect('login_page')
        #try:
        input_addr_l1 = request.POST['address-line-1']
        input_addr_l2 = request.POST['address-line-2']
        input_city = request.POST['city']
        input_pin_code = request.POST['pin-code']
        input_state = request.POST['state']
        input_contract_type = request.POST['contract-type']
        input_facilities = request.POST['facilities']
        # input_contract_type = request.POST['contract-type']
        input_price = request.POST['price']
        input_duration = None
        if input_contract_type == 'RENT':
            input_duration = request.POST['duration']
            if valid_num(input_duration) == False or len(input_duration) == 0 or len(input_duration) > 3:
                messages.error(request, 'Invalid duration field format.')
                return redirect('add_property_page')
            if int(input_duration) > 240 or int(input_duration) < 0:
                messages.error(request, 'Invalid duration range for RENTAL Property.')
                return redirect('add_property_page')
        # print(type(input_price))
        if(valid_address(input_addr_l1) == False or valid_address(input_addr_l2) == False or valid_address(input_city) == False or valid_address(input_state) == False or valid_text(input_contract_type) == False or  valid_num(input_price) == False):
            # print(valid_address(input_addr_l1) == False ,valid_address(input_addr_l2) == False ,valid_address(input_city) == False ,valid_address(input_state) == False ,valid_text(input_contract_type) == False , valid_num(input_price) == False)
            messages.error(request, 'Invalid input format.')
            return redirect('add_property_page') 

        if (len(input_addr_l1) == 0 or len(input_city) ==0 or len(input_contract_type) == 0 or len(input_facilities) == 0 or len(input_price) == 0 or len(input_state) == 0 or len(input_pin_code) ==0):
            messages.error(request, 'Emtpy Fields detected.')
            return redirect('add_property_page')
        
        if (len(input_addr_l1) > 30 or len(input_addr_l2) > 30 or len(input_city) > 30):
            messages.error(request, 'Emtpy Fields detected.')
            return redirect('add_property_page')

        if(len(input_pin_code) !=6 or valid_num(input_pin_code) == False):
            messages.error(request, 'Invalid Pin Code')
            return redirect('add_property_page')
        
        if(input_facilities not in ['Furnished', 'Unfurnished', 'Semi-Furnished']):
            messages.error(request, 'Invalid facilities input.')
            return redirect('add_property_page')
        
        if(input_contract_type not in ['RENT', 'SELL']):
            messages.error(request, 'Invalid Contract Type.')
            return redirect('add_property_page')
        
        if(input_state not in ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh","Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha","Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal","Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Lakshadweep", "Puducherry" ]):
            messages.error(request, 'Invalid State.')
            return redirect('add_property_page')
        
        # input_availability_from = request.POST['availability-from'] 
        # input_availability_till = request.POST['availability-till']
        # print(type(input_availability_till))
        # print((input_availability_till), (input_availability_till).reverse())
        # print(input_contract_type, input_duration)
        if(input_contract_type == 'RENT' and (input_duration == None or len(input_duration) == 0)):
            messages.error(request, 'PLEASE FILL DURATION OF RENT')
            return redirect('add_property_page')
    
        if(input_contract_type == 'SELL'):
            if (int(input_price) <0 or int(input_price) > 1000000000):
                messages.error(request, 'Invalid range of price (sell type property).')
                return redirect('add_property_page')
        else:
            if (int(input_price) <0 or int(input_price) > 5100000):
                messages.error(request, 'Invalid range of price (rental type property).')
                return redirect('add_property_page')
        # print(input_availability_from, input_availability_till, input_contract_type, input_state, input_facilities)
        try:
        # Date fields
            if(input_contract_type == 'RENT'):
                # date = input_availability_till.split('-')
                # input_availability_till = date[2] + '-' +  date[1] + '-' + date[0]
                # date = input_availability_from.split('-')
                # input_availability_from = date[2] + '-' + date[1] + '-' + date[0]
                # print(input_availability_from, input_availability_till)
                property_to_be_added = Property.objects.create(owner = username, address_line_1 = input_addr_l1, address_line_2 = input_addr_l2, state = input_state,
                city = input_city, pincode = input_pin_code, type = input_contract_type, duration = input_duration,
                price = input_price, facilities = input_facilities)
                property_to_be_added.save()
                messages.success(request, 'Successfully added a property.')
                return redirect('my_properties_page')   
            # print(input_availability_from, input_availability_till)
            # Creating the object
            else:
                property_to_be_added = Property.objects.create(owner = username, address_line_1 = input_addr_l1, address_line_2 = input_addr_l2, state = input_state,
                city = input_city, pincode = input_pin_code, type = input_contract_type, price = input_price, facilities = input_facilities)
                property_to_be_added.save()
                messages.success(request, 'Successfully added a property.')
                return redirect('my_properties_page')   
        except:
            messages.error(request, 'Unexpected Error while adding the property. Please Try Again Later.')
            return redirect('my_properties_page')
        # except:
        #     messages.error(request, 'Unexpected Error')
        #     return redirect('add_property_page')
    else:
        if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
        if(username is None):
            return redirect('login_page')
        return render(request, 'add_property.html')
    
def my_properties(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    if(request.method == 'POST'):
        return redirect('my_properties_page')
    else:
        try:
            my_properties_list = []
            properties = Property.objects.values()
            for i in range(len(properties)):
                if username == properties[i]["owner"] and properties[i]['type'] != 'DELETED':
                    my_properties_list.append(properties[i])
            # print("NUMBER_OF_PROPERTIES:",len(my_properties_list))
            return render(request, 'my_properties.html', {'properties':my_properties_list})
        except:
            messages.error(request, 'Unexpected Error')
            return redirect('dashboard_page')

def search_properties(request):
    request.session['transaction_ekyc'] = None
    if(request.method == 'POST'):
        username = request.session.get('username')
        if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
        if(username is None):
            return redirect('login_page')
        return redirect('search_properties_page')
    else:
        username = request.session.get('username')
        # print(type(username), username)
        if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
        if(username is None):
            return redirect('login_page')
        try:
            my_properties_list = []
            properties = list(Property.objects.values())
            # print(properties)
            for i in range(len(properties)):
                # Exlcuding all properties of type: DELETED, DELISTED, ON_LEASE
                if(properties[i]['owner'] !=username and properties[i]['type'] in ['SELL', 'RENT']):
                    my_properties_list.append(properties[i])
            # print("LENGTH:", len(my_properties_list))
            # print("SELECTED LIST:\n", (my_properties_list))

            # Fetching property_applications data --> NEED TO PASS ONLY THE APPLICATION IDs and nothing else.
            applications_list = []
            applications = list(PropertyApplications.objects.values())
            for i in range(len(applications)):
                if applications[i]['interested_user'] == username and applications[i]['status'] in ['PENDING', 'ACCEPTED']:
                    applications_list.append({'id': applications[i]['id']
                                              , 'status': applications[i]['status']
                                              , 'interested_user': applications[i]['interested_user']
                                              , 'property_id': applications[i]['property_id']
                                            })
            # print(applications)
            user_details = [{'user': username}]
            return render(request, 'search_properties.html', {'properties':my_properties_list, 'applications':applications_list, 'user': user_details})
        except:
            messages.error(request, 'Unexpected Error')
            return redirect('dashboard_page')

def edit_property(request, id = id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    
    try:
        property = Property.objects.get(id=id)
        if(property.owner != username):
            return redirect('logout_page')
        if(property.type == 'DELETED'):
            messages.error(request, "THIS PROPERTY WAS DELETED.")
            return redirect('my_properties_page')
        
        if(property.type == 'BANNED'):
            messages.error(request, "You can not modify a BANNED listing.")
            return redirect('my_properties_page')

        if(property.type == 'ON LEASE'):
            # Calculating the expiration of the lease contract.
            
            messages.error(request, 'You can not modify a property ON LEASE')
            return redirect('my_properties_page')
        
        # Checking if any accepted application exists.
        applications = PropertyApplications.objects.filter(property_id = id, property_owner = username, status = 'ACCEPTED')
        if len(applications) != 0:
            messages.error(request, 'You can not edit a property which is in between transaction phase.')
            return redirect('my_properties_page')

        return render(request, 'edit_property.html', {'property':property})
    except:
        messages.error(request, 'Unexpected Error. Please Try Again Later')
        return redirect('my_properties_page')

def update_property(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):   
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    
    try: 
        property = Property.objects.get(id=id)
        if(property.owner != username):
            return redirect('logout_page')
        if(property.type == 'DELETED'):
            messages.error(request, "THIS PROPERTY WAS DELETED.")
            return redirect('my_properties_page')
        
        if(property.type == 'BANNED'):
            messages.error(request, "You can not modify a BANNED listing.")
            return redirect('my_properties_page')
        
        if(property.type == 'ON LEASE'):
            messages.error(request, 'can not modify a property on lease')
            return redirect('my_properties_page')

        applications = PropertyApplications.objects.filter(property_id = id, property_owner = username, status = 'ACCEPTED')
        if len(applications) != 0:
            messages.error(request, 'You can not edit a property which is in between transaction phase.')
            return redirect('my_properties_page')
        
        if request.method =="POST":
            # property_instance = get_object_or_404(Property, pk = id)
            property_instance = Property.objects.get(id = id)
            # input_addr_l1 = request.POST['address-line-1']
            # input_addr_l2 = request.POST['address-line-2']
            # input_city = request.POST['city']
            # input_pin_code = request.POST['pin-code']
            # input_state = request.POST['state']
            input_contract_type = request.POST['contract-type']
            input_facilities = request.POST['facilities']
            input_contract_type = request.POST['contract-type']
            input_price = request.POST['price']
            input_duration = None

            if(valid_text(input_contract_type) == False or  valid_num(input_price) == False):
                # print(valid_address(input_addr_l1) == False ,valid_address(input_addr_l2) == False ,valid_address(input_city) == False ,valid_address(input_state) == False ,valid_text(input_contract_type) == False , valid_num(input_price) == False)
                messages.error(request, 'Invalid input format.')
                return redirect('add_property_page') 

            if (len(input_contract_type) == 0 or len(input_facilities) == 0 or len(input_price) == 0):
                messages.error(request, 'Emtpy Fields detected.')
                return redirect('add_property_page')
            
            if(input_facilities not in ['Furnished', 'Unfurnished', 'Semi-Furnished']):
                messages.error(request, 'Invalid facilities input.')
                return redirect('add_property_page')
            
            if(input_contract_type not in ['RENT', 'SELL']):
                messages.error(request, 'Invalid Contract Type.')
                return redirect('add_property_page')

            if input_contract_type == 'RENT':
                input_duration = request.POST['duration']
                if valid_num(input_duration) == False or len(input_duration) == 0 or len(input_duration) > 3:
                    messages.error(request, 'Invalid duration field format.')
                    return redirect('add_property_page')
                if int(input_duration) > 240 or int(input_duration) < 0:
                    messages.error(request, 'Invalid duration range for RENTAL Property.')
                    return redirect('add_property_page')
                if (int(input_price) <0 or int(input_price) > 5100000):
                    messages.error(request, 'Invalid range of price (rental type property).')
                    return redirect('add_property_page')
            # input_availability_from = request.POST['availability-from']
            # input_availability_till = request.POST['availability-till']
            if(input_contract_type == 'RENT' and (input_duration is None or input_duration == '')):
                messages.error(request, 'PLEASE FILL RENTAL DURATION')
                return redirect('edit_property_page')
            # print(input_availability_from, input_availability_till, input_contract_type, input_state, input_facilities)

            if(input_contract_type == 'SELL'):
                if (int(input_price) <0 or int(input_price) > 1000000000):
                    messages.error(request, 'Invalid range of price (sell type property).')
                    return redirect('add_property_page')

            # Date fields
            if(input_contract_type == 'RENT'):
                # property_instance.owner = input_owner
                # property_instance.address_line_1 = input_addr_l1
                # property_instance.address_line_2 = input_addr_l2
                # property_instance.state = input_state
                # property_instance.city = input_city
                # property_instance.pincode = input_pin_code
                property_instance.type = input_contract_type
                # property_instance.starting_date = input_availability_from
                # property_instance.ending_date = input_availability_till
                property_instance.duration = input_duration
                property_instance.price = input_price
                property_instance.facilities = input_facilities
                property_instance.save()
                messages.success(request, "Successfully updated the property details.")
                # Rejecting all current applications.
                applications = PropertyApplications.objects.filter(property_id=id, status='PENDING')
                for application in applications:
                    application.status = 'REJECTED'
                    application.save()
                return redirect('my_properties_page')   
            # print(input_availability_from, input_availability_till)
            # Creating the object
            else:
                # property_instance.address_line_1 = input_addr_l1
                # property_instance.address_line_2 = input_addr_l2
                # property_instance.state = input_state
                # property_instance.city = input_city
                # property_instance.pincode = input_pin_code
                property_instance.type = input_contract_type
                property_instance.duration = None
                # property_instance.starting_date = None
                # property_instance.ending_date = None
                # print(property_instance.starting_date)
                # print(property_instance.ending_date)
                property_instance.price = input_price
                property_instance.facilities = input_facilities
                property_instance.save()
                applications = PropertyApplications.objects.filter(property_id=id, status='PENDING')
                for application in applications:
                    application.status = 'REJECTED'
                    application.save()
                messages.success(request, "Successfully updated the property details.")
                return redirect('my_properties_page')  
        else:
            return render(request, 'edit_property.html', {'property':property})
    except:
        messages.error(request, 'Unexpected Error')
        return redirect('my_properties_page')

def delete_property(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    try:
        property = Property.objects.get(id=id)
        if(property.owner != username):
            return redirect('logout_page')
        
        if property.type == 'ON LEASE':
            messages.error(request, 'You can not delete a property ON LEASE.')
            return redirect('my_properties_page')
        
        if property.type == 'BANNED':
            messages.error(request, 'You can not delete a BANNED listing.')
            return redirect('my_properties_page')
        
        applications = PropertyApplications.objects.filter(property_id = id, property_owner = username, status = 'ACCEPTED')
        if len(applications) != 0:
            messages.error(request, 'You can not delete a property which is in between transaction phase.')
            return redirect('my_properties_page')
        
        # property.delete()
        property.type = 'DELETED'
        property.save()
        return redirect('my_properties_page')
    except:
        messages.error(request, 'Unexpected Error')
        return redirect('my_properties_page')

def logout_user(request):
    request.session.flush()
    return redirect('/')

def apply_property_deal(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    try:
        property_selected = Property.objects.get(id=id)
        if property_selected.type not in ['SELL', 'RENT']:
            messages.error(request, 'Invalid application selected. Property NOT FOR SALE/RENT.')
            return redirect('logout_page')
        if property_selected.owner == username:
            messages.error(request, 'You can not apply for a property that you own.')
            return redirect('logout_page')
        property_owner_username = property_selected.owner
        contract_type = property_selected.type

        # Check if no existing row/copy is there:
        applications = list(PropertyApplications.objects.values())
        for i in range(len(applications)):
            # if(applications[i]['property_id'] == id and applications[i]['status'] == 'ACCEPTED'):
            #     if(applications[i]['interested_user'] == username):
            #         messages.success(request, 'Your request has been accepted.\nPlease proceed to pay!')
            #         return redirect('search_properties_page')
            if(applications[i]['property_id'] == id and applications[i]['status'] == 'PENDING'):
                if(applications[i]['interested_user'] == username):
                    messages.info(request, 'Pending Request Already Exists')
                    return redirect('search_properties_page')
            # if(applications[i]['property_id'] == id and applications[i]['status'] == 'ACCEPTED'):
            #     return redirect('display_property_applications_page', id = applications[i]['id'])
                
        # Now, we've to add this pending request for the given property.
        application = PropertyApplications.objects.create(property_id = id, interested_user = username, property_owner = property_owner_username, application_type = contract_type)
        application.save()
        messages.success(request, 'Application Sent Successfully!')
        return redirect('search_properties_page')
    except:
        messages.error(request, 'Unexpected Error')
        return redirect('search_properties_page')

def display_property_applications(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    
    try:
        property = Property.objects.get(id = id)

        if property.owner != username:
            return redirect('logout_page')
        
        if property.type == 'DELETED':
            messages.error(request, 'No applications exist for a deleted property.')
            return redirect('my_properties_page')

        if property.type == 'ON LEASE':
            messages.error(request, 'No applications are allowed for a property ON LEASE.')
            return redirect('my_properties_page')
        
        if(property.type == 'BANNED'):
            messages.error(request, "No transactions allowed for a BANNED listing.")
            return redirect('my_properties_page')

        # accepted_applications = PropertyApplications.objects.filter(property_id=id, status='ACCEPTED')
        accepted_applications = []
        applications = list(PropertyApplications.objects.values())
        for i in range(len(applications)):
            if(applications[i]['property_id'] == id and applications[i]['status'] == 'ACCEPTED'):
                accepted_applications.append(applications[i])
                break
        if(len(accepted_applications) != 0):
            # print("PROPERTY ACCEPTED APPLICATION")
            return render(request, 'accepted_property_application.html', {'applications':accepted_applications})

        # property = Property.objects.get(id = id)
        current_applications = []
        for i in range(len(applications)):
            if(applications[i]['property_id'] == id and applications[i]['status'] == 'PENDING'):
                current_applications.append(applications[i])

        # No pending requests 
        if(len(current_applications) == 0):
            # print('NO APPLICATIONS AVAILABLE')
            messages.info(request, 'No Pending Requests')
            return redirect('my_properties_page')
        
        # If pending requests exist:
        return render(request, 'display_property_applications.html', {'applications':current_applications})
    except:
        messages.error(request, 'Unexpected Error')
        return redirect('my_properties_page')

def reject_property_application(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    try:
        # fetching the object
        current_application = PropertyApplications.objects.get(id = id)
        property = Property.objects.get(id = current_application.property_id)
        if(property.owner != username):
            messages.error(request, 'You are not the owner of the property you are trying to delete.')
            return redirect('logout_page')
        current_property = current_application.property_id
        # Changing the request's status
        current_application.status = 'REJECTED'
        current_application.save()
        messages.success(request, 'Succesfully Updated Request')
        
        # # Find if more pending requests are there.
        applications = list(PropertyApplications.objects.values())
        for i in range(len(applications)):
            if(applications[i]['property_id'] == current_property and applications[i]['status'] == 'PENDING'):
                # return redirect('display_property_applications_page/{current_property}')
                # return redirect(request.path)
                current_url = reverse('display_property_applications_page', args=[current_property])
                # messages.info(request, 'Successfully Updated Request')
                return redirect(current_url)

        # If none, return to my_properties page.
        return redirect('my_properties_page')
    except:
        messages.error(request, 'Unexpected Error')
        return redirect('my_properties_page')

def accept_property_application(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    # property = Property.objects.get(id = id)
    # if property.owner != username:
    #     return redirect('logout_page')
    # fetching the object
    try:
        current_application = PropertyApplications.objects.get(id = id)
        property = Property.objects.get(id = current_application.property_id)
        if(property.owner != username):
            messages.error(request, 'You are not the owner of the property you are trying to process.')
            return redirect('logout_page')
        # current_property = current_application.property_id

        # # Changing the current request's status
        # current_application.status = 'ACCEPTED'
        # current_application.save()
        # messages.info(request, 'Succesfully Updated Request')

        
        # # Rejecting all other pending requests.
        # applications = PropertyApplications.objects.filter(property_id=current_property, status='PENDING')
        # for application in applications:
        #     application.status = 'REJECTED'
        #     application.save()
        
        # Create another contract and pass it to the next api. 

        # messages.info(request, "Application Accepted!\n Please Wait for Payment.")
        if current_application.application_type == 'RENT':
            return redirect('lessor_contract_page', id = id)
        else:
            return redirect('seller_contract_page', id = id)
    except:
        messages.error(request, 'Unexpected Error')
        return redirect('my_properties_page')

def lessor_contract(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    
    try:
        current_application = PropertyApplications.objects.get(id = id)
        property = Property.objects.get(id = current_application.property_id)
        if(property.owner != username):
            messages.error(request, 'You are trying to process contract of a property that you do not own. Please login into respective account first.')
            return redirect('logout_page')
        
        if request.method == 'POST':
            data = json.loads(request.body)
            base64JsonString = data.get('contract_payload', None)
            # jsonString = base64.b64decode(data.get('contract_payload', None)).decode('utf-8')
            base64Signature = data.get('signature', None)
            # signature = base64.b64decode(base64Signature)
            signature = base64.b64decode(data.get('signature', None))
            # print('JSON STRING',jsonString)
            # print('SIGNATURE',signature)

            # Create hash of the same payload and then verify the signatures. 
            # If correct, then accept the application, create a contract and save the data in the table.
            public_key_pem = AppUser.objects.get(username = username).public_key
            public_key = RSA.import_key(public_key_pem)
            # print(public_key)
            # Create a hash of the original file contents
            try:
                h = SHA256.new(base64JsonString.encode('utf-8'))
                verifier = pkcs1_15.new(public_key)
                verifier.verify(h, signature)
            except Exception as e:
                messages.error(request, 'Signature Error!\n Please Try Again.')
                response_data = {
                    'success': False,
                    'url': f'/lessor_contract/{id}'
                }
                return JsonResponse(response_data)
            
            # Approve the application & reject others.
            # fetching the object
            current_application = PropertyApplications.objects.get(id = id)
            current_property_id = current_application.property_id
            property = Property.objects.get(id = current_property_id)
            # Changing the current request's status
            current_application.status = 'ACCEPTED'
            current_application.save()
            
            # Rejecting all other pending requests.
            applications = PropertyApplications.objects.filter(property_id=current_property_id, status='PENDING')
            for application in applications:
                application.status = 'REJECTED'
                application.save()
            
            contract_value = property.duration * property.price
            # lessee_obj = AppUser.objects.get(username = current_application.interested_user)
            lessor_obj = AppUser.objects.get(username = current_application.property_owner)
            # Create a contract object and save the string. 
            signed_token = base64JsonString + "." + base64Signature
            rentals_object = RentalsContract.objects.create(application_id = id, property_id = current_application.property_id,
                                                            property_address_line_1 = property.address_line_1, property_address_line_2 = property.address_line_2,
                                                            property_state = property.state, property_city = property.city, property_pincode = property.pincode,
                                                            username = current_application.property_owner, first_name = lessor_obj.first_name, second_name = lessor_obj.second_name, 
                                                            party_type='lessor' ,date_of_agreement = timezone.now().date(), token = signed_token, duration = property.duration,
                                                            rent_per_month = property.price, total_rent = contract_value)
            rentals_object.save()
            # print(rentals_object)
            messages.success(request, 'Successfully approved the application')
            response_data = {
                'success': True,
                'url': '/my_properties/'
            }
            return JsonResponse(response_data)
            
        else:
            # Fetch the current application object.
            current_application = PropertyApplications.objects.get(id = id)
            property = Property.objects.get(id = current_application.property_id)

            property_address = property.address_line_1 + " " +  property.address_line_2
            property_state = property.state
            property_city = property.city
            property_pincode = property.pincode
            contract_value = property.price * property.duration
            date_of_agreement = timezone.now().date()

            # buyer = AppUser.objects.get(username = current_application.interested_user)
            # buyer_name = buyer.first_name + " " + buyer.second_name

            seller = AppUser.objects.get(username = current_application.property_owner)
            seller_name = seller.first_name +  " " + seller.second_name        

            # Sending contract details to be displayed.
            resp_data =  {'application_id': id, 'seller_username': current_application.property_owner, 'seller_name': seller_name,
                        'property_id': current_application.property_id,  'property_address': property_address, 'duration': property.duration,
                        'city': property_city, 'state': property_state, 'pincode': property_pincode, 'price_pm': property.price, 
                        'contract_value': contract_value, 'date_of_agreement': date_of_agreement, 'party_type': 'Lessor'
                        }
            # messages.info(request, 'Sign the above contract.')
            return render(request, 'lessor_contract.html', resp_data)
    except:
        messages.error(request, 'Unexpected Error')
        return redirect('my_properties_page')

def seller_contract(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    
    try:
        current_application = PropertyApplications.objects.get(id = id)
        property = Property.objects.get(id = current_application.property_id)
        if(property.owner != username):
            messages.error(request, 'You are trying to process contract of a property that you do not own. Please login into respective account first.')
            return redirect('logout_page')
        
        if request.method == 'POST':
            data = json.loads(request.body)
            base64JsonString = data.get('contract_payload', None)
            # jsonString = base64.b64decode(data.get('contract_payload', None)).decode('utf-8')
            base64Signature = data.get('signature', None)
            # signature = base64.b64decode(base64Signature)
            signature = base64.b64decode(data.get('signature', None))
            # print('JSON STRING',jsonString)
            # print('SIGNATURE',signature)

            # Create hash of the same payload and then verify the signatures. 
            # If correct, then accept the application, create a contract and save the data in the table.
            public_key_pem = AppUser.objects.get(username = username).public_key
            public_key = RSA.import_key(public_key_pem)
            # print(public_key)
            # Create a hash of the original file contents
            try:
                h = SHA256.new(base64JsonString.encode('utf-8'))
                verifier = pkcs1_15.new(public_key)
                verifier.verify(h, signature)
            except Exception as e:
                messages.error(request, 'Signature Error!\n Please Try Again.')
                response_data = {
                    'success': False,
                    'url': f'/seller_contract/{id}'
                }
                return JsonResponse(response_data)
            
            # Approve the application & reject others.
            # fetching the object
            current_application = PropertyApplications.objects.get(id = id)
            current_property_id = current_application.property_id
            property = Property.objects.get(id = current_property_id)
            # Changing the current request's status
            current_application.status = 'ACCEPTED'
            current_application.save()
            
            # Rejecting all other pending requests.
            applications = PropertyApplications.objects.filter(property_id=current_property_id, status='PENDING')
            for application in applications:
                application.status = 'REJECTED'
                application.save()
            
            buyer_obj = AppUser.objects.get(username = current_application.interested_user)
            seller_obj = AppUser.objects.get(username = current_application.property_owner)
            # Create a contract object and save the string. 
            signed_token = base64JsonString + "." + base64Signature
            contract_object = Property_Transfer_Contract.objects.create(application_id = id, property_id = current_application.property_id,
                                                                        property_address_line_1 = property.address_line_1, property_address_line_2 = property.address_line_2,
                                                                        property_state = property.state, property_city = property.city, property_pincode = property.pincode,
                                                                        buyer = current_application.interested_user, first_name_buyer = buyer_obj.first_name, second_name_buyer = buyer_obj.second_name,
                                                                        seller = current_application.property_owner, first_name_seller = seller_obj.first_name, second_name_seller = seller_obj.second_name, 
                                                                        price = property.price, date_of_agreement = timezone.now().date(), token = signed_token)
            contract_object.save()
            messages.success(request, 'Successfully approved the application')
            response_data = {
                'success': True,
                'url': '/my_properties/'
            }
            return JsonResponse(response_data)
            
        else:
            # Fetch the current application object.
            current_application = PropertyApplications.objects.get(id = id)
            property = Property.objects.get(id = current_application.property_id)

            property_address = property.address_line_1 + " " +  property.address_line_2
            property_state = property.state
            property_city = property.city
            property_pincode = property.pincode
            contract_value = property.price
            date_of_agreement = timezone.now().date()

            buyer = AppUser.objects.get(username = current_application.interested_user)
            buyer_name = buyer.first_name + " " + buyer.second_name

            seller = AppUser.objects.get(username = current_application.property_owner)
            seller_name = seller.first_name +  " " + seller.second_name        

            # Sending contract details to be displayed.
            resp_data =  {'application_id': id, 'buyer_username':current_application.interested_user,
                        'buyer_name': buyer_name, 'seller_username': current_application.property_owner, 'seller_name': seller_name,
                        'property_id': current_application.property_id,  'property_address': property_address,
                        'city': property_city, 'state': property_state, 'pincode': property_pincode, 
                        'contract_value': contract_value, 'date_of_agreement': date_of_agreement 
                        }
            # messages.info(request, 'Sign the above contract.')
            return render(request, 'seller_contract.html', resp_data)
    except:
        messages.error(request, 'Unexpected Error')
        return redirect('my_properties_page')

# Defining a method for generating OTP and saving its object.
def generateOtpEmail(username):
    otp = str(random.randint(100000, 999999))
    expiry_time = timezone.now() + timedelta(minutes=5)
    
    # Creating the OTP object & saving it for the user. 
    try:
        otp_object = OTP.objects.get(user = username)
        # If already exisiting OTP can be used, save time. 
        if otp_object.valid and otp_object.expiry_time > timezone.now():
            return
        otp_object.valid = True
        otp_object.otp = otp
        otp_object.expiry_time = expiry_time
        otp_object.save()
    except OTP.DoesNotExist:
        otp_object = OTP.objects.create(user = username, otp = otp, expiry_time = expiry_time, valid = True)
        otp_object.save()

    # Sending A mail to the user.
    user_email = AppUser.objects.get(username = username).email
    send_mail(
        subject= 'OTP for transaction (FCS G-13 Portal)',
        message=f'OTP: {otp}',
        from_email='fcsgroup013@gmail.com',
        recipient_list=[
            user_email
        ]
    )

def rentals_payment_gateway(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    if request.session.get('transaction_ekyc') is None or (request.session.get('transaction_ekyc') is not None and request.session.get('transaction_ekyc') != id):
        # EKYC was skipped intentionally.
        messages.info(request, 'EKYC is mandatory before moving on to payment gateway.')
        return redirect('transaction_ekyc_page', id = id)
    try:
        current_application = PropertyApplications.objects.get(id = id)
        property = Property.objects.get(id = current_application.property_id)
        if(property.owner == username or current_application.status != 'ACCEPTED' or current_application.interested_user != username):
            return redirect('logout_page')
        
        if request.method == 'POST':
            data = json.loads(request.body)
            otp = data.get('otp', None)
            if(valid_num(otp) == False or len(otp) !=6):
                messages.error(request, 'Invalid OTP format detected.')
                response_data = {
                    'success': False,
                    'url': f'/rentals_payment_gateway/{id}'
                }
                return JsonResponse(response_data)
            otp_object = OTP.objects.get(user = username)
            if otp_object.valid == False:
                messages.error(request, 'OTP already used before in some old transaction.')
                response_data = {
                    'success': False,
                    'url': f'/rentals_payment_gateway/{id}'
                }
                return JsonResponse(response_data)
            if otp_object.expiry_time < timezone.now():
                messages.error(request, 'OTP expired. Please check your mail again.')
                response_data = {   
                    'success': False,
                    'url': f'/rentals_payment_gateway/{id}'
                }
                return JsonResponse(response_data)
            if otp != otp_object.otp:
                messages.error(request, 'OTP did not match.')
                response_data = {
                    'success': False,
                    'url': f'/rentals_payment_gateway/{id}'
                }
                return JsonResponse(response_data)

            base64JsonString = data.get('contract_payload', None)
            # jsonString = base64.b64decode(data.get('contract_payload', None)).decode('utf-8')
            base64Signature = data.get('signature', None)
            # signature = base64.b64decode(base64Signature)
            signature = base64.b64decode(data.get('signature', None))
            # print('JSON STRING',jsonString)
            # print('SIGNATURE',signature)

            # Create hash of the same payload and then verify the signatures. 
            # If correct, then accept the application, create a contract and save the data in the table.
            public_key_pem = AppUser.objects.get(username = username).public_key
            public_key = RSA.import_key(public_key_pem)
            # print(public_key)
            # Create a hash of the original file contents
            try:
                h = SHA256.new(base64JsonString.encode('utf-8'))
                verifier = pkcs1_15.new(public_key)
                verifier.verify(h, signature)
            except Exception as e:
                messages.error(request, 'Signature Error!\n Please Try Again.')
                response_data = {
                    'success': False,
                    'url': f'/rentals_payment_gateway/{id}'
                }
                return JsonResponse(response_data)
            
            # Signing with admin key.
            try:
                with open('/home/iiitd/dj_dir/project/project_app/apk.txt','r') as akf:
                    key = akf.read()
                # print(key)
                pk = RSA.import_key(key)
                # print(pk)
                admin_sign = pkcs1_15.new(pk).sign(h)
                admin_b64_sign = base64.b64encode(admin_sign).decode('utf-8')
            except:
                # print("Error while signing with admin keys")
                messages.error(request, 'Signature Error (T2)!\n Please Try Again.')
                response_data = {
                    'success': False,
                    'url': f'/payment_gateway/{id}'
                }
                return JsonResponse(response_data)
            
            # Signature verification successful. 
            lessee_obj = AppUser.objects.get(username = username)
            current_application = PropertyApplications.objects.get(id = id)
            property = Property.objects.get(id = current_application.property_id)
            # Create a contract object and save the string. 
            signed_token = base64JsonString + "." + base64Signature + "." + admin_b64_sign
            contract_value = property.duration * property.price
            rentals_object = RentalsContract.objects.create(application_id = id, property_id = current_application.property_id,
                                                            property_address_line_1 = property.address_line_1, property_address_line_2 = property.address_line_2,
                                                            property_state = property.state, property_city = property.city, property_pincode = property.pincode,
                                                            username = current_application.interested_user, first_name = lessee_obj.first_name, second_name = lessee_obj.second_name, 
                                                            party_type='lessee' ,date_of_agreement = timezone.now().date(), token = signed_token, duration = property.duration,
                                                            rent_per_month = property.price, total_rent = contract_value)
            rentals_object.save()

            # Changing the owner.
            property_obj = Property.objects.get(id = rentals_object.property_id)
            property_obj.type = 'ON LEASE'
            property_obj.save()

            # Rejecting all other existing pending applications.
            applications = PropertyApplications.objects.filter(property_id= current_application.property_id, status='PENDING')
            for application in applications:
                application.status = 'REJECTED'
                application.save()

            # Updating the application status.
            current_application_obj = PropertyApplications.objects.get(id = id)
            current_application_obj.status = 'SUCCESS'
            current_application_obj.save()

            # Update the OTP object validity.
            otp_object.valid = False
            otp_object.save()

            messages.success(request, 'Transaction Successful!')
            response_data = {
                'success': True,
                'url': '/search_properties/'
            }
            return JsonResponse(response_data)

        else:
            current_application = PropertyApplications.objects.get(id = id)
            # Find the current_user_balance
            current_user = AppUser.objects.filter(username = username)
            current_user_balance = current_user[0].balance
            # print("BALANCE: ",current_user_balance)

            # Find the amount required for the property. (RENTAL -> 12months contract)
            required_amount = None
            current_property_id = current_application.property_id
            property_object = Property.objects.get(id = current_property_id)
            # property_type = property_object.type
            required_amount = property_object.duration * property_object.price
            if(required_amount > current_user_balance):
                messages.error(request, "INSUFFICIENT BALANCE! Please update it & proceed again!")
                return redirect('search_properties_page')
            post_balance = current_user_balance - required_amount
            
            # Fetch the current application object.
            # property = Property.objects.get(id = current_application.property_id)

            property_address = property_object.address_line_1 + " " +  property_object.address_line_2
            property_state = property_object.state
            property_city = property_object.city
            property_pincode = property_object.pincode
            rent_per_month = property_object.price
            rental_duration = property_object.duration
            contract_value = rent_per_month * rental_duration
            # print("hi")
            # print(current_application)
            date_of_agreement = RentalsContract.objects.get(application_id = id).date_of_agreement
            # print("hi")

            buyer = AppUser.objects.get(username = username)
            buyer_name = buyer.first_name + " " + buyer.second_name

            # Sending contract details to be displayed.
                # Sending contract details to be displayed.
            resp_data =  {'application_id': id, 'buyer_username': buyer.username, 'buyer_name': buyer_name,
                        'property_id': current_application.property_id,  'property_address': property_address, 'duration': rental_duration,
                        'city': property_city, 'state': property_state, 'pincode': property_pincode, 'price_pm': rent_per_month, 
                        'contract_value': contract_value, 'date_of_agreement': date_of_agreement, 'party_type': 'Lessee',
                        'post_balance': post_balance
                        }
            
            generateOtpEmail(username)
            messages.info(request, f'OTP sent to {AppUser.objects.get(username = username).email}. Please Check SPAM FOLDER in case you do not find it.')
            return render(request, 'rentals_payment_gateway.html', resp_data)
    except:
        messages.error(request, 'Unexpected Error. Please Try Again Later.')
        return redirect('search_properties_page')
            

def payment_gateway(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    if request.session.get('transaction_ekyc') is None or (request.session.get('transaction_ekyc') is not None and request.session.get('transaction_ekyc') != id):
        # EKYC was skipped intentionally.
        messages.info(request, 'EKYC is mandatory before moving on to payment gateway.')
        return redirect('transaction_ekyc_page', id = id)
    try:
        current_application = PropertyApplications.objects.get(id = id)
        property = Property.objects.get(id = current_application.property_id)
        if(property.owner == username or current_application.status != 'ACCEPTED' or current_application.interested_user != username):
            return redirect('logout_page')
        
        if request.method == 'POST':
            data = json.loads(request.body)
            otp = data.get('otp', None)
            otp_object = OTP.objects.get(user = username)
            if(valid_num(otp) == False or len(otp) !=6):
                messages.error(request, 'Invalid OTP format detected.')
                response_data = {
                    'success': False,
                    'url': f'/rentals_payment_gateway/{id}'
                }
                return JsonResponse(response_data)
            if otp_object.valid == False:
                messages.error(request, 'OTP already used before in some old transaction.')
                response_data = {
                    'success': False,
                    'url': f'/rentals_payment_gateway/{id}'
                }
                return JsonResponse(response_data)
            if otp_object.expiry_time < timezone.now():
                messages.error(request, 'OTP expired. Please check your mail again.')
                response_data = {
                    'success': False,
                    'url': f'/rentals_payment_gateway/{id}'
                }
                return JsonResponse(response_data)
            if otp != otp_object.otp:
                messages.error(request, 'OTP did not match.')
                response_data = {
                    'success': False,
                    'url': f'/rentals_payment_gateway/{id}'
                }
                return JsonResponse(response_data)
            base64JsonString = data.get('contract_payload', None)
            # jsonString = base64.b64decode(data.get('contract_payload', None)).decode('utf-8')
            base64Signature = data.get('signature', None)
            # signature = base64.b64decode(base64Signature)
            signature = base64.b64decode(data.get('signature', None))
            # print('JSON STRING',jsonString)
            # print('SIGNATURE',signature)

            # Create hash of the same payload and then verify the signatures. 
            # If correct, then accept the application, create a contract and save the data in the table.
            public_key_pem = AppUser.objects.get(username = username).public_key
            public_key = RSA.import_key(public_key_pem)
            # print(public_key)
            # Create a hash of the original file contents
            try:
                h = SHA256.new(base64JsonString.encode('utf-8'))
                verifier = pkcs1_15.new(public_key)
                verifier.verify(h, signature)
            except Exception as e:
                messages.error(request, 'Signature Error!\n Please Try Again.')
                response_data = {
                    'success': False,
                    'url': f'/payment_gateway/{id}'
                }
                return JsonResponse(response_data)
            
            # Signing with admin key.
            try:
                with open('/home/iiitd/dj_dir/project/project_app/apk.txt','r') as akf:
                    key = akf.read()
                # print(key)
                pk = RSA.import_key(key)
                # print(pk)
                admin_sign = pkcs1_15.new(pk).sign(h)
                admin_b64_sign = base64.b64encode(admin_sign).decode('utf-8')
            except:
                # print("Error while signing with admin keys")
                messages.error(request, 'Signature Error (T2)!\n Please Try Again.')
                response_data = {
                    'success': False,
                    'url': f'/payment_gateway/{id}'
                }
                return JsonResponse(response_data)
            
            # Signature verification successful. 
            # Append the signature.
            contract_object = Property_Transfer_Contract.objects.get(application_id = id)
            contract_object.token = contract_object.token + "." + base64Signature + "." + admin_b64_sign
            contract_object.save()

            # Changing the owner.
            property_obj = Property.objects.get(id = contract_object.property_id)
            property_obj.owner = contract_object.buyer
            property_obj.type = 'DELISTED'
            property_obj.save()

            # Rejecting all existing applications of this property.
            applications = PropertyApplications.objects.filter(property_id= current_application.property_id, status='PENDING')
            for application in applications:
                application.status = 'REJECTED'
                application.save()
            
            # Updating the current application status.
            current_application_obj = PropertyApplications.objects.get(id = id)
            current_application_obj.status = 'SUCCESS'
            current_application_obj.save()        

            # Updating the OTP object.
            otp_object.valid = False
            otp_object.save()
            messages.success(request, 'Transaction Successful!')
            response_data = {
                'success': True,
                'url': '/search_properties/'
            }
            return JsonResponse(response_data)

        else:
            current_application = PropertyApplications.objects.get(id = id)
            # Find the current_user_balance
            current_user = AppUser.objects.filter(username = username)
            current_user_balance = current_user[0].balance
            # print("BALANCE: ",current_user_balance)

            # Find the amount required for the property. (RENTAL -> 12months contract)
            required_amount = None
            current_property_id = current_application.property_id
            property_object = Property.objects.get(id = current_property_id)
            property_type = property_object.type
            if(property_type.lower() == 'rent'):
                required_amount = property_object.duration * property_object.price
                if(required_amount > current_user_balance):
                    messages.error(request, "INSUFFICIENT BALANCE! Please update it & proceed again!")
                    return redirect('search_properties_page')
                post_balance = current_user_balance - required_amount
                
                # Fetch the current application object.
                # property = Property.objects.get(id = current_application.property_id)

                property_address = property_object.address_line_1 + " " +  property_object.address_line_2
                property_state = property_object.state
                property_city = property_object.city
                property_pincode = property_object.pincode
                rent_per_month = property_object.price
                rental_duration = property_object.duration
                contract_value = rent_per_month * rental_duration
                # print("hi")
                date_of_agreement = RentalsContract.objects.get(application_id = id)
                # print("hi")

                buyer = AppUser.objects.get(username = username)
                buyer_name = buyer.first_name + " " + buyer.second_name

                seller = AppUser.objects.get(username = PropertyApplications.objects.get(id = id).property_owner)
                # seller = AppUser.objects.get(username = Property_Transfer_Contract.objects.get(application_id = id).seller)
                seller_name = seller.first_name +  " " + seller.second_name        

                # Sending contract details to be displayed.
                # Sending contract details to be displayed.
                resp_data =  {'application_id': id, 'seller_username': current_application.property_owner, 'seller_name': seller_name,
                            'property_id': current_application.property_id,  'property_address': property_address, 'duration': rental_duration,
                            'city': property_city, 'state': property_state, 'pincode': property_pincode, 'price_pm': rent_per_month, 
                            'contract_value': contract_value, 'date_of_agreement': date_of_agreement, 'party_type': 'Lessee'
                            }
                # messages.info(request, 'Sign the above contract.')
                return render(request, 'payment_gateway.html', resp_data)
            else:
                required_amount = property_object.price
                # print("REQUIRED_AMOUNT: ", required_amount, "\nBALANCE AVAILABLE: ", current_user_balance)

                if(required_amount > current_user_balance):
                    messages.error(request, "INSUFFICIENT BALANCE!")
                    return redirect('search_properties_page')
                post_balance = current_user_balance - required_amount
                
                # Fetch the current application object.
                # property = Property.objects.get(id = current_application.property_id)

                property_address = property_object.address_line_1 + " " +  property_object.address_line_2
                property_state = property_object.state
                property_city = property_object.city
                property_pincode = property_object.pincode
                contract_value = property_object.price
                date_of_agreement = Property_Transfer_Contract.objects.get(application_id = id).date_of_agreement

                buyer = AppUser.objects.get(username = username)
                buyer_name = buyer.first_name + " " + buyer.second_name

                seller = AppUser.objects.get(username = PropertyApplications.objects.get(id = id).property_owner)
                # seller = AppUser.objects.get(username = Property_Transfer_Contract.objects.get(application_id = id).seller)
                seller_name = seller.first_name +  " " + seller.second_name        

                # Sending contract details to be displayed.
                resp_data =  {'application_id': id, 'buyer_username':current_application.interested_user,
                            'buyer_name': buyer_name, 'seller_username': current_application.property_owner, 'seller_name': seller_name,
                            'property_id': current_application.property_id,  'property_address': property_address,
                            'city': property_city, 'state': property_state, 'pincode': property_pincode, 
                            'contract_value': contract_value, 'date_of_agreement': date_of_agreement, 'post_balance': post_balance
                            }
                # messages.info(request, 'Sign the above contract.')
                generateOtpEmail(username)
                messages.info(request, f'OTP sent to {AppUser.objects.get(username = username).email}. Please Check SPAM FOLDER in case you do not find it.')
                return render(request, 'payment_gateway.html', resp_data)
    except:
        messages.error(request, 'Unexpected Error. Please Try Again Later.')
        return redirect('search_properties_page')

def process_payment(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    
    current_application = PropertyApplications.objects.get(id = id)
    property = Property.objects.get(id = current_application.property_id)
    if(property.owner == username or current_application.status != 'ACCEPTED' or current_application.interested_user != username):
        return redirect('logout_page')
    # 1. Balance Reduction & Addition (Completed here)
        # Find the current_user_balance
    current_user = AppUser.objects.filter(username = username)[0]
    current_user_balance = current_user.balance
    
    current_application = PropertyApplications.objects.get(id =id)
    current_property_id = current_application.property_id
    property_object = Property.objects.get(id = current_property_id)
    required_amount = None
    current_property_id = current_application.property_id
    property_object = Property.objects.get(id = current_property_id)
    property_type = property_object.type
    if(property_type.lower() == 'rent'):
        required_amount = property_object.duration * property_object.price
    else:
        required_amount = property_object.price
    # print("REQUIRED_AMOUNT: ", required_amount, "\nBALANCE AVAILABLE: ", current_user_balance)
        # Updating the balance and saving the database. 
    current_user.balance = current_user_balance - required_amount
    current_user.save()

    seller = AppUser.objects.filter(username = current_application.property_owner)[0]
    seller.balance = seller.balance + required_amount
    seller.save()

    # 2. Ownership transfer (in case of sell) & de-list it.
    if(property_type.lower() == 'sell'):
        property_object.owner = username
        property_object.type = 'DELISTED'
        property_object.save()
    # 3. If rentals -> property_status (delist it).
    if(property_type.lower() == 'rent'):
        property_object.lessee = username
        property_object.type = 'DELISTED'
        property_object.save()
    # 4. Application status change to SUCCESS
    current_application.status = 'SUCCESS'
    current_application.save()
    # 5. Contract Creation.
        # Step 1: Create Contract (including the signatures)
        # Step 2: Past history web page date should be obtained from contracts table.

    messages.success(request, "Transaction SUCCESSFUL")
    return redirect('search_properties_page')

def past_buy_history(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')
    if(username is None):
        return redirect('login_page')

    try:
        if request.method == 'GET':
            contracts = Property_Transfer_Contract.objects.filter(buyer = username)
            buy_contracts_list = []
            for i in range(len(contracts)):
                # print(c.application_id)   
                # print(c)
                application = PropertyApplications.objects.get(id = contracts[i].application_id)
                # print(application.status)
                if application.status == 'SUCCESS':
                    temp = {
                        'application_id':contracts[i].application_id,
                        'type':'BUY',
                        'property_id': contracts[i].property_id,
                        'seller': contracts[i].seller,
                        'date_of_agreement': contracts[i].date_of_agreement,
                        'price': contracts[i].price
                    }
                    # print(type(c))
                    buy_contracts_list.append(temp)

            contracts = RentalsContract.objects.filter(username = username, party_type = 'lessee')
            # print(rental_contracts)
            for i in range(len(contracts)):
                application = PropertyApplications.objects.get(id = contracts[i].application_id)
                # print(application.status)
                if application.status == 'SUCCESS':
                    temp = {
                        'application_id':contracts[i].application_id,
                        'type':'RENT',
                        'property_id': contracts[i].property_id,
                        'seller': 'portal',
                        'date_of_agreement': contracts[i].date_of_agreement,
                        'price': contracts[i].total_rent
                    }
                    # print(type(c))
                    buy_contracts_list.append(temp)
            # print("HELLO")
            # properties = Property.objects.values()
            # for i in range(len(properties)):
            #     if username == properties[i]["owner"]:
            #         my_properties_list.append(properties[i])
            # print("NUMBER_OF_PROPERTIES:",len(my_properties_list))
            return render(request, 'past_buy_history.html', {'contracts':buy_contracts_list})
    except:
        messages.error(request, 'Unexpected Error. Please Try Again Later.')
        return redirect('dashboard_page')

def past_sell_history(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    try:
        if request.method == 'GET':
            sell_contracts_list = []
            contracts = Property_Transfer_Contract.objects.filter(seller = username)
            for i in range(len(contracts)):
                # print(c.application_id)
                # print(c)
                application = PropertyApplications.objects.get(id = contracts[i].application_id)
                # print(application.status)
                if application.status == 'SUCCESS':
                    temp = {
                        'application_id':contracts[i].application_id,
                        'type':'SELL',
                        'property_id': contracts[i].property_id,
                        'buyer': contracts[i].buyer,
                        'date_of_agreement': contracts[i].date_of_agreement,
                        'price': contracts[i].price
                    }
                    # print(type(c))
                    sell_contracts_list.append(temp)
                    # sell_contracts_list.append(c)
            contracts = RentalsContract.objects.filter(username = username, party_type = 'lessor')
            for i in range(len(contracts)):
                # print(c.application_id)
                # print(c)
                application = PropertyApplications.objects.get(id = contracts[i].application_id)
                # print(application.status)
                if application.status == 'SUCCESS':
                    temp = {
                        'application_id':contracts[i].application_id,
                        'type':'RENT',
                        'property_id': contracts[i].property_id,
                        'buyer': 'portal',
                        'date_of_agreement': contracts[i].date_of_agreement,
                        'price': contracts[i].total_rent
                    }
                    # print(type(c))
                    sell_contracts_list.append(temp)
            # print("HELLO")
            # properties = Property.objects.values()
            # for i in range(len(properties)):
            #     if username == properties[i]["owner"]:
            #         my_properties_list.append(properties[i])
            # print("NUMBER_OF_PROPERTIES:",len(my_properties_list))
            return render(request, 'past_sell_history.html', {'contracts':sell_contracts_list})
    except:
        messages.error(request, 'Unexpected Error. Please Try Again Later.')
        return redirect('dashboard_page')

def view_contract(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')
    
    if(username is None):
        return redirect('login_page')
    
    try:
        current_application = PropertyApplications.objects.get(id = id)
        # Unauthorized access.
        if(username != current_application.interested_user and username != current_application.property_owner):
            return redirect('logout_page')
        
        if(current_application.application_type == 'RENT'):
            # Rental Contract
            if username == current_application.interested_user:
                rentalsContract = RentalsContract.objects.get(application_id = id, party_type = 'lessee')
                # Lessee
                return render(request, 'rentals_contract.html', {
                    'current_application_id': id,
                    'party_name': rentalsContract.first_name + " " + rentalsContract.second_name,
                    'party_username': rentalsContract.username,
                    'party_type': rentalsContract.party_type,
                    'property_id': rentalsContract.property_id,
                    'property_address': rentalsContract.property_address_line_1 + " " + rentalsContract.property_address_line_2,
                    'city': rentalsContract.property_city,
                    'state': rentalsContract.property_state,
                    'pincode': rentalsContract.property_pincode,
                    'duration': rentalsContract.duration,
                    'price_pm': rentalsContract.rent_per_month,
                    'contract_value': rentalsContract.total_rent,
                    'date_of_agreement': rentalsContract.date_of_agreement,
                    'token': rentalsContract.token,
                })
            else:
                # Lessor
                rentalsContract = RentalsContract.objects.get(application_id = id, party_type = 'lessor')
                return render(request, 'rentals_contract.html', {
                    'current_application_id': id,
                    'party_name': rentalsContract.first_name + " " + rentalsContract.second_name,
                    'party_username': rentalsContract.username,
                    'party_type': rentalsContract.party_type,
                    'property_id': rentalsContract.property_id,
                    'property_address': rentalsContract.property_address_line_1 + " " + rentalsContract.property_address_line_2,
                    'city': rentalsContract.property_city,
                    'state': rentalsContract.property_state,
                    'pincode': rentalsContract.property_pincode,
                    'duration': rentalsContract.duration,
                    'price_pm': rentalsContract.rent_per_month,
                    'contract_value': rentalsContract.total_rent,
                    'date_of_agreement': rentalsContract.date_of_agreement,
                    'token': rentalsContract.token,
                })
        else:
            # Buy/Sell contract -> Single Contract exists & hence, we don't need to check what to show.
            transferContract = Property_Transfer_Contract.objects.get(application_id = id)
            # print(transferContract.application_id)
            # print(id)
            # print(current_application.id)
            return render(request, 'property_transfer_contract.html', {
                'current_application_id': id,
                'buyer_username': transferContract.buyer,
                'buyer_name': transferContract.first_name_buyer + " " + transferContract.second_name_buyer,
                'seller_username': transferContract.seller,
                'seller_name': transferContract.first_name_seller + " " + transferContract.second_name_seller,
                'property_id': transferContract.property_id,
                'property_address': transferContract.property_address_line_1 + " " + transferContract.property_address_line_2,
                'city': transferContract.property_city,
                'state': transferContract.property_state,
                'pincode': transferContract.property_pincode,
                'contract_value': transferContract.price,
                'date_of_agreement': transferContract.date_of_agreement,
                'token': transferContract.token,
            })
    except:
        messages.error(request, 'Unexpected Error in displaying the contract.')
        return redirect('dashboard_page')

def verify_contract(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')
    
    if(username is None):
        return redirect('login_page')
    
    if request.method == 'POST':
        application_id = request.POST['application_id']
        token = request.POST['token']
        # Input validation.
        if (valid_num(application_id) == False or len(application_id) == 0 or len(token) == 0):
            messages.error(request, 'Invalid Input.')
            return redirect('verify_contract_page')

        # Fetching the corresponding application: 
        try:
            current_application = PropertyApplications.objects.get(id = application_id)
            # Checking if current application is having SUCCESS or not.
            if(current_application.status != 'SUCCESS'):
                messages.error(request, "APPLICATION PENDING/REJECTED")
                return redirect('verify_contract_page')

            # Fetching the contract object: 
            if current_application.application_type == 'RENT':
                # Fetch the contract
                contract = RentalsContract.objects.filter(application_id = application_id)
                for i in contract:
                    if token == i.token:
                        # Valid contract.
                        messages.success(request, "Token is VALID")
                        return redirect('verify_contract_page')
                # Invalid Contract/Token.
                messages.error(request, "Token is INVALID")
                return redirect('verify_contract_page')
            else:
                # SELL TYPE APPLICATION
                contract = Property_Transfer_Contract.objects.get(application_id = application_id)
                if contract.token == token:
                    messages.success(request, "Token is VALID")
                    return redirect('verify_contract_page')
                # Invalid Contract/Token.
                messages.error(request, "Token is INVALID")
                return redirect('verify_contract_page')
        except PropertyApplications.DoesNotExist:
            # No such application exists:
            messages.error(request, "No such application exists.")
            return render(request, 'verify_contract.html')
    else:
        # GET request.
        # messages.info(request, 'Fill the desired fields and hit verify.')
        return render(request, 'verify_contract.html')
    
def edit_profile(request):
    username = request.session.get('username')
    
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')
    
    if(username is None):
        return redirect('login_page')
    
    if request.method == 'POST':
        try:
            contact = request.POST['contact']
            balance = request.POST['balance']
            # Checking for password.
            password = request.POST['newPassword']
            confirmPassword = request.POST['confirmPassword']

            # Input Validation:
            if(valid_num(contact) == False or len(contact) != 10 or valid_num(balance) == False or int(balance) <0 or int(balance) > 100000000000 ):
                messages.error(request, 'Invalid input format')
                return redirect('edit_profile_page')
            
            if ( password != '' and (valid_text(password) == False or len(password) < 5 or len(password) > 30)):
                messages.error(request, 'Invalid password format.')
                return redirect('edit_profile_page')
            
            if( confirmPassword != '' and (valid_text(confirmPassword) == False or password != confirmPassword)):
                messages.error(request, 'Invalid password/confirm-password format.')
                return redirect('edit_profile_page')

            if(password == ''):
                current_user = AppUser.objects.get(username = username)
                current_user.balance = balance
                current_user.contact = contact
                current_user.save()
                messages.success(request, 'SAVED PROFILE SUCCESSFULLY')
                return redirect('dashboard_page')
            else:
                # Password also needs to be changed.
                if password!= confirmPassword:
                    messages.error(request, 'Passwords DID NOT MATCH.')
                    return redirect(edit_profile)
                # Passwords matched. -> Calculate hash and update the user profile.
                hash = hashlib.sha256()
                hash.update(password.encode())
                new_password = hash.hexdigest()
                current_user = AppUser.objects.get(username = username)
                current_user.balance = balance
                current_user.contact = contact
                current_user.password = new_password
                current_user.save()
                request.session['username'] = None
                # Redirecting to the login page for a fresh login. 
                messages.success(request, 'Profile & password have been updated successfully')
                return redirect('login_page')
        except:
            messages.error(request, "Unexpected error while processing. Please Try Again Later.")
            return redirect('dashboard_page')
    else:
        # GET request.
        try:
            current_user = AppUser.objects.get(username = username)
            return render(request, 'edit_profile.html', {
                'username': username,
                'full_name': current_user.first_name + " " + current_user.second_name,
                'email_address': current_user.email,
                'contact_number': current_user.contact,
                'balance': current_user.balance
            })
        except:
            messages.error(request, 'Unexpected error while extracting user detials. Please Try Again Later.')
            return redirect('dashboard_page')
    
def transaction_ekyc(request, id):
    username = request.session.get('username')
    
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')
    
    if(username is None):
        return redirect('login_page')
    
    try:
        if request.method == 'POST':
            email_input = request.POST['email'].lower()
            password_input = request.POST['password']
            # Input validation.
            if(valid_email(email_input) == False  or valid_text(password_input) == False):
                # print(valid_email(email_input), valid_text(password_input))
                messages.error(request, 'Invalid Input Format.')
                return redirect('transaction_ekyc_page', id = id)
            # print(type(email_input))
            dictionary = {
                "email": email_input,
                "password":password_input
            }
            # print(email_input, password_input)
            # Will call the API here and set the flag accordingly.
            try:
                api_response = requests.post('https://192.168.3.39:5000/kyc', json = dictionary, verify= False)
                if api_response.status_code == 200:
                    response_data = api_response.json()
                    if(response_data.get('status') == 'success'):
                        # messages.success(request, 'Verification Successful!')
                        # Checking type of application and redirecting the user.
                        current_application = PropertyApplications.objects.get(id = id)
                        request.session['transaction_ekyc'] = id
                        if current_application.application_type == 'RENT':
                            return redirect('rentals_payment_gateway_page', id= id)
                        else:
                            return redirect('payment_gateway_page', id = id)
                    elif response_data.get('status') == 'error':
                        messages.error(request, response_data.get('message'))
                        return redirect('transaction_ekyc_page', id = id)
                else:
                    messages.error(request, 'Error Code: {api_response.stat  us_code}')
                    return redirect('transaction_ekyc_page', id = id)
            except requests.exceptions.RequestException as e:
                messages.error(request, 'PLEASE TRY AGAIN LATER')
                return redirect('transaction_ekyc_page', id = id)
        else:
            # GET Request.
            return render(request, 'transaction_ekyc.html', {'id': id})
    except:
        messages.error(request, 'Unexpected Error. Please Try Again Later.')
        return redirect('search_properties_page')

def report_malicious_buyer(request, id):
    username = request.session.get('username')
    
    if(request.session.get('email_kyc') is None):
        return redirect('logout_page')
    
    if(username is None):
        return redirect('login_page')
    
    try:
        currentApplication = PropertyApplications.objects.get(id = id)
        buyer = currentApplication.interested_user
        if currentApplication.property_owner != username:
            messages.error(request, 'You can not report a buyer in an application where you are not the property owner.')
            return redirect('my_properties_page')
        status = currentApplication.status
        if status == 'PENDING':
            messages.error(request, 'Can not report a buyer without a valid contract in progress')
            return redirect('my_properties_page')
        elif status == 'SUCCESS':
            messages.error(request, 'Can not report a buyer once the contract has been completed.')
            return redirect('my_properties_page')
        elif status == 'ACCEPTED':
            # Check if already reported.
            try:
                previous_record = ReportedBuyer.objects.get(application_id = id)
                messages.info(request, f'You have already reported the user: {currentApplication.interested_user} .')
                return redirect('my_properties_page')
            except ReportedBuyer.DoesNotExist:
                # Reporting the buyer for the first time.
                date_of_agreement = None
                if currentApplication.application_type == 'RENT':
                    date_of_agreement = RentalsContract.objects.get(application_id = id).date_of_agreement
                else:
                    date_of_agreement = Property_Transfer_Contract.objects.get(application_id = id).date_of_agreement
                if timezone.now().date() - date_of_agreement < timedelta(days = 5):
                    messages.info(request, 'You can not report a buyer within 5 immediate days after agreement.')
                    return redirect('my_properties_page')
                else:
                    # Create a new report object.
                    new_report = ReportedBuyer.objects.create(application_id = id, buyer = currentApplication.interested_user, seller = username)
                    new_report.save()

                    # cancelling the transaction.
                    currentApplication.status = 'CANCELLED'
                    currentApplication.save()
                    messages.success(request, f'User {buyer} has been reported & Transaction has been cancelled.')
                    return redirect('my_properties_page')
        elif status == 'REJECTED':
            messages.error(request, 'You can not report a buyer without having a PENDING contract.')
            return redirect('my_properties_page')
        elif status == 'CANCELLED':
            messages.error(request, 'Transaction has already been cancelled and the buyer was reported.')
            return redirect('my_properties_page')
    except:
        messages.error(request, 'Unexpected Error while processing the request.')
        return redirect('my_properties_page')

def reported_buyers_list(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    
    # Still need to add logic for only admin to be able to access it. (optional)
    return render(request, 'reported_buyer.html', context = {'reports': ReportedBuyer.objects.all()})

def reported_property_list(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    
    reports = list(ReportedListing.objects.values())
    reportsList = []
    for i in range(len(reports)):
        property = Property.objects.get(id = reports[i]['property_id'])
        if property.type != 'BANNED':
            reportsList.append(reports[i])
    # Still need to add logic for only admin to be able to access it. (optional)
    return render(request, 'reported_property_list.html', context = {'reports': reportsList})

def report_listing(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    
    try:
        if request.method == 'POST':
            complain = None
            complain_id = request.POST['complain_id']
            # Input Validation.
            if(valid_num(complain_id) == False or len(complain_id) != 1 ):
                messages.error(request, 'Invalid input format.')
                return redirect('report_listing_page', id = id)
            if complain_id == 1:
                # Seller is not the rightful owner.
                complain = "Seller is not the RIGHTFUL owner."
            elif complain_id == 2:
                # Listed property doesn't exist.
                complain = "Listed Property do NOT exist."
            elif complain_id == 3:
                complain = "Multiple Transactions detected for the same listed property."
            
            try:
                existing_report = ReportedListing.objects.get(property_id = id, reporter = username)
                messages.info(request, 'You can only report once per listing')
                return redirect('search_properties_page')
            except ReportedListing.DoesNotExist:
                # Create a report object for the listed property.
                new_report = ReportedListing.objects.create(property_id = id, complain_id = complain_id, reporter = username)
                new_report.save()
                messages.success(request, 'The listed property has been reported to the admin.')
                return redirect('search_properties_page')
        else:
            # Get request
            currentProperty = Property.objects.get(id = id)
            if currentProperty.owner == username:
                messages.error(request, 'You can not report your own property')
                return redirect('search_properties_page')
            
            return render(request, 'report_listing.html', {'id': id})
    except:
        messages.error(request, 'Unexpected error while processing the request. Please Try Again Later')
        return redirect('search_properties_page')

def ban_property(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None):
            return redirect('logout_page')
    if(username is None):
        return redirect('login_page')
    
    if username not in ['chirag20047']:
        messages.error(request, "Unauthorized Acces Detected. Report Sent. Ekyc access may be revoked for this account.")
        return redirect('logout_page')
    
    try:
        currentProperty = Property.objects.get(id = id)
        currentProperty.type = 'BANNED'
        currentProperty.save()

        messages.success(request, 'Successfully banned the listing.')
        return redirect('reported_property_list_page') 
    except:
        messages.error(request, 'Error while processing the ban request.')
        return redirect('reported_property_list_page')