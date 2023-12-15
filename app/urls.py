from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('api/baseForm', views.baseForm),
    path('api/table', views.table),
    path('api/filter', views.filter),
    path('api/nat', views.nat),
    path('api/domain', views.domainBlock),
]