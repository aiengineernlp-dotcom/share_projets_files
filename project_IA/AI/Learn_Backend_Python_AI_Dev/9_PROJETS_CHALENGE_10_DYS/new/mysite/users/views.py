from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm
# Create your views here.




def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Enregistre l'utilisateur en base de données
            username = user.username  # Récupère le nom d'utilisateur
            messages.success(request, f'Welcome {username}, your account has been created!')
            return redirect('login')  # Redirige après l'inscription vers la connection login
    else:
        form = RegisterForm()  # Formulaire vide pour une requête GET

    return render(request, 'users/register.html', {'form': form})  # Affiche le formulaire



@login_required
def profile_page(request):
    return render(request,'users/profile-page.html',{})






