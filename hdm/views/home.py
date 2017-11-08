# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import csv
import uuid
import json
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.db import connection
from hdm.models import HDM
from hdm.forms.signup import SignupForm
from hdm.modules.hdm_db_query import HdmDBQuery
from django.views.generic import View

class HomeView(View):
    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/accounts/login/')
        
    def get(self, request):
        cursor = connection.cursor()
        if request.user.is_staff == True:
            query = """SELECT a.*, strftime('%m/%d/%Y', a.created_date) cre_date,
                             (SELECT count(DISTINCT expert_email) FROM hdm_evaluation WHERE hdm_id=a.id) eval_cnt,
                             (SELECT username FROM auth_user WHERE id=a.registrant_id) user_id
                       FROM hdm_hdm a
                       ORDER BY a.created_date desc LIMIT 5"""
            query_user = "SELECT * FROM auth_user ORDER BY date_joined LIMIT 5"
        else:
            query = """SELECT a.*, strftime('%%m/%%d/%%Y', a.created_date) cre_date,
                             (SELECT count(distinct expert_email) FROM hdm_evaluation WHERE hdm_id=a.id) eval_cnt
                       FROM hdm_hdm a
                       WHERE registrant_id = '%s'
                       ORDER BY a.created_date desc
                       LIMIT 5 """ % (request.user.id)
        
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        hdm_list = [dict(zip(columns, row)) for row in cursor.fetchall()]

        user_list = None
        if request.user.is_staff == True:
            cursor.execute(query_user)
            columns = [col[0] for col in cursor.description]
            user_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return render(request, 'hdm/home.html', {'hdm_list': hdm_list, 'user_list':user_list})
        '''
        return render(request, 'hdm/home.html')
       
                
    def help_manual(self, request):
        return render(request, 'help/manual.html', {})
        '''
