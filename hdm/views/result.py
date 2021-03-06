import csv

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from hdm.modules.calc_result import CalcResult
from hdm.modules.calc_eval import CalcEvaluation
import numpy as np
import pandas as pd


class ModelResultView(View):
    @login_required(login_url="/auth/login/")
    def get(self, request, hdm_id, exp_id):
        # pandas setting for float number
        pd.options.display.float_format = '{:.4f}'.format
    
        cursor = connection.cursor()
    
        query = """SELECT a.*, '-' chart_cr, '-' chart_al FROM hdm_evaluation a JOIN 
                    (SELECT max(id) as max_id FROM hdm_evaluation GROUP BY hdm_id, expert_email) b
                ON a.id = b.max_id
                WHERE a.hdm_id = '%s'
                ORDER BY a.id DESC""" % (hdm_id)
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        eval_all_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # For Checked Experts
        if exp_id != "":
            exp_id = "AND a.expert_no in (" + exp_id + ")"
    
        # Individual Result
        query = """SELECT a.*, '-' chart_cr, '-' chart_al FROM hdm_evaluation a JOIN 
                    (SELECT max(id) as max_id FROM hdm_evaluation GROUP BY hdm_id, expert_email) b
                ON a.id = b.max_id
                WHERE a.hdm_id = '%s'
                %s
                ORDER BY a.id DESC""" % (hdm_id, exp_id)
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        eval_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
    
        main_df_cr = pd.DataFrame()
        main_df_fa = pd.DataFrame()
        main_df_al = pd.DataFrame()
        total_df_al = pd.DataFrame()
        total_df_al_chart = pd.DataFrame()
        
        list_col_keys = []
    
        for ev in eval_list:
            exp_no = ev['expert_no']
            eval_cr = pd.read_json(ev['eval_cr'])
            eval_cr.index = np.arange(1, len(eval_cr) + 1)
            main_df_cr = pd.concat([main_df_cr, eval_cr])
            eval_cr_html = eval_cr.to_html()
            eval_fa = pd.read_json(ev['eval_fa'])
            eval_fa.index = np.arange(1, len(eval_fa) + 1)
            main_df_fa = pd.concat([main_df_fa, eval_fa])
            eval_fa_html = eval_fa.to_html()
            eval_al = pd.read_json(ev['eval_al'])
            eval_al.index = np.arange(1, len(eval_al) + 1)
            main_df_al = pd.concat([main_df_al, eval_al])
            eval_al_html = eval_al[['Criteria', 'Factors', 'Alternatives', 'Value']].to_html()
            
            ev['eval_cr'] = eval_cr_html.replace("dataframe", "dataframe data_eval eval_cr") 
            ev['eval_fa'] = eval_fa_html.replace("dataframe", "dataframe data_eval eval_fa")
            ev['eval_al'] = eval_al_html.replace("dataframe", "dataframe data_eval eval_al")
    
            # chart data
            temp = ""
            dic_chart_cr = pd.read_json(ev['result_cr']).to_dict()
            for key, val in dic_chart_cr["eval"].items():
                temp += "['%s', %s]," % (key, val)
            ev['chart_cr'] = "[%s]" % temp
            dic_sum = pd.read_json(ev['result_al']).sum(axis=1)
            temp = ""
            for key, val in dic_sum.items():
                temp += "['%s', %.2f]," % (key, val)
            ev['chart_al'] = "[%s]" % temp
            
            ev['result_cr'] = pd.read_json(ev['result_cr']).to_html()
            ev['result_fa'] = pd.read_json(ev['result_fa']).to_html()  # .replace("0.000", "-").replace("0.00", "-").replace("0.0", "-")
            ev['result_al'] = pd.read_json(ev['result_al'])
            ev['result_al']['SUM'] = ev['result_al'].sum(axis=1)
            ev['result_al'] = ev['result_al'].to_html()
            
            ev['result_cr'] = ev['result_cr'].replace("dataframe", "dataframe data_result result_cr") 
            ev['result_fa'] = ev['result_fa'].replace("dataframe", "dataframe data_result result_fa")
            ev['result_al'] = ev['result_al'].replace("dataframe", "dataframe data_result result_al")
    
            
            # Calculating for Main Alternative
            al_cal = CalcResult(hdm_id)
            al_result_dic = al_cal.proc_total_result_al(hdm_id, exp_no)
            
            # for chart data
            temp_df_al_chart = pd.DataFrame([al_result_dic], columns=al_result_dic.keys())
            total_df_al_chart = pd.concat([total_df_al_chart, temp_df_al_chart])
            
            temp_df = pd.DataFrame([al_result_dic], columns=al_result_dic.keys())
    
            for key in list(temp_df.columns.values):
                temp_df[key] = temp_df[key].astype(float).fillna(0.0)
                temp_df[key] = temp_df[key] / 100
                list_col_keys.append(al_result_dic.keys())
    
            # Add expert column
            temp_df['Experts'] = ev['expert_lname'] + ', ' + ev['expert_fname']
            inconsistency = 0.0000
            # al_result_dic.update({'_Inconsistency':inconsistency})
            temp_df['Inconsistency'] = inconsistency
            
            total_df_al = pd.concat([total_df_al, temp_df])
    
        
        # main_total_chart_cr
        main_chart_cr = ''
        
        # main_total_chart_al
        for key in list(total_df_al_chart.columns.values):
            total_df_al_chart[key] = total_df_al_chart[key].astype(float).fillna(0.0)
        
        total_df_al_mean_dict = total_df_al_chart.mean().to_dict()        
        temp = ""
        for key, val in total_df_al_mean_dict.items():
            temp += "['%s', %.2f]," % (key, val)
        main_chart_al = "[%s]" % temp
        
        # Set Index as Expert's name
        total_df_al.set_index('Experts', inplace=True, drop=True)
    
        # calculate mean, min, max, std. dev.
        total_df_al.loc['Mean'] = total_df_al.mean()
        total_df_al.loc['Min'] = total_df_al.min()
        total_df_al.loc['Max'] = total_df_al.max()
        total_df_al.loc['Std. Deviation'] = total_df_al.std()
        
        result_cal = CalcResult(hdm_id)
        main_result_cr = result_cal.proc_result_main_cr(main_df_cr)
        main_result_fa = result_cal.proc_result_main_fa(main_df_fa)
        main_result_al = result_cal.proc_result_main_al(main_df_al)
    
        # multiindex to single index
        total_df_al = total_df_al.reset_index()
    
        # char data for main
        main_result_cr_html = main_result_cr.to_html()
        main_result_fa_html = main_result_fa.to_html()
        main_result_al_html = main_result_al.to_html()
        total_df_al_html = total_df_al.to_html()
    
        main_result_cr_html = main_result_cr_html.replace("dataframe", "dataframe data_eval eval_cr") 
        main_result_fa_html = main_result_fa_html.replace("dataframe", "dataframe data_eval eval_fa")
        main_result_al_html = main_result_al_html.replace("dataframe", "dataframe data_eval eval_al")
        total_df_al_html = total_df_al_html.replace("dataframe", "dataframe data_main main_al")
        
        return render(request, 'hdm/model_result.html', {'eval_all_list': eval_all_list, 'eval_list': eval_list, 'hdm_id':hdm_id,
                       'main_result_cr':main_result_cr_html, 'main_result_fa':main_result_fa_html, 'main_result_al':main_result_al_html,
                       'total_df_al':total_df_al_html, 'main_chart_cr':main_chart_cr, 'main_chart_al':main_chart_al})


