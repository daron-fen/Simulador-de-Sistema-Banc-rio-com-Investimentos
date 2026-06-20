from django.shortcuts import render
from django.db.models import Sum
from .models import Conta, Transacao

def index(request):
    if request.user.is_authenticated:
        # Pega ou cria a conta do usuário logado
        conta, created = Conta.objects.get_or_create(usuario=request.user)
        
        # Filtra e soma todas as transações do tipo DEPOSITO deste usuário
        total_depositos = Transacao.objects.filter(conta=conta, tipo='DEPOSITO').aggregate(total=Sum('valor'))['total'] or 0.00
        
        # Filtra e soma todas as transações do tipo SAQUE deste usuário
        total_saques = Transacao.objects.filter(conta=conta, tipo='SAQUE').aggregate(total=Sum('valor'))['total'] or 0.00
        
        # O saldo real agora é calculado: Saldo Inicial + Depósitos - Saques
        saldo_calculado = conta.saldo + total_depositos - total_saques
    else:
        saldo_calculado = 0.00
        total_depositos = 0.00
        total_saques = 0.00

    # Enviamos todas estas variáveis calculadas para o HTML
    context = {
        'saldo': saldo_calculado,
        'depositos': total_depositos,
        'saques': total_saques,
    }
    return render(request, 'index.html', context)