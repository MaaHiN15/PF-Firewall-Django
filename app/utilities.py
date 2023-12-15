from .models import Options, Domain, Filter, Table, Position, NatRules
import psutil, re, pydig, fileinput, os, shutil
from pffirewall.settings import BASE_DIR

def writeFile(position, line):
    if not os.path.exists(BASE_DIR / 'pf.conf'):
        shutil.copyfile(BASE_DIR / 'pf.conf.temp', BASE_DIR / 'pf.conf')
    with fileinput.FileInput('pf.conf', inplace=True) as file:
        for p, l in enumerate(file, start=1):
            if p == position:
                print(line)
            else:
                print(l, end='')
        fileinput.close()

def getInterfaces():
    interfaces = psutil.net_if_stats()
    return [interface for interface, stats in interfaces.items() if stats.isup]


class DomainDef:
    def __init__(self) -> None:
        try:
            obj = Position.objects.get(id=1)
            self.domainPosition = obj.domainPosition
        except Position.DoesNotExist:
            obj = Position.objects.create(id=1, tablePosition=10, filterRulePosition=200, domainPosition= 300, natRulePosition=450)
            obj.save()
            self.domainPosition = obj.domainPosition

    def domainLoop(self, name):
        if Domain.objects.filter(domainName=name).exists():
            return False
        self.count = 0
        self.first_set = set()
        self.second_set = set()
        for _ in range(200):
            if self.count > 20:
                break
            self.digHostname(name)
        domain = Domain(position=self.domainPosition, address=list(self.first_set), domainName=name)
        domain.save()
        writeFile(position=self.domainPosition, line=f'block out to {{ {" ".join(list(self.first_set))} }}')
        self.domainPosition += 1
        Position.objects.filter(id=1).update(domainPosition=self.domainPosition)
        return True
            
    def digHostname(self, name):
        try:
            self.second_set.update([item for item in pydig.query(name, 'A') if self.validateIP(item)])
            if self.first_set != self.second_set:
                self.first_set = self.second_set.copy()
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
            "debugLevel": 'info',
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
        print(key, val)
        if key == 'blockPolicy':
            writeFile(2, f'set block-policy {val}')
        elif key == 'debugLevel':
            writeFile(3, f'set debug {val}')
        elif key == 'OptimLevel':
            writeFile(4, f'set optimization {val}')
        elif key == 'rulesetOptim':
            writeFile(5, f'set ruleset-optimization {val}')
        elif key == 'statePolicy':
            writeFile(6, f'set state-policy {val}')
        elif key == 'timeoutInterval':
            writeFile(7, f'set timeout interval {val}')

    
class TableDef:
    def __init__(self) -> None:
        try:
            obj = Position.objects.get(id=1)
            self.lastPosition = obj.tablePosition
        except Position.DoesNotExist:
            obj = Position.objects.create(id=1, tablePosition=10, filterRulePosition=200, domainPosition= 300, natRulePosition=450)
            obj.save()
            self.lastPosition = obj.tablePosition
    def tableCreation(self, data):
        if not Table.objects.filter(name=data['tabName']).exists() and not Table.objects.filter(iplist=data['tabIps']).exists():
            table = Table(position=self.lastPosition, name=data['tabName'], iplist=data['tabIps'])
            table.save()
            writeFile(position=self.lastPosition, line=f'table <{data["tabName"]}> const {set(data["tabIps"])}')
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
            obj = Position.objects.create(id=1, tablePosition=10, filterRulePosition=200, domainPosition= 300, natRulePosition=450)
            obj.save()
            self.filterRulePosition = obj.filterRulePosition
    def filterRuleCreation(self, data):
        try:
            rules_table = Filter(
                    position=self.filterRulePosition, 
                    action = data['action'],
                    direction = data['direction'],
                    interfaces = data['interface'],
                    protocol = data['protocol'],
                    sourceAddress = data['sourceAddress'],
                    sourcePort = data['sourcePort'],
                    destAddress = data['destAddress'],
                    destPort = data['destPort'],
                    force = data['force'],
                    log = data['log'],
                    type = data['type'])
            rules_table.save()
            writeFile(position=self.filterRulePosition, line=self.makeRule(data))
            self.filterRulePosition += 1
            Position.objects.filter(id=1).update(filterRulePosition=self.filterRulePosition)
        except Exception as e:
            print(e)

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
            obj = Position.objects.create(id=1, tablePosition=10, filterRulePosition=200, domainPosition= 300, natRulePosition=450)
            obj.save()
            self.natRulePosition = obj.natRulePosition
    def natRuleFunc(self, data):
            print(data)
            natRules = NatRules(
                natChoose = data['natChoose'],
                position=self.natRulePosition, 
                interfaces = data['interface'],
                protocol = data['protocol'],
                sourceAddress = data['sourceAddress'],
                sourcePort = data['sourcePort'],
                destAddress = data['destAddress'],
                destPort = data['destPort'],
                natIP = data['natIP']
            )
            natRules.save()
            writeFile(position=self.natRulePosition, line=self.makeNatRule(data))
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
        print(self.rule)
        return self.rule
