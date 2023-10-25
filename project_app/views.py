from django.shortcuts import render, redirect, reverse
from .models import AppUser, Property, PropertyApplications
from django.contrib import messages
import hashlib, json
import requests
from django.shortcuts import get_object_or_404
from datetime import date 
import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

# Create your views here.
# @csrf_exempt
def login_user(request):
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
        return redirect('/')
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
                    messages.info(request, "Document Verification Pending")
                    return redirect('user_document_verification_page', id=user_id)
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
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
        return redirect('/')
    if request.method == 'POST':
        input_first_name = request.POST['firstname']
        input_last_name = request.POST['lastname']
        input_username = request.POST['username']
        # input_email = request.POST['email']
        input_contact = request.POST['contact']
        input_password = request.POST['password']
        input_confirm_password = request.POST['confirm_password']
        if input_password==input_confirm_password:
            # Passwords matched
            if AppUser.objects.filter(username=input_username).exists():
                messages.info(request, 'Username already EXISTS.')
                return redirect(register_user)
            # elif AppUser.objects.filter(email=input_email).exists():
            #     messages.info(request, 'Email already EXISTS.')
            #     return redirect(register_user)
            else:
                hash = hashlib.sha256()
                hash.update(input_password.encode())
                input_password = hash.hexdigest()
                user = AppUser.objects.create(username=input_username, password=input_password, 
                                        email=request.session.get('email_kyc'), first_name=input_first_name, second_name=input_last_name, contact=input_contact, balance = 10000000, public_key = None)
                user.save()
                # Obtaining the user's id.
                user_id = user.id
                # print("ID:", user_id)
                return redirect('user_document_verification_page', id = user_id)
        # Passwords unmatched.
        else:
            messages.info(request, 'Passwords UNMATCHED')
            return redirect(register_user)
            
    else:
        return render(request, 'signup.html')

def user_document_verification(request, id):
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
        return redirect('/')
    if request.method == 'POST':
        public_key_pem = request.POST['publicKey']
        originalFileContents = request.POST['originalFile']
        signature = request.POST['signedFile']
        # hash = request.POST['hashed']
        print(id)
        verification_result = 'FAIL'
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
                verification_result = 'PASS'
                # Update the user's dv boolean_field & store the public_key_pem.
                current_user = AppUser.objects.get(id = id)
                current_user.dv = True
                current_user.public_key = public_key_pem.decode('utf-8')
                current_user.save()
            messages.info(request, 'Document Verification Successful')
            return redirect('login_page')
            # return render(request, 'user_document_verification_result.html', {'public_key_pem':public_key_pem, 'public_key':public_key, 'originalFile':originalFileContents,
            #                                                                 'signature': signature, 'result': verification_result})
    
        except Exception as e:
            # Handle any exceptions that may occur during verification
            # print("Error during verification:", str(e))
            # Print specific details about the data and error
            messages.info('Document Verification Failed!\n Please Try Again.')
            return render(request, 'user_document_verification.html', {'id': id})

    elif request.method == 'GET':
        messages.info(request, 'NOTE: Leaving the verification process in between may hamper user experience.')
        return render(request, 'user_document_verification.html', {'id': id})

def ekyc(request):
    # status -> success, error
    # message -> Login successful, Invalid password or Invalid email
    if request.method == 'POST':
        email_input = request.POST['email'].lower()
        password_input = request.POST['password']
        # print(type(email_input))
        dictionary = {
            "email": email_input,
            "password":password_input
        }
        # print(email_input, password_input)
        # Will call the API here and set the flag accordingly.
        try:
            api_response = requests.post('https://192.168.3.39:5000/kyc', json = dictionary, verify= False)
            # print(api_response)
            if api_response.status_code == 200:
                response_data = api_response.json()
                # return JsonResponse(response_data)
                if(response_data.get('status') == 'success'):
                    messages.info(request, 'eKYC successful')
                    request.session['email_kyc'] = email_input
                    request.session['password_kyc'] = password_input  
                    return redirect('/login')
                elif response_data.get('status') == 'error':
                    messages.info(request, response_data.get('message'))
                    return redirect('/')
            else:
                messages.info(request, 'Error Code: {api_response.stat  us_code}')
                return redirect('/')
        except requests.exceptions.RequestException as e:
            messages.info(request, 'PLEASE TRY AGAIN LATER')
            return redirect('/')
    else:
        # GET REQUEST
        if(request.session.get('email_kyc') is not None and request.session.get('password_kyc') is not None):
            if(request.session.get('username') is None):
                return redirect('login_page')
            else:
                if(request.session.get('username') in ['chirag20047']):
                    return redirect('admin_dashboard_page')
                return redirect('dashboard_page')
        return render(request, 'ekyc.html')

