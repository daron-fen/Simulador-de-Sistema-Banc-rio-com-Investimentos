# Banco Invest+

Simulador de sistema bancário com investimentos desenvolvido em Python com foco em Orientação a Objetos. O projeto resolve um problema real do dia a dia: controle de conta, movimentações financeiras, transferências, investimentos e histórico de operações.

## O que o programa faz

- cria contas bancárias simuladas
- realiza depósitos, saques e transferências
- aplica investimentos em renda fixa, renda variável e cofrinho
- simula rendimentos dos investimentos
- registra histórico de operações
- salva e carrega os dados em arquivo JSON

## Conceitos de POO usados

- Classes e objetos: `ContaBancaria`, `BancoSimulador`, `Transacao` e classes de investimento
- Encapsulamento: saldo, carteira e histórico protegidos por atributos privados e propriedades
- Abstração: `AtivoFinanceiro` define o contrato das classes de investimento
- Herança: `RendaFixa`, `RendaVariavel` e `Cofrinho` herdam de `AtivoFinanceiro`
- Polimorfismo: cada investimento calcula rendimento de forma diferente
- Associação/composição: uma conta possui investimentos e histórico de transações

## Arquivos principais

- [banco_invest_gui.py](banco_invest_gui.py): **Versão GUI** com Tkinter (recomendada para testes)
- [interface.py](interface.py): **Versão CLI** em linha de comando

## Como executar

Existem duas versões da aplicação:

### Versão GUI (recomendada para demonstração)
Abre uma janela gráfica com interface visual:

```bash
python banco_invest_gui.py
```

Ou:

```bash
C:/Python314/python.exe banco_invest_gui.py
```

### Versão CLI (linha de comando)
Menu interativo em terminal:

```bash
python interface.py
```

Ou:

```bash
C:/Python314/python.exe interface.py
```

## Como testar

Ambas as versões funcionam no seu sistema:

**Na versão GUI** você clica em botões para fazer operações e vê os cards atualizando em tempo real com saldo e investimentos.

**Na versão CLI** você escolhe opções no menu para fazer as mesmas operações.

Os dados ficam persistidos em `banco_invest_dados.json`, então você pode fechar e abrir o programa novamente para conferir se o estado foi mantido.

Teste:
1. Faça um depósito ou saque
2. Crie alguns investimentos (Cofrinho, Tesouro, etc)
3. Simule rendimentos por alguns dias
4. Resgate um investimento
5. Transfira valor para outra conta
6. Salve os dados e feche o programa
7. Abra novamente e veja se tudo foi restaurado


## Observação

A entrega principal recomendada para a atividade é a aplicação em Python/POO. O frontend HTML/CSS do repositório pode ser mantido como material complementar, mas o que realmente demonstra os requisitos do professor é o arquivo `interface.py`.
