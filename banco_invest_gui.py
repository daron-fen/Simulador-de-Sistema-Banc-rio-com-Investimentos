"""
Banco Invest+ | Simulador de Sistema Bancário com Investimentos
Versão GUI Tkinter com Orientação a Objetos

Conceitos de POO aplicados:
- Abstração: AtivoFinanceiro (classe abstrata)
- Herança: RendaFixa, RendaVariavel, Cofrinho herdam de AtivoFinanceiro
- Encapsulamento: atributos privados e propriedades (@property)
- Polimorfismo: cada investimento calcula rendimento diferente
- Composição: ContaBancaria compõe CarteiraInvestimentos
- Associação: BancoSimulador associa múltiplas contas
"""

from __future__ import annotations

import json
import uuid
import tkinter as tk
from tkinter import messagebox, ttk
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import List, Optional


ARQUIVO_DADOS = Path(__file__).with_name("banco_invest_dados.json")
MOEDA = Decimal("0.01")


def decimal_seguro(valor) -> Decimal:
    """Arredonda valor para 2 casas decimais com segurança."""
    return Decimal(str(valor)).quantize(MOEDA, rounding=ROUND_HALF_UP)


def formatar_moeda(valor: Decimal) -> str:
    """Formata Decimal como moeda brasileira."""
    texto = f"{decimal_seguro(valor):,.2f}"
    return f"R$ {texto.replace(',', 'X').replace('.', ',').replace('X', '.')}"


@dataclass
class Lancamento:
    """Registro de transação na conta."""
    data: str
    tipo: str
    valor: str
    descricao: str
    saldo_final: str


