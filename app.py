"""
Banco Invest+ | App Flask
Versão web do simulador de sistema bancário
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from banco_models import (
    BancoSimulador, ContaBancaria, Cofrinho, TesouroDireto, 
    PreFixado, PosFixado, formatar_moeda, decimal_seguro
)
import os

app = Flask(__name__)
app.secret_key = "banco-invest-secret-key-2026"

# Carrega banco na memória
banco = None


def get_banco():
    global banco
    if banco is None:
        banco = BancoSimulador.carregar()
    return banco


def salvar_banco():
    get_banco().salvar()


@app.before_request
def verificar_sessao():
    if 'conta_selecionada' not in session:
        contas = get_banco().nomes_contas()
        session['conta_selecionada'] = contas[0] if contas else 'Principal'


@app.route('/')
def index():
    banco = get_banco()
    contas = banco.nomes_contas()
    return render_template('index.html', contas=contas, conta_selecionada=session.get('conta_selecionada', contas[0]))


@app.route('/api/conta/<nome>')
def api_conta(nome):
    try:
        banco = get_banco()
        conta = banco.conta(nome)
        ativos = conta.carteira.ativos()
        historico = list(reversed(conta.historico[-10:]))
        
        return jsonify({
            'sucesso': True,
            'titular': conta.titular,
            'numero_conta': conta.numero_conta,
            'saldo': str(conta.saldo),
            'saldo_formatado': formatar_moeda(conta.saldo),
            'total_investido': str(conta.total_investido),
            'total_investido_formatado': formatar_moeda(conta.total_investido),
            'investimentos': [
                {
                    'indice': i,
                    'nome': inv.NOME,
                    'valor_aplicado': str(inv.valor_aplicado),
                    'valor_aplicado_formatado': formatar_moeda(inv.valor_aplicado),
                    'valor_atual': str(inv.valor_atual),
                    'valor_atual_formatado': formatar_moeda(inv.valor_atual),
                    'dias_corridos': inv.dias_corridos,
                }
                for i, inv in enumerate(ativos)
            ],
            'historico': [
                {
                    'data': l.data,
                    'tipo': l.tipo,
                    'valor': l.valor,
                    'valor_formatado': formatar_moeda(decimal_seguro(l.valor)),
                    'descricao': l.descricao,
                }
                for l in historico
            ]
        })
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 400


@app.route('/api/depositar', methods=['POST'])
def api_depositar():
    try:
        dados = request.get_json()
        conta_nome = dados.get('conta')
        valor = decimal_seguro(dados.get('valor', 0))
        
        conta = get_banco().conta(conta_nome)
        conta.depositar(valor)
        salvar_banco()
        
        return jsonify({'sucesso': True, 'mensagem': f'Depósito de {formatar_moeda(valor)} realizado.'})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 400


@app.route('/api/sacar', methods=['POST'])
def api_sacar():
    try:
        dados = request.get_json()
        conta_nome = dados.get('conta')
        valor = decimal_seguro(dados.get('valor', 0))
        
        conta = get_banco().conta(conta_nome)
        conta.sacar(valor)
        salvar_banco()
        
        return jsonify({'sucesso': True, 'mensagem': f'Saque de {formatar_moeda(valor)} realizado.'})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 400


@app.route('/api/transferir', methods=['POST'])
def api_transferir():
    try:
        dados = request.get_json()
        origem_nome = dados.get('origem')
        destino_nome = dados.get('destino')
        valor = decimal_seguro(dados.get('valor', 0))
        
        banco = get_banco()
        origem = banco.conta(origem_nome)
        destino = banco.conta(destino_nome)
        origem.transferir(valor, destino)
        salvar_banco()
        
        return jsonify({'sucesso': True, 'mensagem': f'Transferência de {formatar_moeda(valor)} realizada.'})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 400


@app.route('/api/investir', methods=['POST'])
def api_investir():
    try:
        dados = request.get_json()
        conta_nome = dados.get('conta')
        tipo = dados.get('tipo', 'COFRINHO')
        valor = decimal_seguro(dados.get('valor', 0))
        
        conta = get_banco().conta(conta_nome)
        investimento = conta.investir(tipo, valor)
        salvar_banco()
        
        return jsonify({'sucesso': True, 'mensagem': f'{investimento.NOME} criado com {formatar_moeda(valor)}.'})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 400


@app.route('/api/simular-rendimentos', methods=['POST'])
def api_simular_rendimentos():
    try:
        dados = request.get_json()
        conta_nome = dados.get('conta')
        dias = int(dados.get('dias', 1))
        
        conta = get_banco().conta(conta_nome)
        rendimento = conta.simular_rendimentos(dias)
        salvar_banco()
        
        return jsonify({'sucesso': True, 'mensagem': f'Rendimentos simulados: {formatar_moeda(rendimento)}.'})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 400


@app.route('/api/resgatar', methods=['POST'])
def api_resgatar():
    try:
        dados = request.get_json()
        conta_nome = dados.get('conta')
        indice = int(dados.get('indice', 0))
        
        conta = get_banco().conta(conta_nome)
        valor = conta.resgatar_investimento(indice)
        salvar_banco()
        
        return jsonify({'sucesso': True, 'mensagem': f'Resgatado em {formatar_moeda(valor)}.'})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 400


@app.route('/api/contas')
def api_contas():
    try:
        banco = get_banco()
        contas_info = []
        
        for nome in banco.nomes_contas():
            conta = banco.conta(nome)
            contas_info.append({
                'nome': nome,
                'titular': conta.titular,
                'saldo': str(conta.saldo),
                'saldo_formatado': formatar_moeda(conta.saldo),
                'total_investido': str(conta.total_investido),
                'total_investido_formatado': formatar_moeda(conta.total_investido),
            })
        
        return jsonify({'sucesso': True, 'contas': contas_info})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 400


@app.route('/api/selecionar-conta/<nome>')
def api_selecionar_conta(nome):
    try:
        get_banco().conta(nome)  # Valida se a conta existe
        session['conta_selecionada'] = nome
        return jsonify({'sucesso': True, 'mensagem': f'Conta {nome} selecionada.'})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
