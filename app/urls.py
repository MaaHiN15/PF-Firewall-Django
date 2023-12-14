from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/baseForm', views.baseForm, name='baseForm'),
    path('api/table', views.table, name='table'),
    path('api/rule/table', views.filter_table, name="filter_table"),
    path('api/rule/manual', views.filter_manual, name='filter_manual'),
    path('api/nat', views.nat, name='nat_manual'),
    path('api/domain', views.domainBlock, name='domainBlock'),
]