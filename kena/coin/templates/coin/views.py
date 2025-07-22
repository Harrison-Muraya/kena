from django.shortcuts import render
from .forms import RegistrationForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        # Handle form submission
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save the user or perform other actions
            form.save()
            return render(request, 'auth/success.html')
    else:
        # Display registration form
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})
