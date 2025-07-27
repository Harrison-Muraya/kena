from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from . models import Todolist, Item
from . import forms 
from Crypto.PublicKey import RSA


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
            return redirect(request, '/dashboard')
    else:
        # Display registration form
        form = forms.RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'coin/dashboard.html', {'user': request.user})
    else:
        return redirect('login')