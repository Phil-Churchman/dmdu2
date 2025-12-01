from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
import numpy as np
import pandas as pd
# from __future__ import (absolute_import, print_function, division,
# unicode_literals)
import seaborn as sns
import matplotlib.pyplot as plt
import os, io

from django.conf import settings

@login_required
def current_version(request):
    user = request.user

    try:
        currentversion = CurrentVersion.objects.get(user=user)
        return currentversion.version, currentversion
    except:
        return None, None

def check_version_selected(version):

    if version == None:
        version_selected = False
    else:
        version_selected = True
    return version_selected

# DUMMY
def make_copy(old_ver, new_ver):
    methods = list(Method.objects.filter(version=old_ver))
    lookup = Lookup.objects.get(version=old_ver)

    for old_method in methods:
        new_method = Method.objects.create(version=new_ver)

        for field in old_method._meta.get_fields():
            fieldname = field.name
            if fieldname in ["version", "id"]:
                continue
            setattr(new_method, fieldname, getattr(old_method, fieldname))
        new_method.save()
    new_lookup = Lookup.objects.create(version=new_ver,
                                       value_1=lookup.value_1,
                                       value_2=lookup.value_2,
                                       value_3=lookup.value_3,
                                       value_4=lookup.value_4,
                                       value_5=lookup.value_5,
                                       value_6=lookup.value_6,
                                       value_7=lookup.value_7,
                                       value_8=lookup.value_8,
                                       value_9=lookup.value_9,
                                       value_10=lookup.value_10,
                                       value_1_is_option_reqt=lookup.value_1_is_option_reqt,
                                       value_2_is_option_reqt=lookup.value_2_is_option_reqt, 
                                       value_3_is_option_reqt=lookup.value_3_is_option_reqt,
                                       value_4_is_option_reqt=lookup.value_4_is_option_reqt,
                                       value_5_is_option_reqt=lookup.value_5_is_option_reqt,
                                       value_6_is_option_reqt=lookup.value_6_is_option_reqt,
                                       value_7_is_option_reqt=lookup.value_7_is_option_reqt,
                                       value_8_is_option_reqt=lookup.value_8_is_option_reqt,
                                       value_9_is_option_reqt=lookup.value_9_is_option_reqt,
                                       value_10_is_option_reqt=lookup.value_10_is_option_reqt                                   
                                       )
    new_lookup.save()
    return

def create_methods(version, blank, file):
    if blank == False:
        if file == None:
            if Master.objects.filter(ref="default").count() != 0:
                methods_df = pd.DataFrame(json.loads(Master.objects.get(ref="default").methods))
                lookup_df = pd.DataFrame(json.loads(Master.objects.get(ref="default").lookup))
            else:
                if file == None:    
                    methods_df = pd.read_excel(os.path.join(settings.BASE_DIR, "master.xlsx"), engine='openpyxl', sheet_name="Methods")
                    lookup_df = pd.read_excel(os.path.join(settings.BASE_DIR, "master.xlsx"), engine='openpyxl', sheet_name="Lookup")
        else:
            methods_df = pd.read_excel(file, engine='openpyxl', sheet_name="Methods")
            lookup_df = pd.read_excel(file, engine='openpyxl', sheet_name="Lookup")

        for index, row in methods_df.iterrows():
            Method.objects.create(
                version = version,
                index = str(index),
                name=row['Method'],
                description=row['Description'],
                long_description=row['Long Description'],
                links=row['Links'],
                dmdu=row['DMDU'],
                management=row['Management'],
                process=row['Process'],
                enabled=row["Enabled"],
                value_1=row['value_1'],
                value_2=row['value_2'],
                value_3=row['value_3'],
                value_4=row['value_4'],
                value_5=row['value_5'],
                value_6=row['value_6'],
                value_7=row['value_7'],
                value_8=row['value_8'],
                value_9=row['value_9'],
                value_10=row['value_10'],
                )
        variables = []
        for index, row in lookup_df.iterrows():
            variables.append([row['Value'], row['Variable'], row["Is option reqt"]])
            setattr(version, "value_" + str(int(index) + 1), row["Setting"])
        version.save()
        Lookup.objects.create(
            version = version,
            value_1=variables[0][1],
            value_2=variables[1][1],
            value_3=variables[2][1],
            value_4=variables[3][1],
            value_5=variables[4][1],
            value_6=variables[5][1],
            value_7=variables[6][1],
            value_8=variables[7][1],
            value_9=variables[8][1],
            value_10=variables[9][1],
            value_1_is_option_reqt=variables[0][2],
            value_2_is_option_reqt=variables[1][2],
            value_3_is_option_reqt=variables[2][2],
            value_4_is_option_reqt=variables[3][2],
            value_5_is_option_reqt=variables[4][2],
            value_6_is_option_reqt=variables[5][2],
            value_7_is_option_reqt=variables[6][2],
            value_8_is_option_reqt=variables[7][2],
            value_9_is_option_reqt=variables[8][2],
            value_10_is_option_reqt=variables[9][2],
            )
            
    else:
        Lookup.objects.create(
        version = version,
        value_1="NONE",
        value_2="NONE",
        value_3="NONE",
        value_4="NONE",
        value_5="NONE",
        value_6="NONE",
        value_7="NONE",
        value_8="NONE",
        value_9="NONE",
        value_10="NONE",
        )          

def get_variables(version):
    lookup = Lookup.objects.get(version=version)
    lookup_list = [{"value": version.value_1, "variable": lookup.value_1, "index": "0", "name": "value_1", "option_reqt": lookup.value_1_is_option_reqt},
                    {"value": version.value_2, "variable": lookup.value_2, "index": "1", "name": "value_2", "option_reqt": lookup.value_2_is_option_reqt},
                    {"value": version.value_3, "variable": lookup.value_3, "index": "2", "name": "value_3", "option_reqt": lookup.value_3_is_option_reqt},
                    {"value": version.value_4, "variable": lookup.value_4, "index": "3", "name": "value_4", "option_reqt": lookup.value_4_is_option_reqt},
                    {"value": version.value_5, "variable": lookup.value_5, "index": "4", "name": "value_5", "option_reqt": lookup.value_5_is_option_reqt},
                    {"value": version.value_6, "variable": lookup.value_6, "index": "5", "name": "value_6", "option_reqt": lookup.value_6_is_option_reqt},
                    {"value": version.value_7, "variable": lookup.value_7, "index": "6", "name": "value_7", "option_reqt": lookup.value_7_is_option_reqt},
                    {"value": version.value_8, "variable": lookup.value_8, "index": "7", "name": "value_8", "option_reqt": lookup.value_8_is_option_reqt},
                    {"value": version.value_9, "variable": lookup.value_9, "index": "8", "name": "value_9", "option_reqt": lookup.value_9_is_option_reqt},
                    {"value": version.value_10, "variable": lookup.value_10, "index": "9", "name": "value_10", "option_reqt": lookup.value_10_is_option_reqt},
                    ] 
    return lookup_list   
