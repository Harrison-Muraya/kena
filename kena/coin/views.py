from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from . models import Todolist, Item, Coin, Wallet,CustomUser, Billing, Transaction, Block, PendingTransaction, MpesaTransaction
from . import forms 
from . import blockchain
from . import uidgenerator
from . import lipaNaMpesa
# from datetime import timezone
import time
import json
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


from django.urls import reverse
from decimal import Decimal


# constant variables
DIFFICULTY = 4  # Difficulty level for mining blocks
# FEE = 10  # Transaction fee for sending coins


# # generate private key and public key
# def generate_keys():
#     from Crypto.PublicKey import RSA
#     key = RSA.generate(2048)
#     private_key = key.export_key()
#     public_key = key.publickey().export_key()
#     return private_key, public_key

# check key validity
def checkKey(data):
    try:
       key = RSA.import_key(data)
       return key
    except ValueError:
       return print("Invalid private key")

# Generate signature for transaction
def generate_signature(key, transaction_obj):
    try:
    # Extract and structure data
        data_to_sign = {
            "billing": transaction_obj["billing"],
            "uid": transaction_obj["uid"],
            "sender": transaction_obj["sender"],
            "amount": float(transaction_obj["amount"]),
        }

        transaction_bytes = json.dumps(data_to_sign, sort_keys=True).encode('utf-8')
         # Hash the message first
        h = SHA256.new(transaction_bytes)

        # Sign using PKCS#1 v1.5
        signature = pkcs1_15.new(key).sign(h)

        return signature.hex() 

    except Exception as e:
        print(f"Error generating signature: {str(e)}")
        return None
    
# Verify signature for transaction
def verify_signature(key, transaction_obj, signature):
    try:
        # Extract and structure data
        data_to_verify = {
            "billing": transaction_obj["billing"],
            "uid": transaction_obj["uid"],
            "sender": transaction_obj["sender"],
            "amount": float(transaction_obj["amount"]),
        }

        # Convert data to JSON bytes with sorted keys
        transaction_bytes = json.dumps(data_to_verify, sort_keys=True).encode('utf-8')

        # Create SHA-256 hash of the transaction
        hash_obj = SHA256.new(transaction_bytes)

        # Import public key if it's a string
        if isinstance(key, str):
            key = RSA.import_key(key)

        # Decode the hex signature
        signature_bytes = bytes.fromhex(signature)

        # Verify the signature
        pkcs1_15.new(key).verify(hash_obj, signature_bytes)

        return True

    except (ValueError, TypeError):
        return False

# Home view            
def home(request):
    blocks = Block.objects.all()
    pendingTransaction = PendingTransaction.objects.all().order_by('-timestamp')  # Fetch all transactions, ordered by most recent
    return render(request, 'coin/home.html', {'blocks': blocks, 'pendingTransaction': pendingTransaction})

