from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random
from .models import Conta, Transacao, Investimento, ConfiguracaoInvestimento
from .forms import InvestimentoForm, DepositoForm, SaqueForm

@login_required
def dashboard(request):
    conta = request.user.conta
    investimentos_ativos = Investimento.objects.filter(conta=conta, situacao='ATIVO')
    ultimas_transacoes = Transacao.objects.filter(conta=conta).order_by('-data')[:10]
    
    # Calcular total investido
    total_investido = sum(inv.valor_investido for inv in investimentos_ativos)
    
    context = {
        'conta': conta,
        'investimentos_ativos': investimentos_ativos,
        'ultimas_transacoes': ultimas_transacoes,
        'total_investido': total_investido,
    }
    return render(request, 'investimentos/dashboard.html', context)

@login_required
def investir(request):
    conta = request.user.conta
    configs = ConfiguracaoInvestimento.objects.filter(ativo=True)
    
    if request.method == 'POST':
        form = InvestimentoForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            valor = form.cleaned_data['valor']
            
            if conta.saldo < valor:
                messages.error(request, 'Saldo insuficiente para realizar o investimento.')
                return redirect('investir')
            
            # Criar investimento
            investimento = Investimento(
                conta=conta,
                tipo=tipo,
                valor_investido=valor,
                valor_atual=valor,
                situacao='ATIVO'
            )
            
            # Configurações específicas por tipo
            if tipo == 'COFRINHO':
                investimento.indice = 'CDI'
                config = ConfiguracaoInvestimento.objects.get(tipo='COFRINHO')
                investimento.taxa = config.taxa_base
            elif tipo == 'TESOURO':
                config = ConfiguracaoInvestimento.objects.get(tipo='TESOURO')
                investimento.taxa = config.taxa_base
                investimento.vencimento = timezone.now().date() + timedelta(days=365*5)
            elif tipo == 'PRE_FIXADO':
                config = ConfiguracaoInvestimento.objects.get(tipo='PRE_FIXADO')
                investimento.taxa = config.taxa_base
                investimento.vencimento = timezone.now().date() + timedelta(days=365*2)
            elif tipo == 'POS_FIXADO':
                config = ConfiguracaoInvestimento.objects.get(tipo='POS_FIXADO')
                investimento.taxa = config.taxa_base
                investimento.indice = 'IPCA'
                investimento.vencimento = timezone.now().date() + timedelta(days=365*3)
            
            investimento.save()
            
            # Debita da conta
            conta.saldo -= valor
            conta.save()
            
            Transacao.objects.create(
                conta=conta,
                tipo='INVESTIMENTO',
                valor=valor,
                descricao=f"Investimento em {investimento.get_tipo_display()} - R$ {valor:.2f}"
            )
            
            messages.success(request, f'Investimento de R$ {valor:.2f} realizado com sucesso!')
            return redirect('dashboard')
    else:
        form = InvestimentoForm()
    
    context = {
        'form': form,
        'configs': configs,
        'saldo': conta.saldo,
    }
    return render(request, 'investimentos/investir.html', context)

@login_required
def resgatar_investimento(request, investimento_id):
    investimento = get_object_or_404(Investimento, id=investimento_id, conta=request.user.conta)
    
    if investimento.situacao != 'ATIVO':
        messages.error(request, 'Este investimento já foi resgatado ou cancelado.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        if 'confirmar' in request.POST:
            # Calcular rendimento baseado no tipo
            valor_resgate = investimento.valor_atual
            
            # Atualiza o investimento
            investimento.situacao = 'RESGATADO'
            investimento.data_resgate = timezone.now()
            investimento.save()
            
            # Credita na conta
            conta = investimento.conta
            conta.saldo += valor_resgate
            conta.save()
            
            Transacao.objects.create(
                conta=conta,
                tipo='RESGATE',
                valor=valor_resgate,
                descricao=f"Resgate de investimento {investimento.get_tipo_display()} - R$ {valor_resgate:.2f}"
            )
            
            messages.success(request, f'Investimento resgatado com sucesso! Valor total: R$ {valor_resgate:.2f}')
            return redirect('dashboard')
    
    context = {
        'investimento': investimento,
    }
    return render(request, 'investimentos/resgatar.html', context)

@login_required
def simular_rendimento(request):
    """Simula o rendimento dos investimentos (simulação diária)"""
    # Esta função seria chamada por um cron job ou task scheduler
    investimentos_ativos = Investimento.objects.filter(situacao='ATIVO')
    
    for investimento in investimentos_ativos:
        if investimento.tipo == 'COFRINHO':
            # 121% do CDI - Simulando CDI de 10.5% ao ano
            cdi = 10.5
            taxa_diaria = (cdi * 1.21 / 100) / 252
            rendimento = investimento.valor_atual * Decimal(str(taxa_diaria)) / Decimal('100')
            
        elif investimento.tipo == 'TESOURO':
            # Tesouro Direto com rendimento baseado na taxa
            taxa_diaria = investimento.taxa / 100 / 252
            rendimento = investimento.valor_atual * Decimal(str(taxa_diaria))
            
        elif investimento.tipo == 'PRE_FIXADO':
            # Rendimento fixo pré-determinado
            taxa_diaria = investimento.taxa / 100 / 252
            rendimento = investimento.valor_atual * Decimal(str(taxa_diaria))
            
        elif investimento.tipo == 'POS_FIXADO':
            # IPCA + taxa (simulando inflação)
            ipca = random.uniform(0.4, 0.8)  # IPCA mensal simulado
            taxa_total = Decimal(str(investimento.taxa + ipca))
            taxa_diaria = taxa_total / 100 / 30
            rendimento = investimento.valor_atual * taxa_diaria
        
        # Aplica rendimento
        investimento.valor_atual += rendimento
        investimento.save()
        
        # Registra rendimento
        Transacao.objects.create(
            conta=investimento.conta,
            tipo='RENDIMENTO',
            valor=rendimento,
            descricao=f"Rendimento de {investimento.get_tipo_display()} - R$ {rendimento:.2f}"
        )
    
    return JsonResponse({'status': 'Rendimentos simulados com sucesso'})

@login_required
def depositar(request):
    conta = request.user.conta
    
    if request.method == 'POST':
        form = DepositoForm(request.POST)
        if form.is_valid():
            valor = form.cleaned_data['valor']
            if conta.depositar(valor):
                messages.success(request, f'Depósito de R$ {valor:.2f} realizado com sucesso!')
            else:
                messages.error(request, 'Valor inválido para depósito.')
            return redirect('dashboard')
    else:
        form = DepositoForm()
    
    context = {'form': form}
    return render(request, 'investimentos/depositar.html', context)

@login_required
def sacar(request):
    conta = request.user.conta
    
    if request.method == 'POST':
        form = SaqueForm(request.POST)
        if form.is_valid():
            valor = form.cleaned_data['valor']
            if conta.sacar(valor):
                messages.success(request, f'Saque de R$ {valor:.2f} realizado com sucesso!')
            else:
                messages.error(request, 'Saldo insuficiente ou valor inválido.')
            return redirect('dashboard')
    else:
        form = SaqueForm()
    
    context = {'form': form, 'saldo': conta.saldo}
    return render(request, 'investimentos/sacar.html', context)

@login_required
def investimentos_lista(request):
    conta = request.user.conta
    investimentos = Investimento.objects.filter(conta=conta).order_by('-data_investimento')
    
    context = {
        'investimentos': investimentos,
    }
    return render(request, 'investimentos/lista.html', context)