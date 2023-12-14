from .models import Options, DomainBlock
import psutil, re, random, pydig

class Utilities:
    def getInterfaces(self):
        interfaces = psutil.net_if_stats()
        return [interface for interface, stats in interfaces.items() if stats.isup]
    
    def domainLoop(self, names):
        for name in names:
            self.count = 0
            self.first_set = set()
            self.second_set = set()
            for _ in range(200):
                if self.count > 20:
                    break
                self.digHostname(name)
            domain = DomainBlock(position=random.randint(0, 1000), address=list(self.first_set), domainName=name)
            domain.save()
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


class OptionsClass:
    def __init__(self):
        self.options = {
            "blockPolicy":'drop',
            "debugLevel": 'info',
            "OptimLevel": 'normal',
            "rulesetOptim": 'basic',
            "statePolicy": 'floating',
            "timeoutInterval": '10',
            "skipinterfaces": list()
        }
    def changeOptions(self):
        for i,(key, val) in enumerate(self.options.items()):
            item = Options(position=i+2, name=key, value=val)
            item.save()

    def compareDict(self, dic):
        for key, val in dic.items():
            if key in self.options:
                if val != self.options[key]:
                    self.options.update({key : val})
                    self.changeOptions()
        
