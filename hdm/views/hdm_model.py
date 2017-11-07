# -*- coding: utf-8 -*-

import uuid, json, csv

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from hdm.forms.hdm_forms import HdmForm
from hdm.models import HDM
from hdm.modules.design_diagram_script import DiagramScript
from hdm.modules.expert_diagram_script import ExpertDiagramScript
from hdm.modules.hdm_db_query import HdmDBQuery

class HdmModelView(object):
    @login_required(login_url="/accounts/login/")
    def hdm_model_create(self, request):
        if request.method == "POST":
            form = HdmForm(request.POST)
            if form.is_valid():
                hdm = form.save(commit=False)
                hdm.hdm_uuid = uuid.uuid4().hex 
                hdm.registrant = request.user
    
                # clean data
                hdm.hdm_criteria = self.model_str_clean("cr", request.POST.get('hdm_criteria'))
                hdm.hdm_factors = self.model_str_clean("fa", request.POST.get('hdm_factors'))
                hdm.hdm_alternatives = self.model_str_clean("al", request.POST.get('hdm_alternatives'))
    
                hdm.created_date = timezone.now()
                hdm.save()
                return redirect('/hdm/model_manage/')
            else:
                return redirect('/hdm/model_manage/')
        else:
            range12 = list(range(1, 13))
            return render(request, 'hdm/model_create.html', {'range12': range12})
    
    @csrf_exempt
    def uploadCSVfile(self, request):
        response = {}
        print("#################")
        print(request.FILES)
        print("#################")
        if request.method == 'POST' and request.FILES['upload_file']:
            file = request.FILES['upload_file']
            print('test1')
            try:
                data = [row for row in csv.reader(file.read().splitlines())]
                print('test2')
                print(data)
            except:
                print("Error")
            #data = [row for row in csv.reader(f.read().splitlines())] # csv file parsing
            #df = pd.read_csv(f)
            #print(df)
            response = {'success': True}
        else:
            response = {'success': False}
        return HttpResponse(json.dumps(response))

    @login_required(login_url="/accounts/login/")
    def hdm_model_update(self, request, hdm_id):
        # Update Process
        if request.method == "POST":
            hdm_objective = request.POST.get('hdm_objective')
    
            # clean data
            hdm_criteria = self.model_str_clean("cr", request.POST.get('hdm_criteria'))
            hdm_factors = self.model_str_clean("fa", request.POST.get('hdm_factors'))
            hdm_alternatives = self.model_str_clean("al", request.POST.get('hdm_alternatives'))
        
            cursor = connection.cursor()
            query = "UPDATE hdm_hdm SET hdm_objective=%s, hdm_criteria=%s, hdm_factors=%s, hdm_alternatives=%s WHERE id=%s"
            cursor.execute(query, (hdm_objective, hdm_criteria, hdm_factors, hdm_alternatives, hdm_id))
            return redirect('/hdm/model_view/' + hdm_id + '/')
    
        # Update Form
        else:
            try:
                hdm = HDM.objects.get(id__iexact=hdm_id)
                hdm_dict = {"hdm_objective":hdm.hdm_objective, "hdm_criteria":hdm.hdm_criteria, "hdm_factors":hdm.hdm_factors}
                ds = DiagramScript(hdm_dict)
                hdm_fa = hdm.hdm_factors.split("|")
                hdm_fa = list(map(lambda hdm_fa: hdm_fa.strip(), hdm_fa))
    
            except HDM.DoesNotExist:
                raise Http404
        
            range12 = list(range(1, 13))
            return render(request, 'hdm/model_update.html', {'range12': range12, 'hdm': hdm, 'ds':ds, 'hdm_fa':hdm_fa, 'hdm_id':hdm_id})
    
    @login_required(login_url="/accounts/login/")
    def hdm_model_manage(self, request):
        if request.user.is_staff == True:
            query = """SELECT a.*, strftime('%m/%d/%Y %H:%M', a.created_date) cre_date,
                             (SELECT count(distinct expert_email) FROM hdm_evaluation WHERE hdm_id=a.id) eval_cnt,
                             (SELECT username FROM auth_user WHERE id=a.registrant_id) user_id
                       FROM hdm_hdm a
                       ORDER BY a.created_date desc"""
        else:
            query = """SELECT a.*, strftime('%%m/%%d/%%Y %%H:%%M', a.created_date) cre_date,
                             (SELECT count(distinct expert_email) FROM hdm_evaluation WHERE hdm_id=a.id) eval_cnt
                       FROM hdm_hdm a
                       WHERE registrant_id = '%s'
                       ORDER BY a.created_date desc
                       LIMIT 10 """ % (request.user.id)
    
        cursor = connection.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        hdm_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        hdm_domain = "http://" + request.get_host()
        return render(request, 'hdm/model_manage.html', {'hdm_list': hdm_list}, {'hdm_domain':hdm_domain})
    
    @login_required(login_url="/accounts/login/")
    def hdm_model_view(self, request, hdm_id):
        try:
            hdm_dict = HdmDBQuery.getHDMById(request, hdm_id)
    
            ds = DiagramScript(hdm_dict)
            hdm_al = hdm_dict['hdm_alternatives'].split(",")
    
            if hdm_id == "":
                hdm_id = hdm_dict['hdm_id']
            eval_cnt = HdmDBQuery.getEvalCount(hdm_id)
            
        except:
            raise Http404
    
        return render(request, 'hdm/model_view.html', {'ds':ds, 'hdm_al':hdm_al, 'hdm':hdm_dict, 'eval_cnt':eval_cnt})
    
    @login_required(login_url="/accounts/login/")
    def hdm_model_diagram(self, request, hdm_id):
        hdm = HDM.objects.get(id__iexact=hdm_id)
        ds = ExpertDiagramScript(hdm)
    
        hdm_al = hdm.hdm_alternatives.split(",")
        return render(request, 'hdm/model_diagram.html', {'ds':ds, 'hdm_al':hdm_al})
            
    @login_required(login_url="/accounts/login/")
    def hdm_model_delete(self, request, hdm_uuid):
        hdm_id = HdmDBQuery.getIDbyUUID(hdm_uuid)
        if hdm_id is None:
            raise Http404
        
        cursor = connection.cursor()
        if request.user.is_staff == True:
            query = "DELETE FROM hdm_evaluation WHERE hdm_id='%s'" % (hdm_id)
            cursor.execute(query)
            query = "DELETE FROM hdm_hdm WHERE id='%s'" % (hdm_id)
            cursor.execute(query)
        else:
            query = """
                DELETE FROM hdm_evaluation
                WHERE hdm_id in (SELECT id FROM hdm_hdm WHERE id='%s' and registrant_id = '%s')
                """ % (hdm_id, request.user.id)
            cursor.execute(query)
            query = "DELETE FROM hdm_hdm WHERE id='%s' and registrant_id='%s'" % (hdm_id, request.user.id)
            cursor.execute(query)
            
        return redirect('/hdm/model_manage/')

    def model_str_clean(self, stype, mstr):
        result = ""
        if stype == "fa":
            # Pink, Blue, Yellow|16GB, 32GB, 64GB, 128GB|USPS, UPS, FedEx|
            for idx, grp in enumerate(mstr.split("|")):
                if len(grp) < 1:
                    continue
                if idx > 0:
                    result += "|"
                for idx2, item in enumerate(grp.split(",")):
                    if idx2 > 0:
                        result += ","
                    result += item.strip()
        # "cr" or "al"
        else:
            # Color, Memory, Delivery
            for idx, item in enumerate(mstr.split(",")):
                if len(item) < 1:
                    continue
                if idx > 0:
                    result += ","
                result += item.strip()
        return result
