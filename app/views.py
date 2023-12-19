from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
import json, subprocess
from .models import *
from .utilities import *

def index(req):
    return render(req, 'addrule.html', {
        'interfaces' : Utilities().getInterfaces(),
        'tables' : list(Table.objects.values_list('name', flat=True)),
        'position' : Position.objects.first(),
        'status' : Utilities().getStatus()
    })

def viewFile(req):
    return render(req, 'view.html', {'filedata': Utilities().getContentOfFile()})

def editFile(req):
    return render(req, 'edit.html', {'tables' : Table.objects.all(), 
                        'filterrules' : Filter.objects.all(),
                        'natrules' : NatRules.objects.all(),
                        'doamins' : Domain.objects.all(),
                        'alert' : req.GET.get('alert')})


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
                return JsonResponse({'status': 200, 'text' : 'Rules added successfully!!!'})
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
        
def tableDeletion(req):
    if delete(req, Table):
        return redirect(reverse('edit') + '?alert=table')

def filterRuleDeletion(req):
    if delete(req, Filter):
        return redirect(reverse('edit') + '?alert=filter')

def natRulesDeletion(req):
    if delete(req, NatRules):
        return redirect(reverse('edit') + '?alert=nat')

def domainDeletion(req):
    if delete(req, Domain):
        return redirect(reverse('edit') + '?alert=domain')


def delete(req, cls):
    data = cls.objects.get(id=req.GET.get('id'))
    Utilities().deleteLines(data.position)
    cls.objects.filter(id=req.GET.get('id')).delete()
    return True


def statusOn(req):
    if Utilities().statusTurnOn():
        return JsonResponse({'status':200, 'text':'PF successfully enabled!'})
    return JsonResponse({'status':300, 'text':'PF Already Enabled!'})

def statusOff(req):
    if Utilities().statusTurnOff():
        return JsonResponse({'status':200, 'text':'PF successfully disabled!'})
    return JsonResponse({'status':300, 'text':'PF Already disabled!'})

def applyConf(req):
    try:
        name = BASE_DIR / 'pf.conf'
        process = subprocess.run(['pfctl', '-nf', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if process.returncode == 0:
            subprocess.run(['pfctl', '-f', str(name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            return JsonResponse({'status': 200, 'text': 'pf.conf applied successfully!'})
        else:
            error_text = process.stderr.strip() if process.stderr else 'Unknown error'
            return JsonResponse({'status': 400, 'text': f'Error applying pf.conf: {error_text}'})
    except Exception as e:
        return JsonResponse({'status': 400, 'text': f'Exception: {str(e)}'})
