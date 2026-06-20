from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


ARQUIVO_DADOS = Path(__file__).with_name("dados_banco.json")


@dataclass
class Transacao:
    tipo: str
    valor: float
    descricao: str
    data: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, dados: dict) -> "Transacao":
        return cls(
            tipo=dados.get("tipo", "Desconhecido"),
            valor=float(dados.get("valor", 0.0)),
            descricao=dados.get("descricao", ""),
            data=dados.get("data", ""),
        )


class AtivoFinanceiro(ABC):
    def __init__(self, nome: str, valor_investido: float):
        self.nome = nome
        self._valor_investido = 0.0
        self.valor_investido = valor_investido

    @property
    def valor_investido(self) -> float:
        return self._valor_investido

    @valor_investido.setter
    def valor_investido(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("O valor do investimento deve ser maior que zero.")
        self._valor_investido = float(valor)

    @abstractmethod
    def calcular_rendimento(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def tipo(self) -> str:
        raise NotImplementedError

    def valor_resgate(self) -> float:
        return round(self._valor_investido + self.calcular_rendimento(), 2)

    def to_dict(self) -> dict:
        return {
            "classe": self.__class__.__name__,
            "nome": self.nome,
            "valor_investido": self.valor_investido,
        }


class RendaFixa(AtivoFinanceiro):
    def __init__(self, nome: str, valor_investido: float, taxa_anual: float = 10.75):
        super().__init__(nome, valor_investido)
        self.taxa_anual = taxa_anual

    def calcular_rendimento(self) -> float:
        return round(self.valor_investido * (self.taxa_anual / 100), 2)

    def tipo(self) -> str:
        return "Renda Fixa"

    def to_dict(self) -> dict:
        dados = super().to_dict()
        dados["taxa_anual"] = self.taxa_anual
        return dados


class RendaVariavel(AtivoFinanceiro):
    def __init__(self, nome: str, valor_investido: float, variacao_percentual: float = 12.8):
        super().__init__(nome, valor_investido)
        self.variacao_percentual = variacao_percentual

    def calcular_rendimento(self) -> float:
        return round(self.valor_investido * (self.variacao_percentual / 100), 2)

    def tipo(self) -> str:
        return "Renda Variável"

    def to_dict(self) -> dict:
        dados = super().to_dict()
        dados["variacao_percentual"] = self.variacao_percentual
        return dados


class Cofrinho(AtivoFinanceiro):
    def __init__(self, nome: str, valor_investido: float):
        super().__init__(nome, valor_investido)

    def calcular_rendimento(self) -> float:
        return round(self.valor_investido * 0.050, 2)

    def tipo(self) -> str:
        return "Reserva / Cofrinho"


class ContaBancaria:
    def __init__(self, titular: str, saldo_inicial: float = 0.0):
        self.titular = titular
        self._saldo = float(saldo_inicial)
        self._investimentos: List[AtivoFinanceiro] = []
        self._historico: List[Transacao] = []

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def total_investido(self) -> float:
        return round(sum(investimento.valor_investido for investimento in self._investimentos), 2)

    @property
    def investimentos_ativos(self) -> List[AtivoFinanceiro]:
        return list(self._investimentos)

    @property
    def historico(self) -> List[Transacao]:
        return list(self._historico)

    def _registrar(self, tipo: str, valor: float, descricao: str) -> None:
        self._historico.append(
            Transacao(
                tipo=tipo,
                valor=round(float(valor), 2),
                descricao=descricao,
                data=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            )
        )

    def depositar(self, valor: float) -> bool:
        if valor <= 0:
            return False
        self._saldo = round(self._saldo + float(valor), 2)
        self._registrar("DEPOSITO", valor, f"Depósito de R$ {valor:.2f}")
        return True

    def sacar(self, valor: float) -> bool:
        if valor <= 0 or valor > self._saldo:
            return False
        self._saldo = round(self._saldo - float(valor), 2)
        self._registrar("SAQUE", valor, f"Saque de R$ {valor:.2f}")
        return True

    def _receber_transferencia(self, valor: float, origem: str) -> None:
        self._saldo = round(self._saldo + float(valor), 2)
        self._registrar("TRANSFERENCIA", valor, f"Transferência recebida de {origem}")

    def transferir(self, valor: float, conta_destino: "ContaBancaria") -> bool:
        if valor <= 0 or valor > self._saldo:
            return False
        if conta_destino is self:
            return False
        self._saldo = round(self._saldo - float(valor), 2)
        self._registrar("TRANSFERENCIA", valor, f"Transferência enviada para {conta_destino.titular}")
        conta_destino._receber_transferencia(valor, self.titular)
        return True

    def investir(self, ativo: AtivoFinanceiro) -> bool:
        if ativo.valor_investido > self._saldo:
            return False
        self._saldo = round(self._saldo - ativo.valor_investido, 2)
        self._investimentos.append(ativo)
        self._registrar(
            "INVESTIMENTO",
            ativo.valor_investido,
            f"Investimento em {ativo.nome} ({ativo.tipo()}) de R$ {ativo.valor_investido:.2f}",
        )
        return True

    def resgatar_investimento(self, indice: int) -> Optional[AtivoFinanceiro]:
        if indice < 0 or indice >= len(self._investimentos):
            return None
        ativo = self._investimentos.pop(indice)
        valor_resgate = ativo.valor_resgate()
        self._saldo = round(self._saldo + valor_resgate, 2)
        self._registrar(
            "RESGATE",
            valor_resgate,
            f"Resgate de {ativo.nome} ({ativo.tipo()}) no valor de R$ {valor_resgate:.2f}",
        )
        return ativo

    def simular_rendimentos(self) -> float:
        total = 0.0
        for ativo in self._investimentos:
            rendimento = ativo.calcular_rendimento()
            total += rendimento
        if total > 0:
            self._saldo = round(self._saldo + total, 2)
            self._registrar("RENDIMENTO", total, f"Rendimento automático de R$ {total:.2f}")
        return round(total, 2)

    def to_dict(self) -> dict:
        return {
            "titular": self.titular,
            "saldo": self._saldo,
            "investimentos": [ativo.to_dict() for ativo in self._investimentos],
            "historico": [transacao.to_dict() for transacao in self._historico],
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "ContaBancaria":
        conta = cls(dados.get("titular", "Desconhecido"), dados.get("saldo", 0.0))
        for investimento in dados.get("investimentos", []):
            classe = investimento.get("classe")
            nome = investimento.get("nome", "Investimento")
            valor = investimento.get("valor_investido", 0.0)
            
            if classe == "RendaFixa":
                ativo = RendaFixa(nome, valor, investimento.get("taxa_anual", 10.75))
            elif classe == "RendaVariavel":
                ativo = RendaVariavel(nome, valor, investimento.get("variacao_percentual", 12.8))
            else:
                ativo = Cofrinho(nome, valor)
            conta._investimentos.append(ativo)
            
        conta._historico = [Transacao.from_dict(item) for item in dados.get("historico", [])]
        return conta


class BancoInvestApp:
    def __init__(self):
        self.conta = ContaBancaria(titular="Ícaro", saldo_inicial=1000.0)
        self.contas_extras: Dict[str, ContaBancaria] = {
            "Maria": ContaBancaria("Maria", 650.0),
            "João": ContaBancaria("João", 1200.0),
        }
        self.carregar_dados()

    def salvar_dados(self) -> None:
        dados = {
            "conta_principal": self.conta.to_dict(),
            "contas_extras": {nome: conta.to_dict() for nome, conta in self.contas_extras.items()},
        }
        ARQUIVO_DADOS.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    def carregar_dados(self) -> None:
        if not ARQUIVO_DADOS.exists():
            return
        try:
            dados = json.loads(ARQUIVO_DADOS.read_text(encoding="utf-8"))
            self.conta = ContaBancaria.from_dict(dados.get("conta_principal", {}))
            contas_extras = {}
            for nome, conta_dados in dados.get("contas_extras", {}).items():
                contas_extras[nome] = ContaBancaria.from_dict(conta_dados)
            if contas_extras:
                self.contas_extras = contas_extras
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            pass

    def ler_valor(self, mensagem: str) -> Optional[float]:
        texto = input(mensagem).strip().replace(",", ".")
        try:
            valor = float(texto)
            if valor <= 0:
                print("O valor precisa ser maior que zero.")
                return None
            return valor
        except ValueError:
            print("Valor inválido.")
            return None

    def escolher_conta_destino(self) -> Optional[ContaBancaria]:
        print("Contas disponíveis para transferência:")
        nomes = list(self.contas_extras.keys())
        for indice, nome in enumerate(nomes, start=1):
            print(f"{indice}. {nome}")
        escolha = input("Escolha o número da conta: ").strip()
        if not escolha.isdigit():
            print("Escolha inválida.")
            return None
        indice = int(escolha) - 1
        if indice < 0 or indice >= len(nomes):
            print("Escolha inválida.")
            return None
        return self.contas_extras[nomes[indice]]

    def mostrar_resumo(self) -> None:
        print("\n=== RESUMO DA CONTA ===")
        print(f"Titular: {self.conta.titular}")
        print(f"Saldo: R$ {self.conta.saldo:.2f}")
        print(f"Total investido: R$ {self.conta.total_investido:.2f}")
        print(f"Quantidade de investimentos: {len(self.conta.investimentos_ativos)}")
        print("\nInvestimentos ativos:")
        if not self.conta.investimentos_ativos:
            print("- Nenhum investimento ativo")
        else:
            for indice, ativo in enumerate(self.conta.investimentos_ativos, start=1):
                print(
                    f"{indice}. {ativo.nome} | {ativo.tipo()} | R$ {ativo.valor_investido:.2f} | "
                    f"Rendimento estimado: R$ {ativo.calcular_rendimento():.2f}"
                )

    def mostrar_historico(self) -> None:
        print("\n=== HISTÓRICO ===")
        if not self.conta.historico:
            print("Sem movimentações registradas.")
            return
        for transacao in self.conta.historico[-10:]:
            print(f"[{transacao.data}] {transacao.tipo} - R$ {transacao.valor:.2f} - {transacao.descricao}")

    def menu(self) -> None:
        while True:
            print("\n========================================")
            print("     BANCO INVEST+ | SIMULADOR POO")
            print("========================================")
            print("1. Ver resumo da conta")
            print("2. Depositar")
            print("3. Sacar")
            print("4. Investir em renda fixa")
            print("5. Investir em renda variável")
            print("6. Investir no cofrinho")
            print("7. Transferir para outra conta")
            print("8. Resgatar investimento")
            print("9. Simular rendimentos")
            print("10. Ver histórico")
            print("11. Salvar dados")
            print("0. Sair")

            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self.mostrar_resumo()
            elif opcao == "2":
                valor = self.ler_valor("Valor do depósito: ")
                if valor is not None:
                    if self.conta.depositar(valor):
                        print("Depósito realizado com sucesso.")
                    else:
                        print("Não foi possível realizar o depósito.")
            elif opcao == "3":
                valor = self.ler_valor("Valor do saque: ")
                if valor is not None:
                    if self.conta.sacar(valor):
                        print("Saque realizado com sucesso.")
                    else:
                        print("Saldo insuficiente ou valor inválido.")
            elif opcao == "4":
                valor = self.ler_valor("Valor para investir em renda fixa: ")
                if valor is not None:
                    nome = input("Nome do investimento (ex.: Tesouro Direto): ").strip() or "Tesouro Direto"
                    ativo = RendaFixa(nome, valor)
                    if self.conta.investir(ativo):
                        print(f"Investimento em renda fixa realizado: R$ {valor:.2f}.")
                    else:
                        print("Saldo insuficiente para investir.")
            elif opcao == "5":
                valor = self.ler_valor("Valor para investir em renda variável: ")
                if valor is not None:
                    nome = input("Nome do investimento (ex.: Ações e FIIs): ").strip() or "Ações e FIIs"
                    ativo = RendaVariavel(nome, valor)
                    if self.conta.investir(ativo):
                        print(f"Investimento em renda variável realizado: R$ {valor:.2f}.")
                    else:
                        print("Saldo insuficiente para investir.")
            elif opcao == "6":
                valor = self.ler_valor("Valor para o cofrinho: ")
                if valor is not None:
                    nome = input("Nome da reserva: ").strip() or "Reserva de emergência"
                    ativo = Cofrinho(nome, valor)
                    if self.conta.investir(ativo):
                        print(f"Reserva criada: R$ {valor:.2f}.")
                    else:
                        print("Saldo insuficiente para reservar esse valor.")
            elif opcao == "7":
                valor = self.ler_valor("Valor para transferir: ")
                if valor is not None:
                    conta_destino = self.escolher_conta_destino()
                    if conta_destino is not None:
                        if self.conta.transferir(valor, conta_destino):
                            print(f"Transferência concluída para {conta_destino.titular}.")
                        else:
                            print("Não foi possível transferir.")
            elif opcao == "8":
                if not self.conta.investimentos_ativos:
                    print("Não há investimentos para resgatar.")
                    continue
                self.mostrar_resumo()
                escolha = input("Digite o número do investimento para resgatar: ").strip()
                
                if escolha.isdigit():
                    indice = int(escolha) - 1
                    if 0 <= indice < len(self.conta.investimentos_ativos):
                        investimento = self.conta.resgatar_investimento(indice)
                        print(f"Resgate realizado em {investimento.nome}.")
                    else:
                        print("Índice de investimento inválido. Escolha um número da lista.")
                else:
                    print("Escolha inválida. Digite apenas números.")
                    
            elif opcao == "9":
                rendimento = self.conta.simular_rendimentos()
                print(f"Rendimentos simulados. Total creditado: R$ {rendimento:.2f}")
            elif opcao == "10":
                self.mostrar_historico()
            elif opcao == "11":
                self.salvar_dados()
                print(f"Dados salvos em {ARQUIVO_DADOS.name}.")
            elif opcao == "0":
                self.salvar_dados()
                print("Saindo do sistema. Dados salvos.")
                break
            else:
                print("Opção inválida.")


if __name__ == "__main__":
    BancoInvestApp().menu()