import tkinter as tk
from tkinter import messagebox
from abc import ABC, abstractmethod

# ==========================================
# 1. ABSTRAÇÃO & HERANÇA (POO)
# ==========================================
class AtivoFinanceiro(ABC):
    def __init__(self, nome: str, valor_investido: float):
        self.nome = nome
        self.valor_investido = valor_investido

    @abstractmethod
    def calcular_rendimento(self) -> float:
        pass

class RendaFixa(AtivoFinanceiro):
    def calcular_rendimento(self) -> float:
        return self.valor_investido * 0.1075  # Simula 10.75% de rendimento

class RendaVariavel(AtivoFinanceiro):
    def calcular_rendimento(self) -> float:
        return self.valor_investido * 0.1280  # Simula 12.80% de rendimento


# ==========================================
# 2. ENCAPSULAMENTO & CONTA BANCÁRIA (POO)
# ==========================================
class ContaBancaria:
    def __init__(self, titular: str, saldo_inicial: float):
        self.titular = titular
        self.__saldo = saldo_inicial  # Atributo privado (Encapsulamento)
        self.__total_investido = 0.0

    @property
    def saldo(self) -> float:
        return self.__saldo

    @property
    def total_investido(self) -> float:
        return self.__total_investido

    def depositar(self, valor: float) -> bool:
        if valor > 0:
            self.__saldo += valor
            return True
        return False

    def sacar(self, valor: float) -> bool:
        if 0 < valor <= self.__saldo:
            self.__saldo -= valor
            return True
        return False

    def investir(self, ativo: AtivoFinanceiro) -> bool:
        if 0 < ativo.valor_investido <= self.__saldo:
            self.__saldo -= ativo.valor_investido
            self.__total_investido += ativo.valor_investido
            return True
        return False


# ==========================================
# 3. INTERFACE GRÁFICA (GUI) - BANCO INVEST+
# ==========================================
class BancoInvestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Banco Invest+ | Simulador Financeiro")
        self.root.geometry("480x600")
        
        # Cores baseadas no seu style.css original
        self.cor_bg = "#07111f"          # --bg
        self.cor_card = "#0c1729"        # --bg-alt
        self.cor_texto = "#e8eefc"       # --text
        self.cor_primary = "#2f80ed"     # --primary
        self.cor_success = "#29c28f"     # --success

        self.root.configure(bg=self.cor_bg)

        # Inicializando o objeto da Conta Bancária
        self.conta = ContaBancaria(titular="Ícaro", saldo_inicial=48920.00)

        self.criar_widgets()
        self.atualizar_tela()

    def criar_widgets(self):
        # Topbar / Cabeçalho
        lbl_titulo = tk.Label(self.root, text="B BANCO INVEST+", font=("Inter", 16, "bold"), bg=self.cor_bg, fg=self.cor_primary)
        lbl_titulo.pack(pady=15)

        # Card de Resumo Financeiro
        self.card = tk.Frame(self.root, bg=self.cor_card, bd=1, relief="solid", highlightthickness=0)
        self.card.pack(pady=10, padx=20, fill="both")

        lbl_titular = tk.Label(self.card, text=f"Conta de: {self.conta.titular}", font=("Inter", 10), bg=self.cor_card, fg="#9ca9c7")
        lbl_titular.pack(pady=(10, 5))

        self.lbl_saldo = tk.Label(self.card, text="", font=("Inter", 20, "bold"), bg=self.cor_card, fg=self.cor_texto)
        self.lbl_saldo.pack(pady=5)

        self.lbl_investido = tk.Label(self.card, text="", font=("Inter", 12), bg=self.cor_card, fg=self.cor_success)
        self.lbl_investido.pack(pady=(5, 10))

        # Seção de Entrada de Valores
        lbl_input = tk.Label(self.root, text="Digite o valor para a operação (R$):", font=("Inter", 10), bg=self.cor_bg, fg=self.cor_texto)
        lbl_input.pack(pady=(20, 5))

        self.entry_valor = tk.Entry(self.root, font=("Inter", 12), justify="center", bd=0, bg="#13233d", fg=self.cor_texto, insertbackground="white")
        self.entry_valor.pack(pady=5, ipady=5, padx=40, fill="x")

        # Botões de Operações Essenciais
        btn_deposito = tk.Button(self.root, text="Efetuar Depósito", font=("Inter", 10, "bold"), bg=self.cor_primary, fg="white", bd=0, command=self.executar_deposito)
        btn_deposito.pack(pady=5, ipady=4, padx=40, fill="x")

        btn_saque = tk.Button(self.root, text="Efetuar Saque", font=("Inter", 10, "bold"), bg="#13233d", fg=self.cor_texto, bd=0, command=self.executar_saque)
        btn_saque.pack(pady=5, ipady=4, padx=40, fill="x")

        # Seção de Investimentos
        lbl_inv_sec = tk.Label(self.root, text="Simular Investimentos:", font=("Inter", 11, "bold"), bg=self.cor_bg, fg=self.cor_texto)
        lbl_inv_sec.pack(pady=(20, 5))

        btn_rf = tk.Button(self.root, text="Investir em Renda Fixa (Tesouro/CDB)", font=("Inter", 10), bg=self.cor_card, fg=self.cor_success, bd=1, command=lambda: self.executar_investimento("RF"))
        btn_rf.pack(pady=5, ipady=4, padx=40, fill="x")

        btn_rv = tk.Button(self.root, text="Investir em Renda Variável (Ações)", font=("Inter", 10), bg=self.cor_card, fg="#60a5fa", bd=1, command=lambda: self.executar_investimento("RV"))
        btn_rv.pack(pady=5, ipady=4, padx=40, fill="x")

    def atualizar_tela(self):
        self.lbl_saldo.config(text=f"Saldo: R$ {self.conta.saldo:.2f}")
        self.lbl_investido.config(text=f"Total Investido: R$ {self.conta.total_investido:.2f}")
        self.entry_valor.delete(0, tk.END)

    def obter_valor(self) -> float:
        try:
            return float(self.entry_valor.get())
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor numérico válido.")
            return 0.0

    def executar_deposito(self):
        valor = self.obter_valor()
        if valor > 0:
            self.conta.depositar(valor)
            messagebox.showinfo("Sucesso", f"Depósito de R$ {valor:.2f} realizado!")
            self.atualizar_tela()

    def executar_saque(self):
        valor = self.obter_valor()
        if valor > 0:
            if self.conta.sacar(valor):
                messagebox.showinfo("Sucesso", f"Saque de R$ {valor:.2f} realizado!")
                self.atualizar_tela()
            else:
                messagebox.showerror("Erro", "Saldo insuficiente para o saque.")

    def executar_investimento(self, tipo):
        valor = self.obter_valor()
        if valor > 0:
            if tipo == "RF":
                ativo = RendaFixa("Tesouro Direto", valor)
            else:
                ativo = RendaVariavel("Carteira Ações", valor)

            if self.conta.investir(ativo):
                messagebox.showinfo("Sucesso", f"Investimento de R$ {valor:.2f} em {ativo.nome} efetuado!")
                self.atualizar_tela()
            else:
                messagebox.showerror("Erro", "Saldo insuficiente para realizar este investimento.")

# Execução do App
if __name__ == "__main__":
    root = tk.Tk()
    app = BancoInvestApp(root)
    root.mainloop()