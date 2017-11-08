# -*- coding: utf-8 -*-
from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework import views
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

class HdmInconsistencyVIew(generics.ListAPIView):
    
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    
    def get_queryset(self):
        term = self.request.GET.get('term', '')
        if len(term) >= 2:
            return null; 
        else:
            return null;
        
