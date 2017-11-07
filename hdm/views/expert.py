# -*- coding: utf-8 -*-
from django.contrib.auth import login, authenticate
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.contrib.auth.decorators import login_required

from hdm.models import HDM
from hdm.modules.hdm_db_query import HdmDBQuery
from hdm.modules.expert_diagram_script import ExpertDiagramScript
from hdm.modules.calc_eval import CalcEvaluation

class ExpertView():
    # login for expert
    def hdm_expert_login(self, request, uuid):
        # proc login - sending to evaluation
        message = ""
        if request.method == "POST":
            exp_email = request.POST.get('exp_email')
            if HdmDBQuery.isExpertParticipated(uuid, exp_email):
                message = "ALREADY"
    
            try:
                hdm = HDM.objects.get(hdm_uuid__iexact=uuid)
                ds = ExpertDiagramScript(hdm)
                
            except HDM.DoesNotExist:
                raise Http404
        
            hdm_al = hdm.hdm_alternatives.split(",")
            range28 = list(range(1, 29))
            return render(request, 'hdm/expert_evaluate.html', {'message':message, 'req_post':request.POST, 'uuid':uuid, 'hdm':hdm, 'ds':ds, 'hdm_al':hdm_al, 'range28':range28})
        # login form
        else:
            try:
                HDM.objects.get(hdm_uuid__iexact=uuid)
            except HDM.DoesNotExist:
                raise Http404
    
            return render(request, 'hdm/expert_login.html', {'uuid': uuid })
            
    # evaluation for expert submit
    @csrf_exempt
    def hdm_expert_evaluate(self, request):
        if request.method == 'POST':
            result = "SUCCESS"
    
            uuid = request.POST.get('uuid')
            exp_fname = request.POST.get('exp_fname')
            exp_lname = request.POST.get('exp_lname')
            exp_email = request.POST.get('exp_email')
            
            hdm_dict = HdmDBQuery.getHDMbyUUID(uuid)
    
            if hdm_dict is None:
                raise Http404("Wrong URL for the Evaluation!")
    
            hdm_id = hdm_dict['hdm_id']
            registrant_id = hdm_dict['registrant_id']
    
            designer_dict = HdmDBQuery.getUserInfoBy(registrant_id)
    
            # Insert Evaluating Data 
            get_eval_cr = request.POST.get('eval_cr')
            get_eval_fa = request.POST.get('eval_fa')
            get_eval_al = request.POST.get('eval_al')
            
            eval_dic = {"cr":get_eval_cr, "fa":get_eval_fa, "al":get_eval_al }
            
            # calculation of evaluation 
            eval_calc = CalcEvaluation(hdm_id, eval_dic)
            eval_cr = eval_calc.proc_eval_cr()
            eval_fa = eval_calc.proc_eval_fa()
            eval_al = eval_calc.proc_eval_al()
            
            # calculation of result
            rs_cr = eval_calc.proc_result_cr()
            rs_fa = eval_calc.proc_result_fa()
            rs_al = eval_calc.proc_result_al()
    
            # DB Insert
            cursor = connection.cursor()
            query = '''INSERT INTO hdm_evaluation (expert_no, expert_fname, expert_lname, expert_email,
                            hdm_id, get_eval_cr, get_eval_fa, get_eval_al, eval_cr, eval_fa, eval_al,
                            result_cr, result_fa, result_al, eval_date)
                        VALUES ((select ifnull(max(expert_no), 0) + 1 FROM hdm_evaluation where hdm_id = %s), %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, DATETIME('now'))
                    '''
            cursor.execute(query, (hdm_id, exp_fname, exp_lname, exp_email, hdm_id, get_eval_cr, get_eval_fa, get_eval_al, eval_cr, eval_fa, eval_al, rs_cr, rs_fa, rs_al))
            
            return render(request, 'hdm/expert_success.html', {'result':result, 'designer':designer_dict})
        else:
            raise Http404
    
    @login_required(login_url="/accounts/login/")
    def hdm_expert_delete(self, request, hdm_id, exp_id):
        cursor = connection.cursor()
    
        query = "DELETE FROM hdm_evaluation WHERE hdm_id = '%s' AND expert_no in (%s)" % (hdm_id, exp_id)
        cursor.execute(query)
    
        return redirect('/hdm/model_view/' + hdm_id)    
