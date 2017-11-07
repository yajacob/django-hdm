# -*- coding: utf-8 -*-
from hdm.models import HDM
from django.forms import ModelForm

class HdmForm(ModelForm):
    class Meta:
        model = HDM
        fields = ('hdm_objective', 'hdm_criteria', 'hdm_factors', 'hdm_alternatives',)

    # overriding for save method
"""
    def save(self, commit = True):
        hdm_design = super(HDMForm, self).save(commit = False)
        if commit:
            hdm_design.save()
        return hdm_design
"""