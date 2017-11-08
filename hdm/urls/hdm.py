# -*- coding: utf-8 -*-
from django.conf.urls import url
from hdm.views.hdm_model import HdmModelView
from hdm.views.result import ResultView

urlpatterns = [
    #url(r'^api/', include(rest_api)),
    url(r'^model_manage/$', HdmModelView.hdm_model_manage, name='hdm_manage_model'),
    url(r'^model_create/$', HdmModelView.hdm_model_create, name='hdm_create_model'),
    url(r'^model_update/(\d+)/$', HdmModelView.hdm_model_update, name='hdm_update_model'),
    url(r'^model_view/(\d*)/*$', HdmModelView.hdm_model_view, name='hdm_view_model'),
    #url(r'^hdm/model_result/(\d+)/([\d,]*)$', view_result.hdm_model_result, name='hdm_model_result'),
    url(r'^model_result/(\d+)/([\d,]*)$', ResultView.hdm_model_result, name='hdm_model_result'),
    url(r'^model_diagram/(\d+)/$', HdmModelView.hdm_model_diagram, name='hdm_model_diagram'),
    url(r'^model_delete/([a-z0-9]+)/$', HdmModelView.hdm_model_delete, name='hdm_model_delete'),
    #url(r'^hdm/uploadcsvfile$', views.uploadCSVfile, name='upload_csv_file'),
    url(r'^result_csv_download/(\d+)/(\d+)$', ResultView.hdm_result_csv_download, name='result_csv_download'),
    url(r'^result_json_download/(\d+)/(\d+)$', ResultView.hdm_result_json_download, name='result_json_download'),
]
