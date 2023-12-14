from django.shortcuts import render
from django.http import JsonResponse
import json, random
from .models import Options, Table, FilterManual, NatRules
from .utilities import OptionsClass, Utilities

def index(req):
    return render(req, 'addrule.html', {
        'interfaces' : Utilities().getInterfaces(),
        'tables' : list(Table.objects.values_list('name', flat=True))
    })

def baseForm(req):
    if req.method == 'POST':
        try:
            if Options.objects.all().count() != 7:
                OptionsClass().changeOptions()
            OptionsClass().compareDict(json.loads(req.body.decode("utf-8")))
            return JsonResponse({'status': 200, 'text' : 'Basic Form Updated Successfully!!!'})
        except Exception as e:
            return JsonResponse({'status' : 400, 'text' : e})

def table(req):
    if req.method == 'POST':
        try:
            data = json.loads(req.body.decode("utf-8"))
            table = Table(name=data['tabName'], iplist=data['tabIps'])
            table.save()
            return JsonResponse({'status': 200, 'text' : 'Table created successfully!!!'})
        except Exception as e:
            return JsonResponse({'status': 400, 'text' : e})
    
def filter_table(req):
    if req.method == 'POST':
        try:
            data = json.loads(req.body.decode("utf-8"))
            fil_tab = FilterManual(
                position=random.randint(0,1000), 
                action = data['action'],
                direction = data['direction'],
                interfaces = data['interfaces'],
                protocol = data['protocol'],
                sourceAddress = data['sourceAddress'],
                sourcePort = data['sourcePort'],
                destAddress = data['destAddress'],
                destPort = data['destPort'],
                tcpFlags = data['tcpFlags'],
                state = data['state'],
                force = data['force'],
                log = data['log'])
            fil_tab.save()
            return JsonResponse({'status': 200, 'text' : 'Rules using Table added successfully!!!'})
        except Exception as e:
            return JsonResponse({'status' : 400, 'text' : e})
    
def filter_manual(req):
    if req.method == 'POST':
        try:
            data = json.loads(req.body.decode("utf-8"))
            fil_manual = FilterManual(
                position=random.randint(0,1000), 
                action = data['action'],
                direction = data['direction'],
                interfaces = data['interfaces'],
                protocol = data['protocol'],
                sourceAddress = data['sourceAddress'],
                sourcePort = data['sourcePort'],
                destAddress = data['destAddress'],
                destPort = data['destPort'],
                tcpFlags = data['tcpFlags'],
                state = data['state'],
                force = data['force'],
                log = data['log'])
            fil_manual.save()
            return JsonResponse({'status': 200, 'text' : 'Manual IP/CIDR Rules added successfully!!!'})
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
            Utilities().domainLoop(data['names'])
            return JsonResponse({'status':200, 'text': 'Domain Block Added successfully!!!'})
        except Exception as e:
            return JsonResponse({'status':400, 'text' : e})