class ResultCsvDownload(View):
    @login_required(login_url="/auth/login/")
    def get(self, request, hdm_id, exp_id):
        cursor = connection.cursor()
        
        # Individual Result
        query = """SELECT a.*, '-' chart_cr, '-' chart_al FROM hdm_evaluation a JOIN 
                    (SELECT max(id) as max_id FROM hdm_evaluation GROUP BY hdm_id, expert_email) b
                ON a.id = b.max_id
                WHERE a.hdm_id = '%s'
                  AND a.expert_no = '%s'
                ORDER BY a.id DESC""" % (hdm_id, exp_id)
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        eval_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        main_df_cr = pd.DataFrame()
        main_df_fa = pd.DataFrame()
        main_df_al = pd.DataFrame()
    
        for ev in eval_list:
            eval_cr = pd.read_json(ev['eval_cr'])
            eval_cr.index = np.arange(1, len(eval_cr) + 1)
            main_df_cr = pd.concat([main_df_cr, eval_cr])
            # eval_cr = eval_cr.to_html()
            
            eval_fa = pd.read_json(ev['eval_fa'])
            eval_fa.index = np.arange(1, len(eval_fa) + 1)
            main_df_fa = pd.concat([main_df_fa, eval_fa])
            # eval_fa = eval_fa.to_html()
            
            eval_al = pd.read_json(ev['eval_al'])
            eval_al.index = np.arange(1, len(eval_al) + 1)
            main_df_al = pd.concat([main_df_al, eval_al])
            # eval_al = eval_al[['Criteria', 'Factors', 'Alternatives', 'Value']].to_html()
    
        # change order of the dataframe
        main_df_al = main_df_al[['Criteria', 'Factors', 'Alternatives', 'Value']]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="hdm_evaluation.csv"'
    
        temp_key1 = []
        temp_key2 = []
        temp_key3 = []
        temp_val = []
        write_list = []
        writer = csv.writer(response)
        writer.writerow(['1. Evaluation for Criteria'])
        for idx, alist in enumerate(main_df_cr.values.tolist()):
            temp_key1.append(alist[0])
            temp_val.append(alist[1])
            
            if idx % 2 == 1:
                write_list += temp_key1
                write_list += temp_val
                writer.writerow(write_list)
                temp_key1 = []
                temp_val = []
                write_list = []
        
        writer.writerow([''])
        writer.writerow(['2. Evaluation for Factors'])
        for idx, alist in enumerate(main_df_fa.values.tolist()):
            if idx % 2 == 0:
                temp_key1.append(alist[0])
            temp_key2.append(alist[1])
            temp_val.append(alist[2])
            
            if idx % 2 == 1:
                write_list += temp_key1
                write_list += temp_key2
                write_list += temp_val
                writer.writerow(write_list)
                temp_key1 = []
                temp_key2 = []
                temp_val = []
                write_list = []
        
        writer.writerow([''])
        writer.writerow(['3. Evaluation for Alternatives'])
        for idx, alist in enumerate(main_df_al.values.tolist()):
            if idx % 2 == 0:
                temp_key1.append(alist[0])
                temp_key2.append(alist[1])
            temp_key3.append(alist[2])
            temp_val.append(alist[3])
            
            if idx % 2 == 1:
                write_list += temp_key1
                write_list += temp_key2
                write_list += temp_key3
                write_list += temp_val
                writer.writerow(write_list)
                temp_key1 = []
                temp_key2 = []
                temp_key3 = []
                temp_val = []
                write_list = []
        
        return response


