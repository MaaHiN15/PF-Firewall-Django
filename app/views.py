from django.shortcuts import render
from django.http import JsonResponse
import json, random
from .models import Options, Table,  NatRules
from .utilities import OptionsDef, DomainDef, TableDef, FilterRulesDef, getInterfaces

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
            FilterRulesDef().filterRuleCreation(json.loads(req.body.decode("utf-8")))
            return JsonResponse({'status': 200, 'text' : 'Rules using Table added successfully!!!'})
        except Exception as e:
            return JsonResponse({'status' : 400, 'text' : e})
    
def nat(req):
    if req.method == 'POST':
        try:
            data = json.loads(req.body.decode("utf-8"))
            natRules = NatRules(
                position=random.randint(0,1000), 
                interfaces = data['interfaces'],
                protocol = data['protocol'],
                sourceAddress = data['sourceAddress'],
                sourcePort = data['sourcePort'],
                destAddress = data['destAddress'],
                destPort = data['destPort'],
                natIP = data['natIP'],
                log = data['logCheck'])
            natRules.save()
            return JsonResponse({'status': 200, 'text' : 'NAT/BINAT Rules added Successfully!!!'})
        except Exception as e:
            return JsonResponse({'status' : 400, 'text' : e})

def domainBlock(req):
    if req.method == 'POST':
        try:
            data = json.loads(req.body.decode('utf-8'))
            DomainDef().domainLoop(data['names'])
            return JsonResponse({'status':200, 'text': 'Domain Block Added successfully!!!'})
        except Exception as e:
            return JsonResponse({'status':400, 'text' : e})