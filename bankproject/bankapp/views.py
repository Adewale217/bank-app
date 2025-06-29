import decimal
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as loginAuth, logout as logoutAuth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Customer
from django.contrib import messages
# Create your views here.
error = None
success = None
def signup(request):
    error = None
    if request.method =='POST':
        username = request.POST.get("username")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2 :
            return render(request, 'signup.html', {'error': "pssword dose not match"})

        if len(password1) < 8 :
            return render(request, 'signup.html', {'error': "passwords length must be more than 8"})

        if User.objects.filter(username = username).exists():
            return render(request, 'signup.html', {'error': "user already exist"})

        if Customer.objects.filter(phone = phone).exists():
            return render(request, 'signup.html', {'error': "phone number has been registered before"})

        if User.objects.filter(email = email).exists():
            return render(request, 'signup.html', {'error': "this Email has already been used"})

        user = User.objects.create_user(username = username, email = email, password = password1)
        user.save()
        Customer.objects.create(user=user, phone= phone)
        return redirect("login")
    return render(request, 'signup.html',{'error':error})

def login(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get('password')

        user = authenticate(request, username=username, phone = phone, email = email, password=password)
        if user is not None:
            loginAuth(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'invalid credentials'})

    return render(request, 'login.html')

@login_required
def dashboard(request):
    user = request.user
    customer = Customer.objects.get(user=user)

    # if not hasattr(user, 'balance') or user.balance is None:
    #     user.balance = 5000
    #     user.save()

    context = {
        'username': user.username,
        'balance': customer.balance if customer else 1000,
    }

    return render(request, 'dashboard.html', context)



@login_required
def transfer(request):
    if request.method == "POST":
        recipient_info = request.POST.get("recipient")
        amount = request.POST.get("amount")
        password = request.POST.get("password")
        

        if not recipient_info or not amount or not password:
            messages.error(request, "Please fill in all fields.")
            return redirect("transfer")


        user = request.user
        if not user.check_password(password):
            messages.error(request, "Incorrect password. Please try again.")
            return redirect("transfer")

        try:
            amount = decimal.Decimal(amount)
            if amount < 100 or amount > 10000:
                messages.error(request, "Amount must be between $100 and $1000.")
                return redirect("transfer")
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return redirect("transfer")

        customer = Customer.objects.get(user= user)

        if decimal.Decimal(customer.balance) < amount:
            messages.error(request, "Insufficient balance.")
            return redirect("transfer")


        recipient_user = User.objects.filter(username=recipient_info).first() or Customer.objects.filter(phone=recipient_info).first()
        if not recipient_user :
            messages.error(request, "User not found.")
            return redirect("transfer")
        recipient = Customer.objects.get(user=recipient_user) 
        
        if not recipient:
            messages.error(request, "This is not a reciepent found in thisapplication.")
            return redirect("transfer")

        print(f"Before Transfer - Sender: {customer.balance}, Receiver: {recipient.balance}")
        customer.balance = decimal.Decimal(customer.balance) - amount
        customer.save(update_fields=["balance"])  # Ensure balance field is updated

        recipient.balance = decimal.Decimal(recipient.balance) + amount
        recipient.save(update_fields=["balance"])  # Ensure balance field is updated
        print(f"After Transfer - Sender: {customer.balance}, Receiver: {recipient.balance}")



        messages.success(request, f"Transfer successful! You sent ${amount} to {recipient.phone}.")
        messages.success(request, f"{recipient.phone} has received ${amount}.")

        return redirect("dashboard")

    return render(request, "transfer.html")



@login_required
def top_up(request):
    if request.method == "POST":
        username = request.POST.get("username")
        amount = request.POST.get("amount")
        password = request.POST.get("password")

        if not amount or not password:
            messages.error(request, "Please enter an amount and confirm your password.")
            return redirect("top_up")

        user = request.user

        if not user.check_password(password):
            messages.error(request, "Incorrect password. Please try again.")
            return redirect("top_up")

        try:
            amount = decimal.Decimal(amount)
            if amount < 100 or amount > 10000:
                messages.error(request, "Amount must be between $100 and $10,000.")
                return redirect("top_up")
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return redirect("top_up")

        customer = Customer.objects.get(user=user)
        
        # Update balance safely
        customer.balance = decimal.Decimal(customer.balance) + amount
        customer.save(update_fields=["balance"])

        messages.success(request, f"Top-up successful! Your new balance is ${customer.balance}.")
        return redirect("dashboard")

    return render(request, "top_up.html")




def signout(request):
    if request.user.is_authenticated:
        logoutAuth(request)
        messages.success(request, "You have successfully logged out.")
        return redirect('login')
    return render(request, 'dashboard.html')

