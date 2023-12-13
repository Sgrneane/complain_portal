from django.shortcuts import render, HttpResponse,redirect,get_list_or_404, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage,EmailMultiAlternatives,send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import get_user_model
from social_core.exceptions import AuthAlreadyAssociated
from .models import CustomUser
from .forms import SignupForm, EditUserForm
from .validation import handle_signup_validation


def signup(request):
    """For creating regular users."""
    if request.method=='POST':
        form = SignupForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            phone = str(form.cleaned_data['phone_number'])
            # password = form.cleaned_data['password']
            
            if not handle_signup_validation(request, email, username, phone):
                return redirect('account:signup')
            User = get_user_model()
            User.objects.create_user(**form.cleaned_data)
            return redirect(reverse('account:login'))
        else:
            messages.error(request, 'User not created! Please fill the form with correct data!')
    else:
        form = SignupForm()
    return render(request, 'account/signup.html')

 
def login_user(request):
    if(request.method == 'POST'):
        email=request.POST['email']
        password=request.POST['password']
        try:
            user=authenticate(request,username=email, password=password)
            if user is not None:
                login(request,user)
                return redirect(reverse('management:user_dashboard'))
            else:
                messages.error(request, 'Incorrect Username or Password!')
                return redirect('account:login')
        except AuthAlreadyAssociated:
            # Handle the case where the Google account is already associated with another account
            return redirect(reverse('management:user_dashboard'))
    else:
        return render(request,'account/login.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect(reverse('management:index'))

def all_user(request):
    users=CustomUser.objects.filter(role=1)
    admin_users=CustomUser.objects.exclude(role = 1)
    context={
        'users': users,
        'admin_users': admin_users,
    }
    return render(request,'account/all_userlist.html',context)
def admin_users(request):
    admin_users=CustomUser.objects.exclude(role = 1)
    context={
        'admin_users': admin_users,
    }
    return render(request,'account/admin_userlist.html',context)
def view_user(request,id):
    user=get_object_or_404(CustomUser, id=id)
    context={
        'user': user
    }
    return render(request,'account/view_user.html',context)




def create_admin(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        role = int(request.POST.get('role'))
        if form.is_valid():            
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            phone = str(form.cleaned_data['phone_number'])
            password = form.cleaned_data['password']
            
            if not handle_signup_validation(request, email, username,phone):
                return redirect('account:create_admin')
            User = get_user_model()
            User.objects.create_user(
                role=role,  
                **form.cleaned_data
            )
            return redirect(reverse('account:admin_user'))
        else:
            print("hello")
            messages.error(request, 'User not created! Please fill the form with correct data!')
    else:
        form = SignupForm()
    return render(request,'account/create_admin.html')


def edit_user(request,id):
    user = get_object_or_404(CustomUser, id=id)
    
    if request.user.id != user.id and request.user.role != 3:  #allows users to update their own details only while allowing admin to update other users details too
        messages.error(request, 'Cannot Access!')
        return redirect('edit-user', id=request.user.id)
    
    if request.method == 'POST':
        print()
        form = EditUserForm(request.POST, instance=user)
        role = int(request.POST.get('role'))
        email = request.POST.get("email")
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(email,username)
        if CustomUser.objects.exclude(id=user.id).filter(username=username).first():
            messages.info(request, f'User with this username "{username}" already exists')
            return redirect('main:my_account')
        
        if CustomUser.objects.exclude(id=user.id).filter(email=email).first():
            messages.info(request, f'User with this email "{email}" already exists')
            return redirect('main:my_account')
    
        if form.is_valid():
            form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['username']
            user.phone_number = str(form.cleaned_data['phone_number'])
            user.first_name=form.cleaned_data['first_name']
            user.last_name=form.cleaned_data['last_name']
            user.password=make_password(password)
            user.role=role
            user.save()
            if request.user.role == 3:
                print("hello")
                messages.success(request, "User Details Updated Successfully")
                return redirect('account:admin_user')
            else:
                messages.success(request, "Details Updated Successfully")
                return redirect('account:my_account')
        else:
            print(form.errors)
            messages.error(request, "Please fill the form with correct data")
    else:
        form = EditUserForm()
        
    context = {'user': user}
    return render(request, 'account/edit_user.html', context)

def my_account(request):
    return render(request,'account/my_account.html')

def delete_user(request, id):
    user=get_object_or_404(CustomUser,id=id)
    print(user.email)
    user.delete()
    return redirect(reverse('account:admin_user'))

"""
def change_password(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('password')
        retype_new_password = request.POST.get('retype_password')
        
        if current_password == '' or new_password == '' or retype_new_password == '':
            messages.error(request, "Please fill all the fields")
            return redirect('account:change_password')
        
        if not user.check_password(current_password):
            messages.error(request, "Incorrect Current Password")
            return redirect('account:change_password')
            
        if new_password != retype_new_password:
            messages.error(request, "New Passwords didn't match")
            return redirect('account:change_password')
        
        if current_password == new_password:
            messages.error(request, "New Password should not be same as Current Password!")
            return redirect('account:change_password')
        
        user.set_password(new_password)
        user.save()
        #update_session_auth_hash(request, user_object) #user is not logged out after changing password
        messages.success(request, "Password Changed Successfully! Login with new password")
        return redirect('account:login_user')
        
    context = {'user': user}
    return render(request, 'account/change_password.html', context)

def admin_can_change_password(request,id):
    user_to_change_password = get_object_or_404(CustomUser, id=id)
    if request.method == 'POST':
        new_password = request.POST.get('password')
        retype_new_password = request.POST.get('retype_password')
        if new_password != retype_new_password:
            messages.error(request, "New Passwords didn't match")
            return redirect('account:admin_can_change_password',id=id)
        user_to_change_password.set_password(new_password)
        user_to_change_password.save()
        update_session_auth_hash(request, user_to_change_password)
        messages.success(request, "Password Changed Successfully!")
        return redirect('main:all_user')
    context = {'user': user_to_change_password}
    return render(request, 'account/admin_can_change_password.html', context)

def forget_password(request):
    if request.method=='POST':
        user_email=request.POST.get('user_email')
        subject="Hello Prasashan OTP alert!!"
        message=f"Please use given OTP to reset your password."
        msg = EmailMessage(subject,message, to=(user_email))
        msg.send()
        return HttpResponse("Email for OTP sent successfully.")

    return render(request,'account/forget-password.html')

# def generate_otp():
#     otp = ''.join(random.choices('0123456789', k=6))
#     return otp
    
# def otp_verify(request):
#     subject = 'Your OTP Code'
#     message = f'Your OTP code is:'
#     recipient_list = 

#     send_mail(subject, message,recipient_list)

def index(request):
    return render(request, 'account/create_admin.html')"""
