from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import Options, Table
from .utilities import OptionsDef, DomainDef, TableDef, FilterRulesDef, getInterfaces, NatDef

def index(req):
    return render(req, 'addrule.html', {
        'interfaces' : getInterfaces(),
        'tables' : list(Table.objects.values_list('name', flat=True))
    })

def baseForm(req):
    if req.method == 'POST':
        try:
            if Options.objects.all().count() != 7:
                OptionsDef().changeOptions()
            OptionsDef().compareDict(json.loads(req.body.decode("utf-8")))
            return JsonResponse({'status': 200, 'text' : 'Basic Form Updated Successfully!!!'})
        except Exception as e:
            return JsonResponse({'status' : 400, 'text' : e})

def table(req):
    if req.method == 'POST':
        try:
            if TableDef().tableCreation(json.loads(req.body.decode("utf-8"))):
                return JsonResponse({'status': 200, 'text' : 'Table created successfully!!'})
            else:
                return JsonResponse({'status': 300, 'text' : 'Duplicate Table entry!!'})
        except Exception as e:
            return JsonResponse({'status': 400, 'text' : e})
    
def filter(req):
    if req.method == 'POST':
        try:
            if FilterRulesDef().filterRuleCreation(json.loads(req.body.decode("utf-8"))):
                return JsonResponse({'status': 200, 'text' : 'Rules using Table added successfully!!!'})
            return JsonResponse({'status': 300, 'text' : 'Duplicate Rule...Check it!!!'})
        except Exception as e:
            return JsonResponse({'status' : 400, 'text' : e})
    
def nat(req):
    if req.method == 'POST':
        try:
            if NatDef().natRuleFunc(json.loads(req.body.decode("utf-8"))):
                return JsonResponse({'status': 200, 'text' : 'NAT/BINAT Rules added Successfully!!!'})
            return JsonResponse({'status': 300, 'text' : 'Duplicate NAT/BINAT Rules!!!'})
        except Exception as e:
            return JsonResponse({'status' : 400, 'text' : e})

def domainBlock(req):
    if req.method == 'POST':
        try:
            data = json.loads(req.body.decode('utf-8'))
            if DomainDef().domainLoop(data['name']):
                return JsonResponse({'status':200, 'text': 'Domain Block Added successfully!!!'})
            return JsonResponse({'status':300, 'text': 'Duplicate Domain Block..!!!'})
        except Exception as e:
            return JsonResponse({'status':400, 'text' : e})