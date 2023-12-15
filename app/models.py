from django.db import models
from uuid import uuid4

class Options(models.Model):
    position = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=100)
    class Meta:
        db_table = 'Options'

class Table(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    position = models.IntegerField()
    name = models.CharField(max_length=100, unique=True)
    iplist = models.CharField(max_length=200, unique=True)
    class Meta:
        db_table = 'Table'

class Filter(models.Model):
    id =  models.UUIDField(primary_key=True, unique=True, default=uuid4)
    type = models.CharField(max_length=10)
    position = models.IntegerField()
    action = models.CharField(max_length=10)
    direction = models.CharField(max_length=10)
    interfaces = models.CharField(max_length=100)
    protocol = models.CharField(max_length=100)
    sourceAddress = models.CharField(max_length=1000)
    sourcePort = models.CharField(max_length=100)
    destAddress = models.CharField(max_length=1000)
    destPort = models.CharField(max_length=100)
    force = models.CharField(max_length=10, null=True)
    log = models.CharField(max_length=10, null=True)
    class Meta:
        db_table = 'Filter'
    

class NatRules(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    natChoose = models.CharField(max_length=10)
    position = models.IntegerField()
    interfaces = models.CharField(max_length=100)
    protocol = models.CharField(max_length=100)
    sourceAddress = models.CharField(max_length=1000)
    sourcePort = models.CharField(max_length=100)
    destAddress = models.CharField(max_length=1000)
    destPort = models.CharField(max_length=100)
    natIP = models.CharField(max_length=20, null=True)
    class Meta:
        db_table = 'NatRules'


class Domain(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    position = models.IntegerField()
    domainName = models.CharField(max_length=200)
    address = models.CharField(max_length=10000)
    class Meta:
        db_table = 'Domain'

class Position(models.Model):
    id = models.IntegerField(primary_key=True)
    tablePosition = models.IntegerField()
    filterRulePosition = models.IntegerField()
    natRulePosition = models.IntegerField()
    domainPosition = models.IntegerField()
    class Meta:
        db_table = 'Position'