class AtivoFinanceiro(ABC):
    """
    Classe abstrata que define contrato para investimentos.
    Demonstra ABSTRAÇÃO e HERANÇA.
    """
    NOME = "Investimento"

    def __init__(self, valor_aplicado, dias_corridos: int = 0, valor_atual=None, ativo: bool = True):
        self.valor_aplicado = decimal_seguro(valor_aplicado)
        self.valor_atual = decimal_seguro(valor_atual if valor_atual is not None else valor_aplicado)
        self.dias_corridos = int(dias_corridos)
        self.ativo = bool(ativo)

    @abstractmethod
    def taxa_diaria(self) -> Decimal:
        """Retorna a taxa diária de rendimento (método abstrato)."""
        raise NotImplementedError

    def simular_rendimento(self, dias: int = 1) -> Decimal:
        """Simula rendimento por dias e atualiza o valor atual."""
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
        """Marca como não ativo e retorna o valor atual."""
        self.ativo = False
        return self.valor_atual.quantize(MOEDA, rounding=ROUND_HALF_UP)

    def to_dict(self) -> dict:
        """Serializa para dicionário (persistência)."""
        return {
            "classe": self.__class__.__name__,
            "valor_aplicado": str(self.valor_aplicado),
            "valor_atual": str(self.valor_atual),
            "dias_corridos": self.dias_corridos,
            "ativo": self.ativo,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "AtivoFinanceiro":
        """Desserializa de dicionário."""
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
    """Cofrinho com rendimento de 121% do CDI (POLIMORFISMO)."""
    NOME = "Cofrinho"

    def taxa_diaria(self) -> Decimal:
        cdi_anual = Decimal("0.105")
        retorno = (cdi_anual * Decimal("1.21")) / Decimal("252")
        return retorno


class TesouroDireto(AtivoFinanceiro):
    """Tesouro Direto com taxa anual de 11.5% (POLIMORFISMO)."""
    NOME = "Tesouro Direto"

    def taxa_diaria(self) -> Decimal:
        return Decimal("0.115") / Decimal("252")


class PreFixado(AtivoFinanceiro):
    """Investimento Pré-fixado com taxa de 10% ao ano (POLIMORFISMO)."""
    NOME = "Pré-fixado"

    def taxa_diaria(self) -> Decimal:
        return Decimal("0.100") / Decimal("252")


class PosFixado(AtivoFinanceiro):
    """Investimento Pós-fixado com variação simulada (POLIMORFISMO)."""
    NOME = "Pós-fixado"

    def taxa_diaria(self) -> Decimal:
        base = Decimal("0.092") / Decimal("252")
        ciclo = Decimal((self.dias_corridos % 6) - 2) * Decimal("0.00004")
        taxa = base + ciclo
        return taxa if taxa > Decimal("0") else Decimal("0")


class CarteiraInvestimentos:
    """
    Compõe uma coleção de investimentos (COMPOSIÇÃO).
    Demonstra ENCAPSULAMENTO com lista privada de investimentos.
    """
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
        total_rendimento = Decimal("0")
        for investimento in self.ativos():
            total_rendimento += investimento.simular_rendimento(dias)
        return total_rendimento.quantize(MOEDA, rounding=ROUND_HALF_UP)

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
    """
    Classe que modela uma conta bancária (ENCAPSULAMENTO).
    Demonstra atributos privados (__saldo, __carteira) com propriedades.
    """
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

    def transferir(self, valor, destino: "ContaBancaria") -> Decimal:
        valor = decimal_seguro(valor)
        if valor <= 0:
            raise ValueError("O valor da transferência precisa ser maior que zero.")
        if destino is self:
            raise ValueError("Selecione uma conta diferente para transferir.")
        if valor > self.__saldo:
            raise ValueError("Saldo insuficiente para a transferência.")

        self.__saldo -= valor
        destino._ContaBancaria__saldo += valor
        self._registrar(
            "TRANSFERENCIA",
            valor,
            f"Transferência para {destino.titular} ({destino.numero_conta})",
        )
        destino._registrar(
            "RECEBIMENTO",
            valor,
            f"Recebimento de {self.titular} ({self.numero_conta})",
        )
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
        self._registrar(
            "INVESTIMENTO",
            valor,
            f"Aplicação em {investimento.NOME}",
        )
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
    """
    Classe que gerencia múltiplas contas (ASSOCIAÇÃO).
    Demonstra padrão similar a um banco com várias contas.
    """
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


class BancoInvestApp:
    """Aplicação GUI Tkinter para o simulador bancário."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Banco Invest+ | Simulador Bancário com Investimentos")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#07111f")

        self.banco = BancoSimulador.carregar()

        self.conta_var = tk.StringVar(value=self.banco.nomes_contas()[0])
        self.conta_destino_var = tk.StringVar(value=self.banco.nomes_contas()[-1])
        self.investimento_var = tk.StringVar(value="COFRINHO")
        self.valor_var = tk.StringVar()
        self.dias_var = tk.StringVar(value="1")

        self._configurar_estilo()
        self._criar_interface()
        self.atualizar_tudo()

    def _configurar_estilo(self):
        self.cor_bg = "#07111f"
        self.cor_card = "#0c1729"
        self.cor_card_claro = "#13233d"
        self.cor_texto = "#e8eefc"
        self.cor_muted = "#9ca9c7"
        self.cor_primary = "#2f80ed"
        self.cor_success = "#29c28f"

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=self.cor_card_claro, background=self.cor_card_claro, foreground=self.cor_texto)
        style.configure("Treeview", background=self.cor_card, fieldbackground=self.cor_card, foreground=self.cor_texto)
        style.map("Treeview", background=[("selected", self.cor_primary)], foreground=[("selected", "white")])

    def _criar_interface(self):
        # Cabeçalho
        topo = tk.Frame(self.root, bg=self.cor_bg)
        topo.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(topo, text="Banco Invest+", font=("Inter", 22, "bold"), bg=self.cor_bg, fg=self.cor_primary).pack(anchor="w")
        tk.Label(topo, text="Simulador de sistema bancário com investimentos em POO", font=("Inter", 10), bg=self.cor_bg, fg=self.cor_muted).pack(anchor="w")

        # Botões de ação top
        botoes_frame = tk.Frame(topo, bg=self.cor_bg)
        botoes_frame.pack(anchor="e", pady=(8, 0))
        tk.Button(botoes_frame, text="Salvar", command=self.salvar_dados, bg=self.cor_primary, fg="white", bd=0, font=("Inter", 10, "bold")).pack(side="right", padx=(8, 0))
        tk.Button(botoes_frame, text="Carregar", command=self.carregar_dados, bg=self.cor_card_claro, fg=self.cor_texto, bd=0, font=("Inter", 10, "bold")).pack(side="right")

        # Resumo de contas
        resumo_frame = tk.Frame(self.root, bg=self.cor_bg)
        resumo_frame.pack(fill="x", padx=20, pady=(0, 12))

        self.card1 = self._criar_card_conta(resumo_frame, 0)
        self.card1.pack(side="left", expand=True, fill="both", padx=(0, 6))

        self.card2 = self._criar_card_conta(resumo_frame, 1)
        self.card2.pack(side="left", expand=True, fill="both", padx=(6, 6))

        self.card3 = self._criar_card_conta(resumo_frame, 2)
        self.card3.pack(side="left", expand=True, fill="both", padx=(6, 0))

        # Corpo principal
        corpo = tk.Frame(self.root, bg=self.cor_bg)
        corpo.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Painel de operações
        painel_op = tk.Frame(corpo, bg=self.cor_card)
        painel_op.pack(side="left", fill="y", padx=(0, 12))

        tk.Label(painel_op, text="Operações", bg=self.cor_card, fg=self.cor_texto, font=("Inter", 13, "bold")).pack(anchor="w", padx=14, pady=(12, 8))

        tk.Label(painel_op, text="Conta", bg=self.cor_card, fg=self.cor_muted, font=("Inter", 9)).pack(anchor="w", padx=14)
        self.combo_conta = ttk.Combobox(painel_op, textvariable=self.conta_var, state="readonly", values=self.banco.nomes_contas(), width=24)
        self.combo_conta.pack(fill="x", padx=14, pady=(2, 8))
        self.combo_conta.bind("<<ComboboxSelected>>", lambda _: self.atualizar_tudo())

        tk.Label(painel_op, text="Transferir para", bg=self.cor_card, fg=self.cor_muted, font=("Inter", 9)).pack(anchor="w", padx=14)
        ttk.Combobox(painel_op, textvariable=self.conta_destino_var, state="readonly", values=self.banco.nomes_contas(), width=24).pack(fill="x", padx=14, pady=(2, 8))

        tk.Label(painel_op, text="Tipo de investimento", bg=self.cor_card, fg=self.cor_muted, font=("Inter", 9)).pack(anchor="w", padx=14)
        ttk.Combobox(painel_op, textvariable=self.investimento_var, state="readonly", values=["COFRINHO", "TESOURO", "PRE_FIXADO", "POS_FIXADO"], width=24).pack(fill="x", padx=14, pady=(2, 8))

        tk.Label(painel_op, text="Valor (R$)", bg=self.cor_card, fg=self.cor_muted, font=("Inter", 9)).pack(anchor="w", padx=14)
        tk.Entry(painel_op, textvariable=self.valor_var, bg=self.cor_card_claro, fg=self.cor_texto, bd=0, justify="center", font=("Inter", 11)).pack(fill="x", padx=14, pady=(2, 8), ipady=5)

        tk.Label(painel_op, text="Dias", bg=self.cor_card, fg=self.cor_muted, font=("Inter", 9)).pack(anchor="w", padx=14)
        tk.Entry(painel_op, textvariable=self.dias_var, bg=self.cor_card_claro, fg=self.cor_texto, bd=0, justify="center", font=("Inter", 11)).pack(fill="x", padx=14, pady=(2, 10), ipady=5)

        # Botões de operação
        botoes_ops = [
            ("Depositar", self.depositar, self.cor_primary),
            ("Sacar", self.sacar, self.cor_card_claro),
            ("Transferir", self.transferir, self.cor_card_claro),
            ("Investir", self.investir, self.cor_success),
            ("Simular Rendimento", self.simular_rendimentos, self.cor_card_claro),
            ("Resgatar", self.resgatar, self.cor_card_claro),
        ]

        for texto, cmd, cor in botoes_ops:
            tk.Button(painel_op, text=texto, command=cmd, bg=cor, fg="white", bd=0, font=("Inter", 10, "bold")).pack(fill="x", padx=14, pady=(0, 6), ipady=5)

        # Painel de detalhes
        painel_det = tk.Frame(corpo, bg=self.cor_bg)
        painel_det.pack(side="left", fill="both", expand=True)

        # Histórico
        frame_hist = tk.Frame(painel_det, bg=self.cor_card)
        frame_hist.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(frame_hist, text="Histórico", bg=self.cor_card, fg=self.cor_texto, font=("Inter", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 8))
        self.lst_historico = tk.Listbox(frame_hist, bg=self.cor_card, fg=self.cor_texto, bd=0, highlightthickness=0, activestyle="none", font=("Inter", 8))
        self.lst_historico.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        # Investimentos
        frame_inv = tk.Frame(painel_det, bg=self.cor_card)
        frame_inv.pack(side="left", fill="both", expand=True, padx=(8, 0))

        tk.Label(frame_inv, text="Investimentos Ativos", bg=self.cor_card, fg=self.cor_texto, font=("Inter", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 8))
        colunas = ("Tipo", "Valor", "Dias")
        self.tree_inv = ttk.Treeview(frame_inv, columns=colunas, show="headings", height=14)
        for col in colunas:
            self.tree_inv.heading(col, text=col)
            self.tree_inv.column(col, width=80, anchor="center")
        self.tree_inv.pack(fill="both", expand=True, padx=14, pady=(0, 12))

    def _criar_card_conta(self, master, indice: int):
        nomes = self.banco.nomes_contas()
        if indice >= len(nomes):
            return tk.Frame(master, bg=self.cor_card)

        conta = self.banco.conta(nomes[indice])
        card = tk.Frame(master, bg=self.cor_card, bd=1, relief="solid", highlightthickness=0)

        tk.Label(card, text=nomes[indice], bg=self.cor_card, fg=self.cor_primary, font=("Inter", 11, "bold")).pack(anchor="w", padx=14, pady=(10, 2))
        tk.Label(card, text=f"{conta.titular}", bg=self.cor_card, fg=self.cor_muted, font=("Inter", 8)).pack(anchor="w", padx=14)

        label_saldo = tk.Label(card, text="", bg=self.cor_card, fg=self.cor_texto, font=("Inter", 16, "bold"))
        label_saldo.pack(anchor="w", padx=14, pady=(8, 2))

        label_investido = tk.Label(card, text="", bg=self.cor_card, fg=self.cor_success, font=("Inter", 9))
        label_investido.pack(anchor="w", padx=14, pady=(0, 10))

        card._label_saldo = label_saldo
        card._label_investido = label_investido
        card._indice = indice
        return card

    def conta_selecionada(self) -> ContaBancaria:
        return self.banco.conta(self.conta_var.get())

    def ler_valor(self) -> Decimal:
        texto = self.valor_var.get().strip().replace(",", ".")
        if not texto:
            raise ValueError("Informe um valor.")
        return decimal_seguro(texto)

    def ler_dias(self) -> int:
        texto = self.dias_var.get().strip()
        return max(1, int(texto) if texto.isdigit() else 1)

    def depositar(self):
        try:
            valor = self.ler_valor()
            self.conta_selecionada().depositar(valor)
            self.banco.salvar()
            self.atualizar_tudo()
            messagebox.showinfo("Sucesso", f"Depósito de {formatar_moeda(valor)} realizado.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def sacar(self):
        try:
            valor = self.ler_valor()
            self.conta_selecionada().sacar(valor)
            self.banco.salvar()
            self.atualizar_tudo()
            messagebox.showinfo("Sucesso", f"Saque de {formatar_moeda(valor)} realizado.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def transferir(self):
        try:
            valor = self.ler_valor()
            origem = self.conta_selecionada()
            destino = self.banco.conta(self.conta_destino_var.get())
            origem.transferir(valor, destino)
            self.banco.salvar()
            self.atualizar_tudo()
            messagebox.showinfo("Sucesso", f"Transferência de {formatar_moeda(valor)} concluída.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def investir(self):
        try:
            valor = self.ler_valor()
            inv = self.conta_selecionada().investir(self.investimento_var.get(), valor)
            self.banco.salvar()
            self.atualizar_tudo()
            messagebox.showinfo("Sucesso", f"{inv.NOME} criado com {formatar_moeda(valor)}.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def simular_rendimentos(self):
        try:
            dias = self.ler_dias()
            rend = self.conta_selecionada().simular_rendimentos(dias)
            self.banco.salvar()
            self.atualizar_tudo()
            messagebox.showinfo("Sucesso", f"Rendimentos simulados: {formatar_moeda(rend)}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def resgatar(self):
        try:
            selecionado = self.tree_inv.selection()
            if not selecionado:
                raise ValueError("Selecione um investimento.")
            indice = int(selecionado[0])
            valor = self.conta_selecionada().resgatar_investimento(indice)
            self.banco.salvar()
            self.atualizar_tudo()
            messagebox.showinfo("Sucesso", f"Resgatado em {formatar_moeda(valor)}.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def salvar_dados(self):
        self.banco.salvar()
        messagebox.showinfo("Sucesso", f"Dados salvos em:\n{ARQUIVO_DADOS}")

    def carregar_dados(self):
        self.banco = BancoSimulador.carregar()
        self.combo_conta["values"] = self.banco.nomes_contas()
        self.atualizar_tudo()
        messagebox.showinfo("Sucesso", "Dados carregados.")

    def atualizar_tudo(self):
        # Atualizar cards
        for card in [self.card1, self.card2, self.card3]:
            indice = card._indice
            nomes = self.banco.nomes_contas()
            if indice < len(nomes):
                conta = self.banco.conta(nomes[indice])
                card._label_saldo.config(text=formatar_moeda(conta.saldo))
                card._label_investido.config(text=f"Investido: {formatar_moeda(conta.total_investido)}")

        # Atualizar histórico
        self.lst_historico.delete(0, tk.END)
        conta = self.conta_selecionada()
        for lance in reversed(conta.historico[-10:]):
            linha = f"[{lance.data}] {lance.tipo} - {formatar_moeda(lance.valor)}"
            self.lst_historico.insert(tk.END, linha)

        # Atualizar investimentos
        for item in self.tree_inv.get_children():
            self.tree_inv.delete(item)
        for idx, inv in enumerate(conta.carteira.ativos()):
            self.tree_inv.insert("", tk.END, iid=str(idx), values=(
                inv.NOME,
                formatar_moeda(inv.valor_aplicado),
                inv.dias_corridos,
            ))


if __name__ == "__main__":
    root = tk.Tk()
    app = BancoInvestApp(root)
    root.mainloop()
