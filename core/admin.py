from django.contrib import admin
from .models import Conta, Transacao # Adicionamos Transacao aqui

admin.site.register(Conta)
admin.site.register(Transacao) # Adicionamos esta linha