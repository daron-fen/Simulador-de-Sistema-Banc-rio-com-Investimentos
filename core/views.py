from django.shortcuts import render, redirect
from django.db.models import Sum
from decimal import Decimal
from .models import Conta, Transacao

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'index.html', {'saldo': 0, 'saldo_total': 0})

    # Pega ou cria a conta do utilizador logado
    conta, created = Conta.objects.get_or_create(usuario=request.user)

    # PROCESSAR ENVIO DO FORMULÁRIO (POST)
    if request.method == 'POST':
        acao = request.POST.get('acao')
        valor_str = request.POST.get('valor')
        
        if valor_str:
            valor = Decimal(valor_str)
            
            if acao == 'deposito':
                # Cria um registo de depósito no banco de dados
                Transacao.objects.create(conta=conta, tipo='DEPOSITO', valor=valor)
                return redirect('index') # Recarrega a página para atualizar os saldos limpos
                
            elif acao == 'saque':
                # Primeiro, calcula o saldo atual para ver se o utilizador tem dinheiro
                total_dep = Transacao.objects.filter(conta=conta, tipo='DEPOSITO').aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
                total_saq = Transacao.objects.filter(conta=conta, tipo='SAQUE').aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
                saldo_atual = conta.saldo + total_dep - total_saq
                
                # Validação: Só saca se tiver saldo suficiente
                if valor <= saldo_atual:
                    Transacao.objects.create(conta=conta, tipo='SAQUE', valor=valor)
                else:
                    # Se não tiver saldo, podes adicionar uma mensagem de erro no futuro
                    pass
                return redirect('index')

    # CÁLCULOS PARA EXIBIÇÃO NA TELA (GET)
    total_depositos = Transacao.objects.filter(conta=conta, tipo='DEPOSITO').aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    total_saques = Transacao.objects.filter(conta=conta, tipo='SAQUE').aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    
    saldo_disponivel = conta.saldo + total_depositos - total_saques
    
    # Valores simulados da carteira
    total_investido = Decimal('73400.00')
    investido_tesouro = total_investido * Decimal('0.34')
    investido_cdb = total_investido * Decimal('0.43')
    investido_acoes = total_investido * Decimal('0.23')
    saldo_total = saldo_disponivel + total_investido
    total_transferencias = Decimal('0.00')

    context = {
        'saldo': saldo_disponivel,
        'saldo_total': saldo_total,
        'depositos': total_depositos,
        'saques': total_saques,
        'transferencias': total_transferencias,
        'investido': total_investido,
        'investido_tesouro': investido_tesouro,
        'investido_cdb': investido_cdb,
        'investido_acoes': investido_acoes,
    }
    return render(request, 'index.html', context)