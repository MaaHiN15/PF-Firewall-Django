from django.db import models
from uuid import uuid4

# Create your models here.
class Options(models.Model):
    position = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=100)
    class Meta:
        db_table = 'Options'

class Table(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    name = models.CharField(max_length=100)
    iplist = models.CharField(max_length=200)
    class Meta:
        db_table = 'Table'

class FilterTable(models.Model):
    id =  models.UUIDField(primary_key=True, unique=True, default=uuid4)
    position = models.IntegerField()
    action = models.CharField(max_length=10)
    direction = models.CharField(max_length=10)
    interfaces = models.CharField(max_length=100)
    protocol = models.CharField(max_length=100)
    sourceAddress = models.CharField(max_length=1000)
    sourcePort = models.CharField(max_length=100)
    destAddress = models.CharField(max_length=1000)
    destPort = models.CharField(max_length=100)
    tcpFlags = models.CharField(max_length=100)
    state = models.CharField(max_length=20)
    force = models.CharField(max_length=10, null=True)
    log = models.CharField(max_length=10, null=True)
    class Meta:
        db_table = 'FilterTable'
    
class FilterManual(models.Model):
    id =  models.UUIDField(primary_key=True, unique=True, default=uuid4)
    position = models.IntegerField()
    action = models.CharField(max_length=10)
    direction = models.CharField(max_length=10)
    interfaces = models.CharField(max_length=100)
    protocol = models.CharField(max_length=100)
    sourceAddress = models.CharField(max_length=1000)
    sourcePort = models.CharField(max_length=100)
    destAddress = models.CharField(max_length=1000)
    destPort = models.CharField(max_length=100)
    tcpFlags = models.CharField(max_length=100)
    state = models.CharField(max_length=20)
    force = models.CharField(max_length=10, null=True)
    log = models.CharField(max_length=10, null=True)
    class Meta:
        db_table = 'FilterManual'

class NatRules(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    position = models.IntegerField()
    interfaces = models.CharField(max_length=100)
    protocol = models.CharField(max_length=100)
    sourceAddress = models.CharField(max_length=1000)
    sourcePort = models.CharField(max_length=100)
    destAddress = models.CharField(max_length=1000)
    destPort = models.CharField(max_length=100)
    natIP = models.CharField(max_length=20, null=True)
    log = models.CharField(max_length=10, null=True)
    class Meta:
        db_table = 'NatRules'


class DomainBlock(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    position = models.IntegerField()
    domainName = models.CharField(max_length=200)
    address = models.CharField(max_length=10000)
    class Meta:
        db_table = 'DomainBlock'