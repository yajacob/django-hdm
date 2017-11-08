# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.http import request

from hdm.views.home import HomeView

from . import auth
from . import hdm
#from . import rest_api


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='hdm_home'),
    #url(r'^api/', include(rest_api)),
    url(r'^auth/', include(auth)),
    url(r'^hdm/', include(hdm)),
    url(r'^expert/', include(expert)),
]
