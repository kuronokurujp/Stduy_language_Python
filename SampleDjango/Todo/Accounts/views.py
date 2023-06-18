from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

# Create your views here.
class MyLoginView(LoginView):
    template_name = 'Accounts/Login.html'
    redirect_authenticated_user = True

class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'Accounts/Singup.html'
    success_url = reverse_lazy('task_list')
