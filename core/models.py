from django.db import models
from django.contrib.auth.models import User

class Conta(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Conta de {self.usuario.username} - Saldo: R$ {self.saldo}"


class Transacao(models.Model):
    # Criamos as opções de tipos de movimentação
    TIPO_CHOICES = [
        ('DEPOSITO', 'Depósito'),
        ('SAQUE', 'Saque'),
    ]

    conta = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='transacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True) # Salva o dia e horário exatos automaticamente

    def __str__(self):
        return f"{self.get_tipo_display()} de R$ {self.valor} - {self.conta.usuario.username}"