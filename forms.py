from django import forms
from .models import Investimento

class InvestimentoForm(forms.Form):
    TIPO_CHOICES = [
        ('COFRINHO', 'Cofrinho - 121% do CDI'),
        ('TESOURO', 'Tesouro Direto'),
        ('PRE_FIXADO', 'Pré-fixado'),
        ('POS_FIXADO', 'Pós-fixado'),
    ]
    
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, label='Tipo de Investimento')
    valor = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=1.00,
        label='Valor',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def clean_valor(self):
        valor = self.cleaned_data['valor']
        if valor <= 0:
            raise forms.ValidationError('O valor deve ser positivo.')
        return valor

class DepositoForm(forms.Form):
    valor = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=1.00,
        label='Valor do Depósito',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def clean_valor(self):
        valor = self.cleaned_data['valor']
        if valor <= 0:
            raise forms.ValidationError('O valor deve ser positivo.')
        return valor

class SaqueForm(forms.Form):
    valor = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=1.00,
        label='Valor do Saque',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def clean_valor(self):
        valor = self.cleaned_data['valor']
        if valor <= 0:
            raise forms.ValidationError('O valor deve ser positivo.')
        return valor