def dashboard_admin(request):
    if request.method == "POST":
        username = request.session.get('username')
        # print(username)
        if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
        if(username is None):
            return redirect('/login')    
    else:
        username = request.session.get('username')
        if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
        if(username is None):
            return redirect('/login') 
        current_user = []
        users = AppUser.objects.all()
        for x in users:
            if x.username == username:
                current_user = x
                break
        return render(request, 'admin_dashboard.html', {'user': current_user}) 

# @login_required
def dashboard_user(request):
    if request.method == "POST":
        username = request.session.get('username')
        if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
        if(username is None):
            return redirect('/login')
        # if(username is None):
        # return redirect('/')
        pass
    else:
        username = request.session.get('username')
        if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
        if(username is None):
            return redirect('/login')
        # print(username)
        current_user = []
        users = AppUser.objects.all()
        for x in users:
            if x.username == username:
                current_user = x
                break
        return render(request, 'dashboard.html', {'user': current_user})
        
def dashboard_user_list(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
    if(username is None):
        return redirect('/login')
    users = list(AppUser.objects.values())
    user_list = []
    for i in range(len(users)):
        if(users[i]['username'] != request.session.get('username')):
            # print(users[i])
            user_list.append(users[i])
    return render(request, 'user_list.html', {'users':user_list})

def add_property(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
    if(username is None):
        return redirect('/login')
    # print(username)
    if request.method == "POST":
        if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
        if(username is None):
            return redirect('/login')
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
        if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
        if(username is None):
            return redirect('/login')
        return render(request, 'add_property.html')
    
def my_properties(request):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
    if(username is None):
        return redirect('/login')
    if(request.method == 'POST'):
        pass
    else:
        my_properties_list = []
        properties = Property.objects.values()
        for i in range(len(properties)):
            if username == properties[i]["owner"]:
                my_properties_list.append(properties[i])
        # print("NUMBER_OF_PROPERTIES:",len(my_properties_list))
        return render(request, 'my_properties.html', {'properties':my_properties_list})
    
def search_properties(request):
    if(request.method == 'POST'):
        username = request.session.get('username')
        if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
        if(username is None):
            return redirect('/login')
    else:
        username = request.session.get('username')
        # print(type(username), username)
        if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
        if(username is None):
            return redirect('/login')
        my_properties_list = []
        properties = list(Property.objects.values())
        # print(properties)
        for i in range(len(properties)):
            if(properties[i]['owner'] !=username and properties[i]['type'] != 'DELISTED'):
                my_properties_list.append(properties[i])
        # print("LENGTH:", len(my_properties_list))
        # print("SELECTED LIST:\n", (my_properties_list))

        # Fetching property_applications data
        applications = list(PropertyApplications.objects.values())
        # print(applications)
        user_details = [{'user': username}]
        return render(request, 'search_properties.html', {'properties':my_properties_list, 'applications':applications, 'user': user_details})
    

def edit_property(request, id = id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
    if(username is None):
        return redirect('/login')
    property = Property.objects.get(id=id)
    return render(request, 'edit_property.html', {'property':property})

def update_property(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
    if(username is None):
        return redirect('/login')
    property = Property.objects.get(id=id)
    if request.method =="POST":
        property_instance = get_object_or_404(Property, pk = id)
        # input_addr_l1 = request.POST['address-line-1']
        # input_addr_l2 = request.POST['address-line-2']
        # input_city = request.POST['city']
        # input_pin_code = request.POST['pin-code']
        # input_state = request.POST['state']
        input_contract_type = request.POST['contract-type']
        input_facilities = request.POST['facilities']
        input_contract_type = request.POST['contract-type']
        input_price = request.POST['price']
        input_availability_from = request.POST['availability-from']
        input_availability_till = request.POST['availability-till']
        if(input_contract_type == 'RENT' and (input_availability_from == '' or input_availability_till == '')):
            messages.info(request, 'PLEASE FILL AVAILABILITY DATES')
            return redirect('edit_property_page')
        # print(input_availability_from, input_availability_till, input_contract_type, input_state, input_facilities)

        # Date fields
        if(input_contract_type == 'RENT'):
            # property_instance.owner = input_owner
            # property_instance.address_line_1 = input_addr_l1
            # property_instance.address_line_2 = input_addr_l2
            # property_instance.state = input_state
            # property_instance.city = input_city
            # property_instance.pincode = input_pin_code
            # property_instance.type = input_contract_type
            property_instance.starting_date = input_availability_from
            property_instance.ending_date = input_availability_till
            property_instance.price = input_price
            property_instance.facilities = input_facilities
            property_instance.save()
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
            property_instance.starting_date = None
            property_instance.ending_date = None
            # print(property_instance.starting_date)
            # print(property_instance.ending_date)
            property_instance.price = input_price
            property_instance.facilities = input_facilities
            property_instance.save()
            return redirect('my_properties_page')  
    else:
        return render(request, 'edit_property.html', {'property':property})

def delete_property(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
    if(username is None):
        return redirect('/login')
    property = Property.objects.get(id=id)
    property.delete()
    return redirect('my_properties_page')

def logout_user(request):
    request.session.flush()
    return redirect('/')

def apply_property_deal(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
    if(username is None):
        return redirect('/login')
    property_selected = Property.objects.get(id=id)
    property_owner_username = Property.owner

    # Check if no existing row/copy is there:
    applications = list(PropertyApplications.objects.values())
    for i in range(len(applications)):
        if(applications[i]['property_id'] == id and applications[i]['status'] == 'ACCEPTED'):
            if(applications[i]['interested_user'] == username):
                messages.info(request, 'Your request has been accepted.\nPlease proceed to pay!')
                return redirect('search_properties_page')
        if(applications[i]['property_id'] == id and applications[i]['status'] == 'PENDING'):
            if(applications[i]['interested_user'] == username):
                messages.info(request, 'Pending Request Already Exists')
                return redirect('search_properties_page')
            
    # Now, we've to add this pending request for the given property.
    application = PropertyApplications.objects.create(property_id = id, interested_user = username)
    application.save()
    messages.info(request, 'Application Sent Successfully!')
    return redirect('search_properties_page')

def display_property_applications(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
    if(username is None):
        return redirect('/login')

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
        return redirect('/my_properties')
    
    # If pending requests exist:
    return render(request, 'display_property_applications.html', {'applications':current_applications})

def reject_property_application(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
    if(username is None):
        return redirect('/login')
    
    # fetching the object
    current_application = PropertyApplications.objects.get(id = id)
    current_property = current_application.property_id
    # Changing the request's status
    current_application.status = 'REJECTED'
    current_application.save()
    messages.info(request, 'Succesfully Updated Request')
    
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

def accept_property_application(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
    if(username is None):
        return redirect('/login')
    
    # fetching the object
    current_application = PropertyApplications.objects.get(id = id)
    current_property = current_application.property_id

    # PAYMENT GATEWAY & EKYC NEEDS TO PERFORMED HERE

    # Changing the current request's status
    current_application.status = 'ACCEPTED'
    current_application.save()
    messages.info(request, 'Succesfully Updated Request')
    
    # Rejecting all other pending requests.
    applications = PropertyApplications.objects.filter(property_id=current_property, status='PENDING')
    for application in applications:
        application.status = 'REJECTED'
        application.save()
    
    messages.info(request, "Application Accepted!\n Please Wait for Payment.")
    return redirect('my_properties_page')

def payment_gateway(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
            return redirect('/')
    if(username is None):
        return redirect('/login')
    
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
        required_amount = 12 * property_object.price
    else:
        required_amount = property_object.price
    print("REQUIRED_AMOUNT: ", required_amount, "\nBALANCE AVAILABLE: ", current_user_balance)

    if(required_amount > current_user_balance):
        messages.info(request, "INSUFFICIENT BALANCE!")
        return redirect('search_properties_page')
    
    payment_contract_details = {'price': required_amount, 'balance':current_user_balance, 'property_id':current_property_id,
                                'application_id':current_application.id, 'date_of_contract': date.today(), 
                                'post_balance': current_user_balance-required_amount}
    if(property_type.lower == 'rent'):
        payment_contract_details['duration'] = '12 Months' 
    print(payment_contract_details)
    return render(request, 'payment_gateway.html', {'contract': payment_contract_details})

def process_payment(request, id):
    username = request.session.get('username')
    if(request.session.get('email_kyc') is None or request.session.get('password_kyc') is None):
        return redirect('/')
    if(username is None):
        return redirect('/login')
    
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
        required_amount = 12 * property_object.price
    else:
        required_amount = property_object.price
    # print("REQUIRED_AMOUNT: ", required_amount, "\nBALANCE AVAILABLE: ", current_user_balance)
        # Updating the balance and saving the database. 
    current_user.balance = current_user_balance - required_amount
    current_user.save()

    seller = AppUser.objects.filter(username = property_object.owner)[0]
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

    messages.info(request, "Transaction SUCCESSFUL")
    return redirect('search_properties_page')