from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
import uuid

class Conta(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    numero_conta = models.CharField(max_length=20, unique=True, editable=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.numero_conta:
            self.numero_conta = self.gerar_numero_conta()
        super().save(*args, **kwargs)
    
    def gerar_numero_conta(self):
        return f"{uuid.uuid4().hex[:10].upper()}"
    
    def __str__(self):
        return f"Conta de {self.usuario.username}"
    
    def depositar(self, valor):
        if valor > 0:
            self.saldo += Decimal(str(valor))
            self.save()
            Transacao.objects.create(
                conta=self,
                tipo='DEPOSITO',
                valor=valor,
                descricao=f"Depósito de R$ {valor:.2f}"
            )
            return True
        return False
    
    def sacar(self, valor):
        if 0 < valor <= self.saldo:
            self.saldo -= Decimal(str(valor))
            self.save()
            Transacao.objects.create(
                conta=self,
                tipo='SAQUE',
                valor=valor,
                descricao=f"Saque de R$ {valor:.2f}"
            )
            return True
        return False

class Transacao(models.Model):
    TIPO_CHOICES = [
        ('DEPOSITO', 'Depósito'),
        ('SAQUE', 'Saque'),
        ('INVESTIMENTO', 'Investimento'),
        ('RESGATE', 'Resgate'),
        ('RENDIMENTO', 'Rendimento'),
    ]
    
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    descricao = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.tipo} - R$ {self.valor:.2f} - {self.data}"

class Investimento(models.Model):
    TIPO_CHOICES = [
        ('COFRINHO', 'Cofrinho'),
        ('TESOURO', 'Tesouro Direto'),
        ('PRE_FIXADO', 'Pré-fixado'),
        ('POS_FIXADO', 'Pós-fixado'),
    ]
    
    SITUACAO_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('RESGATADO', 'Resgatado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor_investido = models.DecimalField(max_digits=15, decimal_places=2)
    valor_atual = models.DecimalField(max_digits=15, decimal_places=2)
    data_investimento = models.DateTimeField(auto_now_add=True)
    data_resgate = models.DateTimeField(null=True, blank=True)
    situacao = models.CharField(max_length=20, choices=SITUACAO_CHOICES, default='ATIVO')
    
    # Campos específicos
    taxa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vencimento = models.DateField(null=True, blank=True)
    indice = models.CharField(max_length=20, null=True, blank=True)
    
    def __str__(self):
        return f"{self.tipo} - {self.conta.usuario.username} - R$ {self.valor_investido:.2f}"

class ConfiguracaoInvestimento(models.Model):
    """
    Configurações dos investimentos - simulando dados de mercado
    """
    TIPO_CHOICES = [
        ('COFRINHO', 'Cofrinho'),
        ('TESOURO', 'Tesouro Direto'),
        ('PRE_FIXADO', 'Pré-fixado'),
        ('POS_FIXADO', 'Pós-fixado'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, unique=True)
    taxa_base = models.DecimalField(max_digits=5, decimal_places=2)
    descricao = models.TextField()
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.tipo} - {self.taxa_base}%"