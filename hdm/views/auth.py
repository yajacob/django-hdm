# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from hdm.forms.signup import UserCreationForm
from django.views.generic import View

class SignupView(View):
    '''
    def make_list(self, temp):
        temp_list = temp.split("|")
        rs_list = []
        for tl in temp_list:
            rs_list.append(tl.split(","))
        return rs_list
    '''
    
    def get(self, request):
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('/')
        else:
            form = UserCreationForm()
        return render(request, 'accounts/signup.html', {'form': form})
    
class SignupHomeView(View):
    # Signup from Home
    def post(self, request):
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('/auth/login/')
        else:
            form = UserCreationForm()
        return render(request, 'hdm/home.html', {'form': form})

class ChangePassword(View):
    def post(self, request):
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password was successfully updated!')
                return redirect('/')
            else:
                messages.error(request, 'Please correct the error below.')
        else:
            form = PasswordChangeForm(request.user)
        return render(request, 'accounts/change_password.html', {
            'form': form
        })