class ResultJsonDownload(View):
    @login_required(login_url="/auth/login/")
    def hdm_result_json_download(self, request, hdm_id, exp_id):
        cursor = connection.cursor()
        
        # Individual Result
        query = """SELECT a.*, '-' chart_cr, '-' chart_al FROM hdm_evaluation a JOIN 
                    (SELECT max(id) as max_id FROM hdm_evaluation GROUP BY hdm_id, expert_email) b
                ON a.id = b.max_id
                WHERE a.hdm_id = '%s'
                  AND a.expert_no = '%s'
                ORDER BY a.id DESC""" % (hdm_id, exp_id)
        cursor.execute(query)
        print(query)
        columns = [col[0] for col in cursor.description]
        eval_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        
        for ev in eval_list:
            json_cr_data = ev['eval_cr']
            json_fa_data = ev['eval_fa'] 
            json_al_data = ev['eval_al']
        
        json_data = "[\n" + json_cr_data + ",\n" + json_fa_data + ",\n" + json_al_data + "]"
        
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=export.json'
    
        return response
    

    '''
    @login_required(login_url="/auth/login/")
    # def hdm_model_result(self, request, hdm_id, exp_id):
    def hdm_model_result_bak(self, request, *args, **kwargs):
        hdm_id = ""
        exp_id = ""
        print(args)
        print(kwargs)

        cursor = connection.cursor()
    
        query = """SELECT a.*, '-' chart_cr, '-' chart_al FROM hdm_evaluation a JOIN 
                    (SELECT max(id) as max_id FROM hdm_evaluation GROUP BY hdm_id, expert_email) b
                ON a.id = b.max_id
                WHERE a.hdm_id = '%s'
                ORDER BY a.id DESC""" % (hdm_id)
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        eval_all_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # For Checked Experts
        if exp_id != "":
            exp_id = "AND a.expert_no in (" + exp_id + ")"
    
        # Individual Result
        query = """SELECT a.*, '-' chart_cr, '-' chart_al FROM hdm_evaluation a JOIN 
                    (SELECT max(id) as max_id FROM hdm_evaluation GROUP BY hdm_id, expert_email) b
                ON a.id = b.max_id
                WHERE a.hdm_id = '%s'
                %s
                ORDER BY a.id DESC""" % (hdm_id, exp_id)
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        eval_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        main_df_cr = pd.DataFrame()
        main_df_fa = pd.DataFrame()
        main_df_al = pd.DataFrame()
    
        for ev in eval_list:
            eval_cr = pd.read_json(ev['eval_cr'])
            eval_cr.index = np.arange(1, len(eval_cr) + 1)
            main_df_cr = pd.concat([main_df_cr, eval_cr])
            eval_cr = eval_cr.to_html()
            eval_fa = pd.read_json(ev['eval_fa'])
            eval_fa.index = np.arange(1, len(eval_fa) + 1)
            main_df_fa = pd.concat([main_df_fa, eval_fa])
            eval_fa = eval_fa.to_html()
            eval_al = pd.read_json(ev['eval_al'])
            eval_al.index = np.arange(1, len(eval_al) + 1)
            main_df_al = pd.concat([main_df_al, eval_al])
            eval_al = eval_al[['Criteria', 'Factors', 'Alternatives', 'Value']].to_html()
            
            ev['eval_cr'] = eval_cr.replace("dataframe", "dataframe data_eval eval_cr") 
            ev['eval_fa'] = eval_fa.replace("dataframe", "dataframe data_eval eval_fa")
            ev['eval_al'] = eval_al.replace("dataframe", "dataframe data_eval eval_al")
            
            # char data
            temp = ""
            dic_chart_cr = pd.read_json(ev['result_cr']).to_dict()
            for key, val in dic_chart_cr["eval"].items():
                temp += "['%s', %s]," % (key, val)
            ev['chart_cr'] = "[%s]" % temp
            dic_sum = pd.read_json(ev['result_al']).sum(axis=1)
            temp = ""
            for key, val in dic_sum.items():
                temp += "['%s', %.2f]," % (key, val)
            ev['chart_al'] = "[%s]" % temp
            
            ev['result_cr'] = pd.read_json(ev['result_cr']).to_html()
            ev['result_fa'] = pd.read_json(ev['result_fa']).to_html().replace("0.000", "-").replace("0.00", "-").replace("0.0", "-")
            ev['result_al'] = pd.read_json(ev['result_al'])
            ev['result_al']['SUM'] = ev['result_al'].sum(axis=1)
            ev['result_al'] = ev['result_al'].to_html()
        
        cal = CalcEvaluation(hdm_id)
        main_result_cr = cal.proc_result_main_cr(main_df_cr)
        main_result_fa = cal.proc_result_main_fa(main_df_fa)
        main_result_al = cal.proc_result_main_al(main_df_al)
        
        # char data for main
        main_result_cr = main_result_cr.to_html()
        main_result_fa = main_result_fa.to_html()
        main_result_al = main_result_al.to_html()
    
        main_result_cr = main_result_cr.replace("dataframe", "dataframe data_eval eval_cr") 
        main_result_fa = main_result_fa.replace("dataframe", "dataframe data_eval eval_fa")
        main_result_al = main_result_al.replace("dataframe", "dataframe data_eval eval_al")
        
        return render(request, 'hdm/model_result.html', {'eval_all_list': eval_all_list, 'eval_list': eval_list, 'hdm_id':hdm_id,
                       'main_result_cr':main_result_cr, 'main_result_fa':main_result_fa, 'main_result_al':main_result_al})
    '''
