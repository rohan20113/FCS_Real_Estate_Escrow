from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import AppUser
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.views.decorators.csrf import csrf_exempt
import hashlib
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
        return render(request, 'dashboard.html', {'user': current_user})
        
def dashboard_user_list(request):
    users = AppUser.objects.all()
    return render(request, 'user_list.html', {'users':users})