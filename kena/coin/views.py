from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from . models import Todolist, Item, Coin, Wallet,CustomUser, Billing, Transaction, Block, PendingTransaction
from . import forms 
from . import blockchain
from . import uidgenerator
# from datetime import timezone
import time
import json
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


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

# Dashboard view
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
                    "private_key":  checkKey(sender.private_key).export_key().decode()
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
                    amount=amount + FEE,  # Total amount including fee
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
    previous_hash = previous_block.hash if previous_block else '0' * 64
    height = previous_block.height + 1 if previous_block else 1

    return JsonResponse({
        "height": height,
        "previous_hash": previous_hash,
        "transactions": tx_data,
        "timestamp": time.time(),
    })


@csrf_exempt
def submit_block(request):
    data = json.loads(request.body)
    # print("data: ", data)

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
    previous_hash = previous_block.hash if previous_block else '0' * 64
    height = previous_block.height + 1 if previous_block else 1

    # Reconstruct block data
    block_data = {
        "height": height,
        "timestamp": data["timestamp"],        
        "previous_hash": previous_hash,
        "nonce": data["nonce"],
        "transactions": tx_data,
    }   
    print("height: ", block_data['height'] )
    print("timestamp: ", block_data['timestamp'] )
    print("previous_hash: ", block_data['previous_hash'] )
    print("nonce: ", block_data['nonce'] )
    print(' ')
    print("transactions: ", tx_data )

    print(' ')

    calculated_hash = blockchain.CalculateHash(block_data).calculate()  
    print("calculated_hash: ", calculated_hash)
    print('received hash fron front: ', data["hash"], 'nonce: ', data["nonce"])
    if calculated_hash != data["hash"] :
        return JsonResponse({"error": "Invalid hash or proof"}, status=400)

    # Fetch and move transactions
    confirmed = []
    for tx_hash in data["transactions"]:
        try:
            pending = PendingTransaction.objects.get(hash=tx_hash)
            tx = Transaction.objects.create(
                billing=pending.billing,
                gateway=pending.gateway,
                type=pending.type,
                debit=pending.debit,
                credit=pending.credit,
                sender=pending.sender.username,
                receiver=pending.receiver.username,
                amount=pending.amount
            )
            confirmed.append(tx)
            pending.delete()
        except PendingTransaction.DoesNotExist:
            return JsonResponse({"error": f"Transaction {tx_hash} not found"}, status=400)

    block = Block.objects.create(
        height=data["height"],
        timestamp=data["timestamp"],
        nonce=data["nonce"],
        previous_hash=data["previous_hash"],
        hash=calculated_hash,
    )
    block.transactions.set(confirmed)
    return JsonResponse({"success": True, "block": block.hash})



def logout_view(request):
    logout(request)
    return redirect('home')