# API endpoint to get the latest 5 pending transactions
def get_pending_transactions(request):
    txns = PendingTransaction.objects.all().order_by('-timestamp')[:5]
    data = [
        {
            'hash': t.hash,
            'amount': str(t.amount),
            'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        } for t in txns
    ]
    return JsonResponse({'transactions': data})
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

# User registration view
def register(request):

    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            # Create user object but don’t commit yet
            user = form.save()

            # Save final user
            user.save()

            # Log the user in
            login(request, user)    
            return redirect('dashboard')
    else:
        form = forms.RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

# Function to send verification email
def send_verification_email(user, request):
    """Send email verification to user"""
    try:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        verification_link = request.build_absolute_uri(
            reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
        )
        
        subject = 'Verify your Kena account'
        message = f'''
        Hi {user.first_name},
        
        Thank you for registering with Kena! Please click the link below to verify your email address:
        
        {verification_link}
        
        If you didn't create this account, please ignore this email.
        
        Best regards,
        The Kena Team
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")

FEE = Decimal('10.0')  # Transaction fee for sending coins

# Dashboard view
def dashboard(request):
    if request.user.is_authenticated:       
        user = request.user
        # print("Private Key:", user.private_key)
        # print("Public Key:", user.public_key)
        # -------------------------------------------------------------------------------------------
        # Handle Send Kena form submission via AJAX
        if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = forms.SendKenaForm(request.POST, user=request.user)

            # print('form Data',form)  # Debug: Print form errors if any
            
            if form.is_valid():
                sender = request.user
                # receiver = form.cleaned_data['receiver']
                walletHash = form.cleaned_data['walletHash']
                amount = form.cleaned_data['amount']
                selected_wallet = form.cleaned_data['wallet']
                password = form.cleaned_data['password']
                
                # Find receiver by walletHash
                try:
                    sender_wallet = Wallet.objects.filter(user=sender)
                    if not sender_wallet.exists():
                        return JsonResponse({'success': False, 'error': 'Sender wallet not found.'})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})

                # Validate wallet ownership
                data = {
                    "name": selected_wallet.name,
                    "password": password,
                    "walletType": selected_wallet.wallettype,
                    "private_key": checkKey(sender.private_key).export_key().decode()
                }
                hasher = blockchain.CalculateHash(data) 
                generated_hash = hasher.calculate()
            
                if selected_wallet.hash != generated_hash:
                    return JsonResponse({'success': False, 'error': 'This wallet does not belong to you or password is incorrect.'})
                
                # print('wallet ownership validated')
                # Check if wallet has sufficient balance
                if selected_wallet.amount < (amount + FEE):
                    error_msg = f'Insufficient balance. You have {selected_wallet.amount} KENA but need {amount + FEE} KENA (including fee).'                    
                    return JsonResponse({'success': False, 'error': error_msg})
                    
                # Check if wallet has sufficient balance
                if selected_wallet.amount < (amount + FEE):
                    error_msg = f'Insufficient balance. You have {selected_wallet.amount} KENA but need {amount + FEE} KENA (including fee).'
                    return JsonResponse({'success': False, 'error': error_msg})
                    

                # Check if the receiver exists
                try:
                    # recipient = CustomUser.objects.filter(username=receiver)                    
                    # if not recipient.exists():
                    receiver_wallet = Wallet.objects.filter(hash=walletHash).first()
                    # print('Recipient wallet exicist:', receiver_wallet)
                    if not receiver_wallet:
                        return JsonResponse({'success': False, 'error': 'Receiver does not exist'})
                    
                    # receiver_wallet = Wallet.objects.filter(user=recipient.first())
                    receiver_wallet_user = receiver_wallet.user
                    # print('receiver wallet User is: ', receiver_wallet)
                    # print('receiver wallet hash is: ', receiver_wallet.hash)
                    

                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
                # print('receiver wallet found')
                # Prevent sending to yourself
                if receiver_wallet_user == sender:
                    return JsonResponse({'success': False, 'error': 'Cannot send to your own wallet'})
                
                # print('not sending to self')

                # Creating billing instance
                billing = Billing(
                    user=sender,
                    wallet=selected_wallet,
                    amount=amount + FEE,
                    fee=FEE,
                    total=amount + FEE,
                    uid=uidgenerator.generate_code(),
                    type='send',
                )
                billing.save()

                # print("Billing created with ID:", billing.id)
                # Create pending transactions (debit, credit, fee)
                # 1. Debit transaction for sender
                pending_transaction = PendingTransaction(
                    billing=billing,
                    wallet=selected_wallet,
                    sender=sender,
                    # receiver=recipient.first(),
                    amount=billing.amount,
                    type='send',
                    gateway='kena',
                    credit=0,
                    debit=billing.amount,
                    walletHash = selected_wallet.hash,
                    signature=generate_signature(checkKey(sender.private_key), {
                        "billing": billing.id,
                        "uid": billing.uid,
                        "sender": sender.username,
                        "amount": billing.amount,
                    })
                )
                pending_transaction.save()

                # print("Pending transaction for sender created with ID:", pending_transaction.id)

                # 2. Credit transaction for receiver
                pending_transaction_receiver = PendingTransaction(
                    billing=billing,
                    wallet=receiver_wallet,
                    sender=sender,
                    # receiver=recipient.first(),
                    amount=billing.amount - FEE,
                    type='receive',
                    gateway='kena',
                    credit=amount,
                    debit=0,
                    walletHash = receiver_wallet.hash,
                    signature=generate_signature(checkKey(sender.private_key), {
                        "billing": billing.id,
                        "uid": billing.uid,
                        "sender": sender.username,
                        "amount": billing.amount - FEE,
                    })
                )
                pending_transaction_receiver.save()

                # print("Pending transaction for receiver created with ID:", pending_transaction_receiver.id)

                # Transaction for fee (credit to system)
                transactionc = CustomUser.objects.filter(username='harris').first()
                pending_transaction_fee = PendingTransaction(
                    billing=billing,
                    # wallet=fee_wallet,
                    sender=sender,
                    receiver=transactionc,
                    amount=FEE,
                    type='fee', 
                    gateway='kena',
                    credit=FEE,
                    debit=0,
                    signature=generate_signature(checkKey(sender.private_key), {
                        "billing": billing.id,
                        "uid": billing.uid,
                        "sender": sender.username,
                        "amount": FEE,
                    })
                )
                pending_transaction_fee.save()
                # print("Pending transaction for fee created with ID:", pending_transaction_fee.id)

                return JsonResponse({'success': True, 'message': 'Transaction sent successfully!'})
            else:
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(e) for e in error_list]
                return JsonResponse({'success': False, 'errors': errors})
        # -------------------------------------------------------------------------------------------
        # check if user has 4 wallets if yes disable add wallet option
        wallet_count = Wallet.objects.filter(user=request.user).count()
        if wallet_count >= 5:
            messages.error(request, 'You have reached the maximum limit of 4 wallets.')
            return render(request, 'coin/dashboard.html', {'user': request.user, 'wallet_limit_reached': True})
        
        form = forms.WalletForm()
        if request.method == 'POST':
            form = forms.WalletForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                walletType = form.cleaned_data['walletType']
                password = make_password(form.cleaned_data['password']) 

                # try:
                    # key = RSA.import_key(user.private_key)
                # except ValueError:
                #     print("Invalid private key")

                data = {
                    "name": name,
                    "password": form.cleaned_data['password'],
                    "walletType": walletType,
                    "private_key": checkKey(user.private_key).export_key().decode()
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
            # wallets = Wallet.objects.filter(user=request.user)
            wallets = Wallet.objects.filter(user=request.user, status=1).order_by('created_at')
            send_form = forms.SendKenaForm(user=request.user)
            # context = {
            #         'wallets': wallets,
            #     }
        return render(request, 'coin/dashboard.html', {'user': request.user, 'form': form, 'wallets': wallets, 'send_form': send_form})
    else:
        return redirect('login')
    
#transaction views
def transactions(request):
    transactions = Block.objects.all().order_by('-timestamp')  # Fetch all transactions, ordered by most recent
    print(transactions)
    return render(request, 'coin/transactions.html', {'transactions': transactions})

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

                #  check if the sender wallet exists
                try:
                    sender_wallet = Wallet.objects.filter(user=sender)
                    print("Sender wallet:", sender_wallet)
                except Wallet.DoesNotExist:
                    form.add_error(None, "Sender wallet not found.")
                    return render(request, 'coin/send_kena.html', {'form': form})

                # print("Sender primary key:", sender.private_key)
                # Generate to cheack if the wallet belongs to the user
                data = {
                    "name": selected_wallet.name,
                    "password": password,
                    "walletType": selected_wallet.wallettype,
                    "private_key":  checkKey(sender.private_key).export_key().decode()
                }
                hasher = blockchain.CalculateHash(data) 
                genrated_hash = hasher.calculate()

                 # Validate wallet ownership
                if selected_wallet.hash != genrated_hash:
                    form.add_error('wallet', 'This wallet does not belong to you.')
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
                    amount=amount,  # Total amount including no fee
                    fee=FEE,  # Transaction fee
                    total=amount + FEE,  # Total amount including fee
                    uid=uidgenerator.generate_code(),  # Generate a unique identifier
                    type='send',
                )
                billing.save()

               # Prepare transaction data for signing
                # transaction_data = {
                #     "billing": billing.id,
                #     "uid": billing.uid,
                #     "sender": sender.username,
                #     "amount": billing.amount,
                # }
                # signature = generate_signature(checkKey(sender.private_key), transaction_data)          

                # Create a new debit PendingTransaction instance
                pending_transaction = PendingTransaction(
                    billing=billing,
                    sender=sender,
                    receiver=recepient.first(),
                    amount=billing.amount,  # Amount minus the fee
                    type='send',
                    gateway='kena',
                    credit=0,  # Assuming credit is 0 for debit transactions for the sender
                    debit=billing.amount,
                    signature=generate_signature(checkKey(sender.private_key), {
                            "billing": billing.id,
                            "uid": billing.uid,
                            "sender": sender.username,
                            "amount": billing.amount,
                        }) # Store the signature as hex string
                    # signature=signature.hex() # Store the signature as hex string
                )
                pending_transaction.save()

                # Create a new credit PendingTransaction instance for the receiver
                pending_transaction_receiver = PendingTransaction(
                    billing=billing,
                    sender=sender,
                    receiver=recepient.first(),
                    amount=billing.amount - FEE,  # Amount minus the fee
                    type='receive',
                    gateway='kena',
                    credit=amount,  # Assuming credit is the amount for the receiver
                    debit=0,  # Assuming debit is 0 for credit transactions for the receiver
                    signature=generate_signature(checkKey(sender.private_key), {
                            "billing": billing.id,
                            "uid": billing.uid,
                            "sender": sender.username,
                            "amount": billing.amount - FEE,
                        }) # Store the signature as hex string

                    # signature=signature.hex() if signature else None  # Store the signature as hex string
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
                    signature=generate_signature(checkKey(sender.private_key), {
                            "billing": billing.id,
                            "uid": billing.uid,
                            "sender": sender.username,
                            "amount": FEE,
                        }) # Store the signature as hex string
                    # signature=signature.hex() if signature else None  # Store the signature as hex string
                )
                pending_transaction_fee.save()

                # Update wallet balances, etc. as needed
                return redirect('dashboard')
        else:
            form = forms.SendKenaForm(user=request.user)
        return render(request, 'coin/send_kena.html', {'form': form})

 # Logout view   

# mine kena
def mine_kena(request):
    if request.user.is_authenticated:
        transactions = PendingTransaction.objects.all()

        return render(request, 'coin/mine_kena.html',{'transactions': transactions})
    else:
        return redirect('login')
   
# returns a json file with block data
def get_mine_data(request):
    # pending = PendingTransaction.objects.all()[:10]
    pending = PendingTransaction.objects.all()
    # print(pending)
    tx_data = []

    for tx in pending:
        # validate Pending transaction signature
        try:
            transaction_data = {
                    "billing": tx.billing.id,
                    "uid": tx.billing.uid,
                    "sender": tx.sender.username,
                    "amount": tx.amount,
                }
            
            verifiedSignature = verify_signature(checkKey(tx.sender.public_key),transaction_data,tx.signature)  
            if(verifiedSignature):                    
                # print(f"Amount: { tx.amount} verified: {verifiedSignature}, data: {transaction_data}")
                tx_data.append({
                    "sender": tx.sender.username,
                    # "receiver": tx.receiver.username,
                    "amount": float(tx.amount),
                    "hash": tx.hash
                })                  
            else:
                pass
                # print(f"Amount: { tx.amount} failed verification -- verifiedsig: {verifiedSignature}, data: {transaction_data}")
                           
        except Exception as e:
            print(e)

    previous_block = Block.objects.order_by('-height').first()
    previous_hash = previous_block.hash if previous_block else '0' * 64
    height = previous_block.height + 1 if previous_block else 1

    return JsonResponse({
        "height": height,
        "previous_hash": previous_hash,
        "transactions": tx_data,
        "timestamp": time.time(),
    })

#buy kena via mpesa
def buy_kena(request):
     if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')
        method = data.get('method')
        phone = data.get('phoneNumber')
        user = request.user

        if method == 'M-Pesa':
            # Here you would integrate with M-Pesa API to process the payment
            # For demonstration, we'll just return a success message
            response = lipaNaMpesa.lipaNaMpesaOnline(phone, amount)
           
            if response.get('ResponseCode') != '0':
                return JsonResponse({'success': False, 'message': 'M-Pesa payment initiation failed. Please try again.'})
            else:
                # creating a new billing instance
                billing = Billing(
                    user=user,
                    # wallet=wallet,
                    amount=amount,  # Total amount including no fee
                    fee=0,  # Transaction fee
                    total=amount,  # Total amount including fee
                    uid=uidgenerator.generate_code(),  # Generate a unique identifier
                    type='buykena',
                )
                billing.save()

                # mpesa transaction
                mpesaTransaction = MpesaTransaction(
                    Billing=billing,
                    type = 'buykena',                 
                    MerchantRequestID=response.get('MerchantRequestID'),
                    CheckoutRequestID=response.get('CheckoutRequestID'),                    
                    status='Pending',
                )
                mpesaTransaction.save()
                         
            # responseData = response.json()
            # print("M-Pesa Response Data:", response.get('ResponseCode'))
            return JsonResponse({'success': True, 'message': 'M-Pesa payment initiated. Please complete the payment on your phone.', 'response': response})
        
        elif method == 'PayPal' or method == 'Stripe':
            # Integrate PayPal payment processing here
            print("PayPal payment method selected.")
            return JsonResponse({'success': True, 'message': 'PayPal payment processing is not yet implemented.'})
        
def mpesa_payment_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        checkout_request_id = data.get('CheckoutRequestID')
        try:
            mpesa_transaction = MpesaTransaction.objects.get(CheckoutRequestID=checkout_request_id)
            if mpesa_transaction.status == 'Completed':
                return JsonResponse({'success': True, 'message': 'M-Pesa payment completed successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'M-Pesa payment is still pending.'})
        except MpesaTransaction.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Transaction not found'})            

# Mpesa callback URL to handle payment confirmation
@csrf_exempt
def mpesa_callback(request):
    # data = {
    #     'Body': {
    #         'stkCallback': {
    #             'MerchantRequestID': 'ddb8-4a08-af32-c0e1ff1c640613777',
    #             'CheckoutRequestID': 'ws_CO_05122025235543715726688832', 
    #             'ResultCode': 0, 
    #             'ResultDesc': 'The service request is processed successfully.', 
    #             'CallbackMetadata': {
    #                 'Item': [
    #                     {'Name': 'Amount', 'Value': 1.0}, 
    #                     {'Name': 'MpesaReceiptNumber', 'Value': 'TL5JC06Q6W'}, 
    #                     {'Name': 'Balance', 'Value': 0.0}, 
    #                     {'Name': 'TransactionDate', 'Value': 20251205235605}, 
    #                     {'Name': 'PhoneNumber', 'Value': 254726688832}
    #                     ]
    #                 }
    #             }
    #         }
    #     }

    data = json.loads(request.body)
    if data.get('Body') is None:
        return JsonResponse({'success': False, 'message': 'Invalid callback data'})
    else:
        stkCallback = data.get('Body', {}).get('stkCallback', {})
    
        merchant_request_id = stkCallback.get('MerchantRequestID')
        
        checkout_request_id = stkCallback.get('CheckoutRequestID')
        
        result_code = stkCallback.get('ResultCode')
        result_desc = stkCallback.get('ResultDesc')
        callback_metadata = stkCallback.get('CallbackMetadata', {})
        items = callback_metadata.get('Item', [])
        amount = None
        mpesa_receipt_number = None  
    
    
        for item in items:
            if item.get('Name') == 'Amount':
                amount = item.get('Value')
            elif item.get('Name') == 'MpesaReceiptNumber':
                mpesa_receipt_number = item.get('Value')
            elif item.get('Name') == 'PhoneNumber':
                phone_number = item.get('Value')
        try:
            mpesa_transaction = MpesaTransaction.objects.get(CheckoutRequestID=checkout_request_id)
            if result_code == 0:
                mpesa_transaction.status = 'Completed'
                mpesa_transaction.transaction_id = mpesa_receipt_number
                mpesa_transaction.amount = amount
                mpesa_transaction.phone_number = phone_number
                mpesa_transaction.save()

                # Update user's Kena balance or create a credit transaction
                billing = mpesa_transaction.Billing
                user = billing.user
                wallet = Wallet.objects.filter(user=user, wallettype='primary').first()
                Wallet_hash = wallet.hash if wallet else ''
                # Create a new credit PendingTransaction instance for the purchased Kena
                pending_transaction_credit = PendingTransaction(
                    billing=billing,
                    wallet= wallet,
                    sender= user,  # No sender for purchase transactions 
                    receiver=user,
                    amount=amount,  # Amount of Kena purchased
                    type='receive',
                    gateway='mpesa',
                    credit=amount,  # Credit the purchased amount
                    debit=0,  # No debit for purchase transactions
                    walletHash = Wallet_hash,
                    signature=generate_signature(checkKey(user.private_key), {
                            "billing": billing.id,
                            "uid": billing.uid,
                            "sender": user.username,
                            "amount": billing.amount,
                        })   # No signature needed for purchase transactions
                )
                pending_transaction_credit.save()

                # Here you would typically update the user's Kena balance
                # For demonstration, we'll just print a message
                print(f"User {user.username} has successfully purchased {amount} Kena.")
                return JsonResponse({'success': True, 'message': 'M-Pesa payment completed successfully.'})
            else:
                mpesa_transaction.status = 'Failed'
                mpesa_transaction.save()
                return JsonResponse({'success': False, 'message': f'M-Pesa payment failed: {result_desc}'})
        except MpesaTransaction.DoesNotExist:
            print(f"M-Pesa transaction not found for CheckoutRequestID: {checkout_request_id}")
            return JsonResponse({'success': False, 'message': 'Transaction not found'})

# submit mined block
@csrf_exempt
def submit_block(request):

    pending = PendingTransaction.objects.all()
    # print(pending)
    tx_data = []

    for tx in pending:
        # validate Pending transaction signature
        try:
            transaction_data = {
                    "billing": tx.billing.id,
                    "uid": tx.billing.uid,
                    "sender": tx.sender.username,
                    "amount": tx.amount,
                }
            
            verifiedSignature = verify_signature(checkKey(tx.sender.public_key),transaction_data,tx.signature)  
            if(verifiedSignature):                    
                # print(f"Amount: { tx.amount} verified: {verifiedSignature}, data: {transaction_data}")
                tx_data.append({
                    "sender": tx.sender.username,
                    "receiver": tx.receiver.username,
                    "amount": float(tx.amount),
                    "hash": tx.hash
                })                  
            else:
                pass
                # print(f"Amount: { tx.amount} failed verification -- verifiedsig: {verifiedSignature}, data: {transaction_data}")
                           
        except Exception as e:
            print(e)

    previous_block = Block.objects.order_by('-height').first()
    previous_hashh = previous_block.hash if previous_block else '0' * 64
    height = previous_block.height + 1 if previous_block else 1


    data = json.loads(request.body)

    # height = data.get("height", 0)
    timestamp = data.get("timestamp", "")
    # previous_hash = data.get("previous_hash", "")
    nonce = data.get("nonce", 0)
    transactions = data.get("transactions", [])   

    # Reconstruct block
    block_data = {
        "height": height,
        "timestamp": timestamp,
        "previous_hash": previous_hashh,
        "nonce": nonce,
        "transactions": transactions,
    }
    # return JsonResponse({"message": "Block received", "block": block_data})
    # return JsonResponse({"error": f"Invalid data format: {str(e)}"}, status=400)
    calculated_hash = blockchain.CalculateHash(block_data).calculate()  
    if calculated_hash != data["hash"]:
        return JsonResponse({"error": "Invalid hash or proof"}, status=400)
    
   
    # Fetch and move transactions
    confirmed = []
    for txn_hash in transactions:
        # print('matched pending txn hash: ', txn_hash['hash'])
        try:
            pending_txn = PendingTransaction.objects.get(hash=txn_hash['hash'])

            # print(f"matched pending transaction:  {pending_txn} ")
            tx = Transaction.objects.create(
                billing=pending_txn.billing,
                wallet=pending_txn.wallet,
                gateway=pending_txn.gateway,
                type=pending_txn.type,
                debit=pending_txn.debit,
                credit=pending_txn.credit,
                sender=pending_txn.sender.username,
                walletHash = pending_txn.walletHash,

                # receiver=pending_txn.receiver.username,
                amount=pending_txn.amount
            )

            # Store the serialized transaction data for JSONField
            confirmed.append({
                "sender": tx.sender,
                "receiver": tx.receiver,
                "amount": float(tx.amount),
                "hash": tx.hash,  # if you have this
                "type": tx.type
            })
            # confirmed.append(tx)
            pending_txn.delete()
        except PendingTransaction.DoesNotExist:
            # print(f"error: Transaction not found : {txn_hash}")
            return JsonResponse({"error": f"Transaction {txn_hash} not found"}, status=400)
        
    # check if Block contain data if not create genesis block
    block_dat = Block.objects.all()
    if not block_dat.exists():
        # print('creating genesis block')
        genesis_block = Block(height=0, previous_hash="kena h", nonce=0, hash=data["hash"], transactions = [])
        genesis_block.save()                             


    block = Block.objects.create(
        height=height,
        nonce=nonce,       
        previous_hash=previous_hashh,
        hash=calculated_hash,
        transactions=confirmed
    )
    return JsonResponse({"success": True, "block": block.hash})

# Download miner script
@csrf_exempt
def download_miner_script(request):
    get_url = request.build_absolute_uri(reverse("get_mine_data"))
    post_url = request.build_absolute_uri(reverse("submt_hash"))

    script = f"""
    import requests
    import json
    import hashlib

    GET_URL = "{get_url}"
    POST_URL = "{post_url}"
    DIFFICULTY = 4
    PREFIX = "123456789"[:DIFFICULTY]

    def calculate_hash(data):
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode()).hexdigest()

    def mine_block(data, difficulty=4):
        nonce = 0
        prefix = "123456789"[:difficulty]

        while True:
            data['nonce'] = nonce
            hash_val = calculate_hash(data)
            if hash_val.startswith(prefix):
                return {{"nonce": nonce, "hash": hash_val}}
            nonce += 1
            if nonce % 10000 == 0:
                print(f"Mining... tried {{nonce}} nonces")

    def main():
        print("Fetching block data...")
        response = requests.get(GET_URL)
        if response.status_code != 200:
            print("Failed to fetch data")
            return

        data = response.json()

        block_data = {{
            "height": data["height"],
            "timestamp": data["timestamp"],
            "transactions": data["transactions"],
            "previous_hash": data["previous_hash"]
        }}

        print("Mining block...")
        result = mine_block(block_data, DIFFICULTY)
        print("Block mined!")
        print("Nonce:", result['nonce'])
        print("Hash:", result['hash'])

        submission = {{
            "height": data["height"],
            "timestamp": data["timestamp"],
            "transactions": data["transactions"],
            "previous_hash": data["previous_hash"],
            "nonce": result['nonce'],
            "hash": result['hash']
        }}

        print("Submitting block...")
        post_response = requests.post(POST_URL, json=submission)
        print("Status code:", post_response.status_code)
        print("Response:", post_response.text)

    if __name__ == "__main__":
        main()
    """

    response = HttpResponse(script, content_type='text/x-python')
    response['Content-Disposition'] = 'attachment; filename="miner.py"'
    return response

# Logout view
def logout_view(request):
    logout(request)
    return redirect('home')