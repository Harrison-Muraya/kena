from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from . models import Todolist, Item, Coin, Wallet,CustomUser, Billing, Transaction, Block, PendingTransaction
from . import forms 
from . import blockchain
from . import uidgenerator
from datetime import timezone
# from Crypto.PublicKey import RSA

# constant variables
DIFFICULTY = 4  # Difficulty level for mining blocks
FEE = 10  # Transaction fee for sending coins


# generate private key and public key
def generate_keys():
    from Crypto.PublicKey import RSA
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def home(request):
    print('hellow')
    return render(request, 'coin/home.html')

def create(request):  
    if request.method == 'POST':
        form = forms.CreateNewlist(request.POST)
        if form.is_valid():
            # Process the form data
            name = form.cleaned_data['name']
            check_box = form.cleaned_data['check_box']
            t = Todolist(name=name, check_box=check_box)
            t.save()
            # Here you can save the data to the database or perform other actions
            return HttpResponseRedirect('/coin/home/')
            # return HttpResponse(f"List '{name}' created with checkbox {'checked' if check_box else 'not checked'}")
    else:
        form = forms.CreateNewlist()
    return render(request, 'coin/create.html', {'form': form})

def list(request):
    todolists = Todolist.objects.all()
    items = Item.objects.all()  # Assuming you want to list all items
    return render(request, 'coin/list.html', {'todolists': todolists, 'items': items})

def show(request, id):
    todolist = Todolist.objects.get(id=id)
    items = todolist.item_set.all()
    # return HttpResponse(f"List: {todolist.name} - Checkbox: {'Checked' if todolist.check_box else 'Not Checked'}<br>Items: {', '.join([item.name for item in items])}")

    return render(request, 'coin/show.html', {'todolist': todolist, 'items': items})

def register(request):
    if request.method == 'POST':
        # Handle form submission
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            # Generate keys
            private_key, public_key = generate_keys()
            # Save user with public key
            user = form.save(commit=False)  
            user.public_key = public_key.decode('utf-8')
            user.private_key = private_key.decode('utf-8')
            user.save()
            form.save()
            login(request, form.save())
            return redirect('dashboard')
    else:
        # Display registration form
        form = forms.RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

#Dashboard view
def dashboard(request):
    if request.user.is_authenticated:       
        user = request.user
        # print("Private Key:", user.private_key)
        # print("Public Key:", user.public_key)

        form = forms.WalletForm()
        if request.method == 'POST':
            form = forms.WalletForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                walletType = form.cleaned_data['walletType']
                password = make_password(form.cleaned_data['password']) 

                data = {
                    "name": name,
                    "password": form.cleaned_data['password'],
                    "walletType": walletType,
                    "private_key": user.private_key,
                }

                hasher = blockchain.CalculateHash(data)
                hash_value = hasher.calculate()

                # Create a new wallet instance
                wallet = Wallet(
                    user=request.user,
                    name=name,
                    amount= 0,  # Initial amount can be set to 0 or any other value
                    value= 0,  # Initial value can be set to 0 or any other value
                    hash=hash_value,
                    password=password,
                    wallettype=walletType,
                )
                wallet.save()
                return redirect('dashboard')
        else:
            form = forms.WalletForm()
            wallets = Wallet.objects.filter(user=request.user)
        return render(request, 'coin/dashboard.html', {'user': request.user, 'form': form, 'wallets': wallets})
    else:
        return redirect('login')

