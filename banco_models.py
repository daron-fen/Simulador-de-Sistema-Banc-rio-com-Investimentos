"""
Banco Invest+ | Modelos de POO (puro Python)
Lógica de negócio independente de UI/Framework
"""

from __future__ import annotations

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import List, Optional


ARQUIVO_DADOS = Path(__file__).with_name("banco_invest_dados.json")
MOEDA = Decimal("0.01")


def decimal_seguro(valor) -> Decimal:
    """Arredonda valor para 2 casas decimais."""
    return Decimal(str(valor)).quantize(MOEDA, rounding=ROUND_HALF_UP)


def formatar_moeda(valor: Decimal) -> str:
    """Formata como moeda brasileira."""
    texto = f"{decimal_seguro(valor):,.2f}"
    return f"R$ {texto.replace(',', 'X').replace('.', ',').replace('X', '.')}"


@dataclass
class Lancamento:
    """Registro de transação."""
    data: str
    tipo: str
    valor: str
    descricao: str
    saldo_final: str


class AtivoFinanceiro(ABC):
    """Abstração para investimentos."""
    NOME = "Investimento"

    def __init__(self, valor_aplicado, dias_corridos: int = 0, valor_atual=None, ativo: bool = True):
        self.valor_aplicado = decimal_seguro(valor_aplicado)
        self.valor_atual = decimal_seguro(valor_atual if valor_atual is not None else valor_aplicado)
        self.dias_corridos = int(dias_corridos)
        self.ativo = bool(ativo)

    @abstractmethod
    def taxa_diaria(self) -> Decimal:
        raise NotImplementedError

    def simular_rendimento(self, dias: int = 1) -> Decimal:
        dias = max(1, int(dias))
        rendimento_total = Decimal("0")
        for _ in range(dias):
            if not self.ativo:
                break
            rendimento = (self.valor_atual * self.taxa_diaria()).quantize(MOEDA, rounding=ROUND_HALF_UP)
            self.valor_atual += rendimento
            self.dias_corridos += 1
            rendimento_total += rendimento
        return rendimento_total.quantize(MOEDA, rounding=ROUND_HALF_UP)

    def resgatar(self) -> Decimal:
        self.ativo = False
        return self.valor_atual.quantize(MOEDA, rounding=ROUND_HALF_UP)

    def to_dict(self) -> dict:
        return {
            "classe": self.__class__.__name__,
            "valor_aplicado": str(self.valor_aplicado),
            "valor_atual": str(self.valor_atual),
            "dias_corridos": self.dias_corridos,
            "ativo": self.ativo,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "AtivoFinanceiro":
        classes = {
            "Cofrinho": Cofrinho,
            "TesouroDireto": TesouroDireto,
            "PreFixado": PreFixado,
            "PosFixado": PosFixado,
        }
        classe = classes.get(dados.get("classe"), Cofrinho)
        return classe(
            dados.get("valor_aplicado", "0"),
            dias_corridos=dados.get("dias_corridos", 0),
            valor_atual=dados.get("valor_atual"),
            ativo=dados.get("ativo", True),
        )


class Cofrinho(AtivoFinanceiro):
    NOME = "Cofrinho"
    def taxa_diaria(self) -> Decimal:
        return (Decimal("0.105") * Decimal("1.21")) / Decimal("252")


class TesouroDireto(AtivoFinanceiro):
    NOME = "Tesouro Direto"
    def taxa_diaria(self) -> Decimal:
        return Decimal("0.115") / Decimal("252")


class PreFixado(AtivoFinanceiro):
    NOME = "Pré-fixado"
    def taxa_diaria(self) -> Decimal:
        return Decimal("0.100") / Decimal("252")


class PosFixado(AtivoFinanceiro):
    NOME = "Pós-fixado"
    def taxa_diaria(self) -> Decimal:
        base = Decimal("0.092") / Decimal("252")
        ciclo = Decimal((self.dias_corridos % 6) - 2) * Decimal("0.00004")
        taxa = base + ciclo
        return taxa if taxa > Decimal("0") else Decimal("0")


class CarteiraInvestimentos:
    """Composição: coleção de investimentos."""
    def __init__(self, investimentos: List[AtivoFinanceiro] | None = None):
        self._investimentos = investimentos or []

    @property
    def investimentos(self) -> tuple[AtivoFinanceiro, ...]:
        return tuple(self._investimentos)

    def adicionar(self, investimento: AtivoFinanceiro) -> None:
        self._investimentos.append(investimento)

    def ativos(self) -> List[AtivoFinanceiro]:
        return [inv for inv in self._investimentos if inv.ativo]

    def total_aplicado(self) -> Decimal:
        total = sum((inv.valor_aplicado for inv in self._investimentos), Decimal("0"))
        return decimal_seguro(total)

    def total_atual(self) -> Decimal:
        total = sum((inv.valor_atual for inv in self._investimentos), Decimal("0"))
        return decimal_seguro(total)

    def simular_rendimentos(self, dias: int = 1) -> Decimal:
        total = Decimal("0")
        for inv in self.ativos():
            total += inv.simular_rendimento(dias)
        return total.quantize(MOEDA, rounding=ROUND_HALF_UP)

    def resgatar(self, indice_ativo: int) -> tuple[AtivoFinanceiro, Decimal]:
        ativos = self.ativos()
        if indice_ativo < 0 or indice_ativo >= len(ativos):
            raise IndexError("Investimento inválido.")
        investimento = ativos[indice_ativo]
        valor = investimento.resgatar()
        return investimento, valor

    def to_list(self) -> list[dict]:
        return [inv.to_dict() for inv in self._investimentos]

    @classmethod
    def from_list(cls, dados: list[dict]) -> "CarteiraInvestimentos":
        investimentos = [AtivoFinanceiro.from_dict(item) for item in dados]
        return cls(investimentos)


class ContaBancaria:
    """Encapsulamento: atributos privados com @property."""
    def __init__(
        self,
        titular: str,
        saldo_inicial=0,
        numero_conta: str | None = None,
        historico: List[Lancamento] | None = None,
        carteira: CarteiraInvestimentos | None = None,
    ):
        self.titular = titular
        self.__numero_conta = numero_conta or self._gerar_numero_conta()
        self.__saldo = decimal_seguro(saldo_inicial)
        self.__historico = historico or []
        self.__carteira = carteira or CarteiraInvestimentos()

    @staticmethod
    def _gerar_numero_conta() -> str:
        return uuid.uuid4().hex[:10].upper()

    @property
    def numero_conta(self) -> str:
        return self.__numero_conta

    @property
    def saldo(self) -> Decimal:
        return self.__saldo

    @property
    def historico(self) -> tuple[Lancamento, ...]:
        return tuple(self.__historico)

    @property
    def carteira(self) -> CarteiraInvestimentos:
        return self.__carteira

    @property
    def total_investido(self) -> Decimal:
        return self.__carteira.total_aplicado()

    def _registrar(self, tipo: str, valor: Decimal, descricao: str) -> None:
        self.__historico.append(
            Lancamento(
                data=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                tipo=tipo,
                valor=str(decimal_seguro(valor)),
                descricao=descricao,
                saldo_final=str(decimal_seguro(self.__saldo)),
            )
        )

    def depositar(self, valor) -> Decimal:
        valor = decimal_seguro(valor)
        if valor <= 0:
            raise ValueError("O valor do depósito precisa ser maior que zero.")
        self.__saldo += valor
        self._registrar("DEPOSITO", valor, f"Depósito de {formatar_moeda(valor)}")
        return valor

    def sacar(self, valor) -> Decimal:
        valor = decimal_seguro(valor)
        if valor <= 0:
            raise ValueError("O valor do saque precisa ser maior que zero.")
        if valor > self.__saldo:
            raise ValueError("Saldo insuficiente para o saque.")
        self.__saldo -= valor
        self._registrar("SAQUE", valor, f"Saque de {formatar_moeda(valor)}")
        return valor

    # Correção: Novo método para respeitar o Encapsulamento da conta destino
    def _receber_transferencia(self, valor: Decimal, origem: "ContaBancaria") -> None:
        self.__saldo += valor
        self._registrar("RECEBIMENTO", valor, f"Recebimento de {origem.titular}")

    def transferir(self, valor, destino: "ContaBancaria") -> Decimal:
        valor = decimal_seguro(valor)
        if valor <= 0:
            raise ValueError("O valor da transferência precisa ser maior que zero.")
        if destino is self:
            raise ValueError("Selecione uma conta diferente para transferir.")
        if valor > self.__saldo:
            raise ValueError("Saldo insuficiente para a transferência.")
        
        self.__saldo -= valor
        self._registrar("TRANSFERENCIA", valor, f"Transferência para {destino.titular}")
        # Correção: Invocando o método da classe destino ao invés de alterar sua propriedade privada diretamente
        destino._receber_transferencia(valor, self)
        
        return valor

    def investir(self, tipo: str, valor) -> AtivoFinanceiro:
        valor = decimal_seguro(valor)
        if valor <= 0:
            raise ValueError("O valor do investimento precisa ser maior que zero.")
        if valor > self.__saldo:
            raise ValueError("Saldo insuficiente para investir.")
        mapa = {
            "COFRINHO": Cofrinho,
            "TESOURO": TesouroDireto,
            "PRE_FIXADO": PreFixado,
            "POS_FIXADO": PosFixado,
        }
        classe = mapa.get(tipo)
        if classe is None:
            raise ValueError("Tipo de investimento inválido.")
        investimento = classe(valor)
        self.__saldo -= valor
        self.__carteira.adicionar(investimento)
        self._registrar("INVESTIMENTO", valor, f"Aplicação em {investimento.NOME}")
        return investimento

    def simular_rendimentos(self, dias: int = 1) -> Decimal:
        dias = max(1, int(dias))
        rendimento = self.__carteira.simular_rendimentos(dias)
        if rendimento > 0:
            self.__saldo += rendimento
            self._registrar("RENDIMENTO", rendimento, f"Rendimentos acumulados")
        return rendimento

    def resgatar_investimento(self, indice_ativo: int) -> Decimal:
        investimento, valor = self.__carteira.resgatar(indice_ativo)
        self.__saldo += valor
        self._registrar("RESGATE", valor, f"Resgate de {investimento.NOME}")
        return valor

    def to_dict(self) -> dict:
        return {
            "titular": self.titular,
            "numero_conta": self.__numero_conta,
            "saldo": str(self.__saldo),
            "historico": [
                {
                    "data": lancamento.data,
                    "tipo": lancamento.tipo,
                    "valor": lancamento.valor,
                    "descricao": lancamento.descricao,
                    "saldo_final": lancamento.saldo_final,
                }
                for lancamento in self.__historico
            ],
            "carteira": self.__carteira.to_list(),
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "ContaBancaria":
        historico = [Lancamento(**item) for item in dados.get("historico", [])]
        carteira = CarteiraInvestimentos.from_list(dados.get("carteira", []))
        return cls(
            titular=dados.get("titular", "Conta"),
            saldo_inicial=dados.get("saldo", "0"),
            numero_conta=dados.get("numero_conta"),
            historico=historico,
            carteira=carteira,
        )


class BancoSimulador:
    """Associação: múltiplas contas."""
    def __init__(self, contas: dict[str, ContaBancaria] | None = None):
        self._contas = contas or {}

    @property
    def contas(self) -> dict[str, ContaBancaria]:
        return self._contas

    def nomes_contas(self) -> list[str]:
        return list(self._contas.keys())

    def conta(self, nome: str) -> ContaBancaria:
        return self._contas[nome]

    def to_dict(self) -> dict:
        return {nome: conta.to_dict() for nome, conta in self._contas.items()}

    @classmethod
    def criar_padrao(cls) -> "BancoSimulador":
        contas = {
            "Principal": ContaBancaria("Ícaro", "1000.00"),
            "Reserva": ContaBancaria("Reserva Financeira", "500.00"),
            "Investimentos": ContaBancaria("Carteira de Investimentos", "2000.00"),
        }
        return cls(contas)

    @classmethod
    def from_dict(cls, dados: dict) -> "BancoSimulador":
        contas = {nome: ContaBancaria.from_dict(info) for nome, info in dados.items()}
        return cls(contas)

    @classmethod
    def carregar(cls) -> "BancoSimulador":
        if ARQUIVO_DADOS.exists():
            try:
                with ARQUIVO_DADOS.open("r", encoding="utf-8") as arquivo:
                    dados = json.load(arquivo)
                return cls.from_dict(dados)
            except Exception:
                return cls.criar_padrao()
        return cls.criar_padrao()

    def salvar(self) -> None:
        with ARQUIVO_DADOS.open("w", encoding="utf-8") as arquivo:
            json.dump(self.to_dict(), arquivo, ensure_ascii=False, indent=2)