from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('investir/', views.investir, name='investir'),
    path('resgatar/<int:investimento_id>/', views.resgatar_investimento, name='resgatar_investimento'),
    path('depositar/', views.depositar, name='depositar'),
    path('sacar/', views.sacar, name='sacar'),
    path('investimentos/', views.investimentos_lista, name='investimentos_lista'),
    path('simular-rendimento/', views.simular_rendimento, name='simular_rendimento'),
]