#send kena
def send_kena(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = forms.SendKenaForm(request.POST or None, user=request.user)

            if form.is_valid():
                sender = request.user
                receiver = form.cleaned_data['receiver']
                amount = form.cleaned_data['amount']
                wallet = form.cleaned_data['wallet']
                selected_wallet = form.cleaned_data['wallet']
                password = form.cleaned_data['password'] 

                # sender_wallet = Wallet.objects.filter(user=sender)
                # print("Sender wallet:", sender_wallet)

                # print("Sender primary key:", sender.private_key)
                # Generate to cheack if the wallet belongs to the user
                data = {
                    "name": selected_wallet.name,
                    "password": password,
                    "walletType": selected_wallet.wallettype,
                    "private_key": sender.private_key,
                }
                hasher = blockchain.CalculateHash(data) 
                genrated_hash = hasher.calculate()
                 # Validate wallet ownership
                if selected_wallet.hash != genrated_hash:
                    form.add_error('wallet', 'This wallet does not belong to you.')
                    return render(request, 'coin/send_kena.html', {'form': form})
                

                #  check if the sender wallet exists
                try:
                    sender_wallet = Wallet.objects.filter(user=sender)
                    print("Sender wallet:", sender_wallet)
                except Wallet.DoesNotExist:
                    form.add_error(None, "Sender wallet not found.")
                    return render(request, 'coin/send_kena.html', {'form': form})
                
                # check if the receiver exists
                try:
                    recepient= CustomUser.objects.filter(username=receiver)
                    if not recepient.exists():
                        form.add_error('receiver', 'Receiver does not exist')
                        return render(request, 'coin/send_kena.html', {'form': form})
                    receiver_wallet = Wallet.objects.filter(user=recepient.first())
                    if not receiver_wallet.exists():
                        form.add_error('receiver', 'Receiver has no wallet associated with their account')
                        return render(request, 'coin/send_kena.html', {'form': form})
                   
                except Wallet.DoesNotExist:
                    form.add_error('receiver', 'Receiver wallet does not exist')
                    return render(request, 'coin/send_kena.html', {'form': form})
                
            
                # creating a new billing instance
                billing = Billing(
                    user=sender,
                    wallet=form.cleaned_data['wallet'],
                    amount=amount,  # Total amount including fee
                    fee=FEE,  # Transaction fee
                    total=amount + FEE,  # Total amount including fee
                    uid=uidgenerator.generate_code(),  # Generate a unique identifier
                    type='send',
                )
                billing.save()

                # Get the billing ID
                # billing_id = billing.id
                # print("Billing ID:", billing_id)  # or use it however you want

                # Create a new debit PendingTransaction instance
                pending_transaction = PendingTransaction(
                    billing=billing,
                    sender=sender,
                    receiver=recepient.first(),
                    amount=amount - FEE,  # Amount minus the fee
                    type='send',
                    gateway='kena',
                    credit=0,  # Assuming credit is 0 for debit transactions for the sender
                    debit=amount,
                )
                pending_transaction.save()

                # Create a new credit PendingTransaction instance for the receiver
                pending_transaction_receiver = PendingTransaction(
                    billing=billing,
                    sender=sender,
                    receiver=recepient.first(),
                    amount=amount - FEE,  # Amount minus the fee
                    type='receive',
                    gateway='kena',
                    credit=amount,  # Assuming credit is the amount for the receiver
                    debit=0,  # Assuming debit is 0 for credit transactions for the receiver
                )
                pending_transaction_receiver.save()

                # Create a new credit PendingTransaction instance for the fee
                transactionc= CustomUser.objects.filter(username='harris').first()
                pending_transaction_fee = PendingTransaction(
                    billing=billing,
                    sender=sender,
                    receiver= transactionc,  # Assuming receiver is a system account or fee collector
                    amount= FEE,  # Fee amount
                    type='fee', 
                    gateway='kena',
                    credit=FEE,  # Assuming credit is the fee amount
                    debit=0,  # Assuming debit is 0 for fee transactions
                )
                pending_transaction_fee.save()

                # Update wallet balances, etc. as needed
                return redirect('dashboard')
        else:
            form = forms.SendKenaForm(user=request.user)
        return render(request, 'coin/send_kena.html', {'form': form})

 # Logout view   
def logout_view(request):
    logout(request)
    return redirect('home')