from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View


class Login(View):

    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('core:home'))
        return render(request, self.template_name, {'error': False})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username):
            username = User.objects.get(username=username).username
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('core:home'))
        else:
            return render(request, self.template_name, {'error': True,
                                                        'message': 'User not authenticated. Wrong login/password'})


class Logout(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('login'))
