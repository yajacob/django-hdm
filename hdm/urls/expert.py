# -*- coding: utf-8 -*-
from django.conf.urls import url
from hdm.views.hdm_model import HdmModelView
from hdm.views.result import ResultView
from hdm.views.expert import ExpertLoginView, ExpertEvaluateView

urlpatterns = [
    url(r'^([a-z0-9]+)/$', ExpertLoginView, name='expert_login'),
    url(r'^evaluate/$', ExpertEvaluateView.as_view(), name='expert_evaluate'),
    #url(r'^exp_delete/(\d+)/([\d,]*)$', ExpertView.hdm_expert_delete, name='expert_delete'),
]
