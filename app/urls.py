from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('view', views.viewFile, name='view'),
    path('edit', views.editFile, name='edit'),
    path('api/table/delete', views.tableDeletion),
    path('api/filter/delete', views.filterRuleDeletion),
    path('api/nat/delete', views.natRulesDeletion),
    path('api/domain/delete', views.domainDeletion),
    path('api/baseForm', views.baseForm),
    path('api/table', views.table),
    path('api/filter', views.filter),
    path('api/nat', views.nat),
    path('api/domain', views.domainBlock),
    path('api/status/on', views.statusOn),
    path('api/status/off', views.statusOff),
    path('api/apply', views.applyConf),
    path('api/reset', views.resetAll)
]
