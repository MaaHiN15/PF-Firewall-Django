from .models import *
import psutil, re, pydig, fileinput, os, shutil, subprocess, netaddr
from pffirewall.settings import BASE_DIR

class Utilities:
    def writeFile(self, position, line):
        self.checkFileExist()
        with fileinput.FileInput('pf.conf', inplace=True) as file:
            for p, l in enumerate(file, start=1):
                if p == int(position):
                    print(line)
                else:
                    print(l, end='')
            fileinput.close()
    
    def deleteLines(self, position):
        self.checkFileExist()
        with fileinput.FileInput('pf.conf', inplace=True) as file:
            for p, l in enumerate(file, start=1):
                if p == position:
                    print('')
                else:
                    print(l, end='')
            fileinput.close()

    def getContentOfFile(self):
        self.checkFileExist()
        with open(BASE_DIR / 'pf.conf', 'r') as file:
            lines_list = []
            for line_num, line in enumerate(file, start=1):
                if line.strip():                        
                    lines_list.append({'num':line_num, 'line':line})
        file.close()
        return lines_list
            
    def checkFileExist(self):
        if not os.path.exists(BASE_DIR / 'pf.conf'):
            shutil.copyfile(BASE_DIR / 'pf.conf.temp', BASE_DIR / 'pf.conf')

    def getInterfaces(self):
        interfaces = psutil.net_if_stats()
        return [interface for interface, stats in interfaces.items() if stats.isup]
    
    def getStatus(self):
        return 'enabled' in subprocess.run(['pfctl', '-s', 'info'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False).stdout.lower()
    
    def statusTurnOn(self):
        try:
            subprocess.run(['pfctl', '-e'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            return True
        except Exception as e:
            print(e)
            return False

    def statusTurnOff(self):
        try:
            subprocess.run(['sudo','pfctl', '-d'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            return True
        except Exception as e:
            print(e)
            return False

class DomainDef:
    def __init__(self) -> None:
        try:
            obj = Position.objects.get(id=1)
            self.domainPosition = obj.domainPosition
        except Position.DoesNotExist:
            obj = Position.objects.create(id=1, tablePosition=10, filterRulePosition=250, domainPosition= 350, natRulePosition=200)
            obj.save()
            self.domainPosition = obj.domainPosition

    def domainLoop(self, name):
        if Domain.objects.filter(domainName=name).exists():
            return False
        self.count = 0
        self.first_set = set()
        for _ in range(200):
            if self.count > 30:
                break
            self.digHostname(name)
        domain = Domain(position=self.domainPosition, address=list(self.first_set), domainName=name)
        domain.save()
        Utilities().writeFile(position=self.domainPosition, line=f'block out to {{ {" ".join(list(self.first_set))} }}')
        self.domainPosition += 1
        Position.objects.filter(id=1).update(domainPosition=self.domainPosition)
        return True
            
    def digHostname(self, name):
        try:
            self.second_set = set([item for item in pydig.query(name, 'A') if self.validateIP(item)])
            print(self.first_set)
            if not self.second_set.issubset(self.first_set):
                self.first_set.update(self.second_set)
                self.count = 0
            else:
                self.count += 1
        except Exception as e:
            return e
        
    def validateIP(self, ip):
        pattern = r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$'
        return re.match(pattern, ip) is not None


class OptionsDef:
    def __init__(self):
        self.options = {
            "blockPolicy":'drop',
            "OptimLevel": 'normal',
            "rulesetOptim": 'basic',
            "statePolicy": 'floating',
            "timeoutInterval": '10'
        }

    def changeOptions(self):
        for i, (key, val) in enumerate(self.options.items()):
            item = Options(position=i+2, name=key, value=val)
            item.save()

    def compareDict(self, dic):
        for key, val in dic.items():
            if key in self.options:
                if val != self.options[key]:
                    self.options.update({key : val})
                    self.switch(key, val)
                    self.changeOptions()

    def switch(self, key, val):
        if key == 'blockPolicy':
            Utilities().writeFile(2, f'set block-policy {val}')
        elif key == 'OptimLevel':
            Utilities().writeFile(3, f'set optimization {val}')
        elif key == 'rulesetOptim':
            Utilities().writeFile(4, f'set ruleset-optimization {val}')
        elif key == 'statePolicy':
            Utilities().writeFile(5, f'set state-policy {val}')
        elif key == 'timeoutInterval':
            Utilities().writeFile(6, f'set timeout interval {val}')

    
class TableDef:
    def __init__(self) -> None:
        try:
            obj = Position.objects.get(id=1)
            self.lastPosition = obj.tablePosition
        except Position.DoesNotExist:
            obj = Position.objects.create(id=1, tablePosition=10, filterRulePosition=250, domainPosition= 350, natRulePosition=200)
            obj.save()
            self.lastPosition = obj.tablePosition

    def tableCreation(self, data):
        if not Table.objects.filter(name=data['tabName']).exists() and not Table.objects.filter(iplist=data['tabIps']).exists():
            table = Table(position=self.lastPosition, name=data['tabName'], iplist=data['tabIps'])
            table.save()
            Utilities().writeFile(position=self.lastPosition, line=f'table <{data["tabName"]}> const {{ {" ".join(map(str,data["tabIps"]))} }}')
            self.lastPosition += 1
            Position.objects.filter(id=1).update(tablePosition=self.lastPosition)
            return True
        else:
            return False

class FilterRulesDef:
    def __init__(self) -> None:
        try:
            obj = Position.objects.get(id=1)
            self.filterRulePosition = obj.filterRulePosition
        except Position.DoesNotExist:
            obj = Position.objects.create(id=1, tablePosition=10, filterRulePosition=250, domainPosition= 350, natRulePosition=200)
            obj.save()
            self.filterRulePosition = obj.filterRulePosition

    def filterRuleCreation(self, data):
        try:
            if data['position']:
                self.filterRulePosition = data['position']
            rules_table = Filter(
                    position=self.filterRulePosition, 
                    action = data['action'],
                    direction = data['direction'],
                    interface = data['interface'],
                    protocol = data['protocol'],
                    sourceAddress = data['sourceAddress'],
                    sourcePort = data['sourcePort'],
                    destAddress = data['destAddress'],
                    destPort = data['destPort'],
                    force = data['force'],
                    log = data['log'],
                    type = data['type'])
            rules_table.save()
            Utilities().writeFile(position=self.filterRulePosition, line=self.makeRule(data))
            if not data['position']:
                self.filterRulePosition += 1
                Position.objects.filter(id=1).update(filterRulePosition=self.filterRulePosition)
            return True
        except Exception as e:
            print(e)
            return False

    def makeRule(self, data):
        def checkForAll(item):
            return any(_ == 'all' for _ in item)
        
        self.rule = f'{data["action"]} {data["direction"]}' 
        if data['log'] == 'on':
            self.rule += ' log'
        if data['force'] == 'on':
            self.rule += ' quick'
        if not data['interface'] == 'all':
            self.rule += f' on {data["interface"]}'

        if not checkForAll(data['protocol']):
            self.rule += f' proto {{ {" ".join(map(str, data["protocol"]))} }}'

        if not checkForAll(data['sourceAddress']) and checkForAll(data['sourcePort']):
            if data['type'] == 'table':
                self.rule += f' from {{ {" ".join(map(str, ["<{}>".format(_) for _ in data["sourceAddress"]]))} }}'
            else:
                self.rule += f' from {{ {" ".join(map(str, data["sourceAddress"]))} }}'

        if checkForAll(data['sourceAddress']) and not checkForAll(data['sourcePort']):
            self.rule += f' from any port {{ {" ".join(map(str, data["sourcePort"]))} }}'

        if not checkForAll(data['sourceAddress']) and not checkForAll(data['sourcePort']):
            if data['type'] == 'table':
                self.rule += f' from {{ {" ".join(map(str, ["<{}>".format(_) for _ in data["sourceAddress"]]))} }} port {{ {" ".join(map(str, data["sourcePort"]))} }}'
            else:
                self.rule += f' from {{ {" ".join(map(str, data["sourceAddress"]))} }} port {{ {" ".join(map(str, data["sourcePort"]))} }}'


        if not checkForAll(data['destAddress']) and checkForAll(data['destPort']):
            if data['type'] == 'table':
                self.rule += f' to {{ {" ".join(map(str, ["<{}>".format(_) for _ in data["destAddress"]]))} }}'
            else:
                self.rule += f' to {{ {" ".join(map(str, data["destAddress"]))} }}'


        if checkForAll(data['destAddress']) and not checkForAll(data['destPort']):
            self.rule += f' to any port {{ {" ".join(map(str, data["destPort"]))} }}'

        if not checkForAll(data['destAddress']) and not checkForAll(data['destPort']):
            if data['type'] == 'table':
                self.rule += f' to {{ {" ".join(map(str, ["<{}>".format(_) for _ in data["destAddress"]]))} }} port {{ {" ".join(map(str, data["destPort"]))} }}'
            else:
                self.rule += f' to {{ {" ".join(map(str, data["destAddress"]))} }} port {{ {" ".join(map(str, data["destPort"]))} }}'

        if not any(_ in self.rule for _ in ['from', 'to']):
            self.rule += ' all'
        return self.rule


class NatDef:
    def __init__(self) -> None:
        try:
            obj = Position.objects.get(id=1)
            self.natRulePosition = obj.natRulePosition
        except Position.DoesNotExist:
            obj = Position.objects.create(id=1, tablePosition=10, filterRulePosition=250, domainPosition= 350, natRulePosition=200)
            obj.save()
            self.natRulePosition = obj.natRulePosition

    def natRuleFunc(self, data):
            natRules = NatRules(
                natChoose = data['natChoose'],
                position=self.natRulePosition, 
                interface = data['interface'],
                protocol = data['protocol'],
                sourceAddress = data['sourceAddress'],
                sourcePort = data['sourcePort'],
                destAddress = data['destAddress'],
                destPort = data['destPort'],
                natIP = data['natIP']
            )
            natRules.save()
            Utilities().writeFile(position=self.natRulePosition, line=self.makeNatRule(data))
            self.natRulePosition += 1
            Position.objects.filter(id=1).update(natRulePosition=self.natRulePosition)
            return True
    
    def makeNatRule(self, data):
        def checkForAll(item):
            return any(_ == 'all' for _ in item)
        if data['natChoose'] == 'nat':
            self.rule = 'nat'
        elif data['natChoose'] == 'binat':
            self.rule = 'binat'

        if not data['interface'] == 'all':
            self.rule += f' on {data["interface"]}'

        if not checkForAll(data['protocol']):
            self.rule += f' proto {{ {" ".join(map(str, data["protocol"]))} }}'

        if not checkForAll(data['sourceAddress']) and checkForAll(data['sourcePort']):
            self.rule += f' from {{ {" ".join(map(str, data["sourceAddress"]))} }}'

        if checkForAll(data['sourceAddress']) and not checkForAll(data['sourcePort']):
            self.rule += f' from any port {{ {" ".join(map(str, data["sourcePort"]))} }}'

        if not checkForAll(data['sourceAddress']) and not checkForAll(data['sourcePort']):
            self.rule += f' from {{ {" ".join(map(str, data["sourceAddress"]))} }} port {{ {" ".join(map(str, data["sourcePort"]))} }}'

        if 'from' not in self.rule:
            self.rule += ' from any'

        if not checkForAll(data['destAddress']) and checkForAll(data['destPort']):
            self.rule += f' to {{ {" ".join(map(str, data["destAddress"]))} }}'

        if checkForAll(data['destAddress']) and not checkForAll(data['destPort']):
            self.rule += f' to any port {{ {" ".join(map(str, data["destPort"]))} }}'

        if not checkForAll(data['destAddress']) and not checkForAll(data['destPort']):
            self.rule += f' to {{ {" ".join(map(str, data["destAddress"]))} }} port {{ {" ".join(map(str, data["destPort"]))} }}'

        if 'to' not in self.rule:
            self.rule += '  to any'

        self.rule += f' -> {data["natIP"]}'
        return self.rule
