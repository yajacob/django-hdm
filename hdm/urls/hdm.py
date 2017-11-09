# -*- coding: utf-8 -*-
from django.conf.urls import url
from hdm.views.hdm_model import ModelListView, ModelCreateView, ModelUpdateView, ModelDesignView, ModelDiagramView, ModelDelete
from hdm.views.result import ModelResultView, ResultCsvDownload, ResultJsonDownload

urlpatterns = [
    #url(r'^api/', include(rest_api)),
    url(r'^model_manage/$', ModelListView.as_view(), name='hdm_model_list'),
    url(r'^model_create/$', ModelCreateView.as_view(), name='hdm_create_model'),
    #url(r'^hdm/uploadcsvfile$', views.uploadCSVfile, name='upload_csv_file'),
    url(r'^model_update/(\d+)/$', ModelUpdateView.as_view(), name='hdm_update_model'),
    url(r'^model_view/(\d*)/*$', ModelDesignView.as_view(), name='hdm_view_model'),
    #url(r'^hdm/model_result/(\d+)/([\d,]*)$', view_result.hdm_model_result, name='hdm_model_result'),
    url(r'^model_diagram/(\d+)/$', ModelDiagramView.as_view(), name='hdm_model_diagram'),
    url(r'^model_delete/([a-z0-9]+)/$', ModelDelete.as_view(), name='hdm_model_delete'),
    url(r'^model_result/(\d+)/([\d,]*)$', ModelResultView.as_view(), name='hdm_model_result'),
    url(r'^result_csv_download/(\d+)/(\d+)$', ResultCsvDownload.as_view(), name='result_csv_download'),
    url(r'^result_json_download/(\d+)/(\d+)$', ResultJsonDownload.as_view(), name='result_json_download'),
]
