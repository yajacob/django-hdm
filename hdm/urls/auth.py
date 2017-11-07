# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from hdm.views.auth import AuthView 


urlpatterns = [
    url(r'^signup_home/$', AuthView.signupHome,
        name='signup_home'),
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'accounts/login.html'},
        name='login'),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': '/'},
        name='logout'),
    url(r'^accounts/signup/$', AuthView.signup,
        name='signup'),
    url(r'^accounts/password/$', AuthView.change_password,
        name='change_password'),
    url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'registration/password_reset_form.html'}, 
        name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, {'template_name': 'registration/password_reset_done.html'}, 
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,  
        name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, {'template_name': 'registration/password_reset_complete.html'}, 
        name='password_reset_complete'),
]