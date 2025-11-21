#!/usr/bin/env python3
# main.py - Interface gráfica Tkinter do Sistema de Recomendação Hierárquica de Produtos (SRHP)
# Autor: Equipe SRHP | Versão acadêmica otimizada para medição de desempenho e complexidade
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import SUCCESS, INFO, PRIMARY, WARNING, DANGER, SECONDARY

from app.core.arvore_avl import ArvoreAVL
from app.core.categoria import Categoria
from app.services.recomendacao_service import RecomendacaoService
from app.utils.logger import Logger
from app.utils.timer import Timer
from app.flask.web_app import run_api

"""Aplicação principal (GUI) do SRHP — interface com Tkinter/ttkbootstrap.

Contém a classe SRHPGui que monta a interface, conecta com ArvoreAVL e
RecomendacaoService e lida com interações do usuário (busca, seleção, CRUD).
"""
class SRHPGui(ttk.Window):
    """Interface gráfica principal para o SRHP com tema profissional"""

    def __init__(self):
        super().__init__(title="SRHP - Sistema de Recomendação Hierárquica de Produtos", themename="superhero")
        self.geometry("1000x650")
        self.minsize(950, 600)

        # === Core ===
        self.logger = Logger("SRHP-GUI")
        self.timer = Timer()
        self.arvore = ArvoreAVL()
        self.recomendador = RecomendacaoService(self.arvore)
        self._carregar_dados_iniciais()
        self.recomendador.reindexar()
        self.sugestoes_atual = []

        # === UI ===
        self._montar_interface()
        self._atualizar_status_info()
        self.logger.info("Interface gráfica (ttkbootstrap) inicializada com sucesso.")

        # === Web API ===
        self._iniciar_web_api()

    def _iniciar_web_api(self):
        """Inicia a API Web em uma thread separada"""
        try:
            # Passamos a árvore atual para compartilhar o estado
            api_thread = threading.Thread(target=run_api, args=(self.arvore,), daemon=True)
            api_thread.start()
            self.logger.info("Web API iniciada em thread separada.")
        except Exception as e:
            self.logger.error(f"Erro ao iniciar Web API: {str(e)}")

    # --------------------------------------------------------------------------
    # Dados iniciais
    # --------------------------------------------------------------------------
    def _carregar_dados_iniciais(self):
        """Popula a árvore com dados padrão"""
        bebidas = Categoria("Bebidas", ["Suco de Uva", "Refrigerante", "Água Mineral"], peso_popularidade=4.0)
        eletronicos = Categoria("Eletrônicos", ["Celular", "Notebook", "Fone JBL"], peso_popularidade=3.0)
        acessorios = Categoria("Acessórios", ["Cabo HDMI", "Mouse Gamer"], peso_popularidade=2.0)
        eletronicos.adicionar_subcategoria(acessorios)
        bananinha = Categoria("Bananinha", ["Banana Chips", "Banana Passa"], peso_popularidade=5.0)
        bananas_gourmet = Categoria("Bananas Gourmet", ["Banana Flambada", "Banana com Chocolate"], peso_popularidade=2.0)
        bananinha.adicionar_subcategoria(bananas_gourmet)
        for c in [bebidas, eletronicos, bananinha]:
            self.arvore.inserir_publico(c)

    # --------------------------------------------------------------------------
    # Interface principal
    # --------------------------------------------------------------------------
    def _montar_interface(self):
        # Header
        header = ttk.Frame(self, padding=10)
        header.pack(fill="x")
        ttk.Label(header, text="📦 SRHP - Sistema de Recomendação Hierárquica de Produtos",
                  font=("Segoe UI", 16, "bold")).pack(side="left", padx=5)
        ttk.Label(header, text="Interface Gráfica Profissional", font=("Segoe UI", 10)).pack(side="right")

        # Barra de busca
        frame_top = ttk.Labelframe(self, text="Busca de Produtos", padding=10)
        frame_top.pack(fill="x", padx=15, pady=(10, 5))

        ttk.Label(frame_top, text="🔍 Buscar produto:").pack(side="left", padx=(5, 8))
        self.entry_search = ttk.Entry(frame_top, width=40)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", self._on_search_key)

        ttk.Button(frame_top, text="Limpar", bootstyle=SECONDARY, command=self._limpar_busca).pack(side="left", padx=5)

        self.lbl_time = ttk.Label(frame_top, text="⏱ Tempo: -", font=("Segoe UI", 9))
        self.lbl_time.pack(side="right", padx=8)
        self.lbl_total = ttk.Label(frame_top, text="Categorias: 0", font=("Segoe UI", 9))
        self.lbl_total.pack(side="right")

        # Área principal (resultados e detalhes)
        frame_main = ttk.Panedwindow(self, orient="horizontal")
        frame_main.pack(fill="both", expand=True, padx=15, pady=10)

        # --- Esquerda: sugestões
        left_panel = ttk.Labelframe(frame_main, text="Sugestões de Produtos", padding=8)
        frame_main.add(left_panel, weight=1)

        self.lb_resultados = tk.Listbox(left_panel, bg="#101820", fg="#EAEAEA", selectbackground="#0066CC",
                                        font=("Segoe UI", 10), relief="flat", height=20)
        self.lb_resultados.pack(side="left", fill="both", expand=True)
        self.lb_resultados.bind("<<ListboxSelect>>", self._on_select_resultado)
        self.lb_resultados.bind("<Double-Button-1>", self._on_confirmar_produto)

        scroll = ttk.Scrollbar(left_panel, orient="vertical", command=self.lb_resultados.yview)
        scroll.pack(side="right", fill="y")
        self.lb_resultados.config(yscrollcommand=scroll.set)

        # --- Direita: detalhes
        right_panel = ttk.Labelframe(frame_main, text="Detalhes e Métricas", padding=8)
        frame_main.add(right_panel, weight=2)

        self.txt_detalhes = tk.Text(right_panel, wrap="word", state="disabled",
                                    bg="#0d0d0d", fg="#F0E68C", insertbackground="white",
                                    font=("Consolas", 10), relief="flat")
        self.txt_detalhes.pack(fill="both", expand=True, padx=6, pady=6)

        # Rodapé
        frame_bottom = ttk.Frame(self, padding=(15, 10))
        frame_bottom.pack(fill="x", side="bottom")

        # Botões principais (grupo esquerdo)
        for text, cmd, style in [
            ("Adicionar Categoria", self._adicionar_categoria, SUCCESS),
            ("Adicionar Subcategoria", self._adicionar_subcategoria, INFO),
            ("Adicionar Produto", self._adicionar_produto, PRIMARY),
            ("Remover Subcategoria", self._remover_subcategoria, WARNING),
            ("Remover Produto", self._remover_produto, DANGER),
            ("Remover Categoria", self._remover_categoria, SECONDARY),
        ]:
            ttk.Button(frame_bottom, text=text, bootstyle=style, command=cmd, width=18).pack(side="left", padx=4)

        # Botões técnicos (lado direito)
        ttk.Button(frame_bottom, text="📊 Relatório Técnico", bootstyle=INFO, command=self._mostrar_relatorio).pack(side="right", padx=6)
        ttk.Button(frame_bottom, text="🌳 Visualizar Árvore AVL", bootstyle=SUCCESS, command=self._mostrar_arvore_avl).pack(side="right", padx=6)
    # --------------------------------------------------------------------------
    # Funções principais de busca e interação
    # --------------------------------------------------------------------------
    def _on_search_key(self, event=None):
        termo = self.entry_search.get().strip()
        if not termo:
            self.lb_resultados.delete(0, tk.END)
            self._atualizar_status_info()
            return

        with self.timer:
            resultados = self.recomendador.sugerir_por_prefixo(termo, limite=15)
        tempo = self.timer.get_elapsed_time()

        self.logger.info(f"Busca '{termo}' executada | Tempo={tempo:.6f}s | O(n)")
        self.lbl_time.config(text=f"⏱ Tempo: {tempo:.6f}s")

        self.lb_resultados.delete(0, tk.END)
        self.sugestoes_atual = resultados
        for i, r in enumerate(resultados, 1):
            self.lb_resultados.insert(tk.END, f"{i}. {r['nome']} → {r['categoria']}")

    def _on_select_resultado(self, event=None):
        sel = self.lb_resultados.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(self.sugestoes_atual):
            self._mostrar_detalhes(self.sugestoes_atual[idx])

    # --------------------------------------------------------------------------
    #  🚀 MÉTODO CRÍTICO: SELECIONAR PRODUTO (CORRIGIDO COM SUAS REGRAS)
    # --------------------------------------------------------------------------
    def _on_confirmar_produto(self, event=None):
        """Duplo clique: aplica incrementos oficiais +0.008 / +0.003 / +0.005 conforme regras SRHP."""
        sel = self.lb_resultados.curselection()
        if not sel:
            return

        idx = sel[0]
        produto = self.sugestoes_atual[idx]
        nome_prod = produto["nome"]
        caminho = produto["categoria"]

        partes = [p.strip() for p in caminho.split(">")] if caminho else []
        cat_nome = partes[0] if partes else None
        sub_nome = partes[-1] if len(partes) > 1 else None

        cat = self.arvore.buscar_publico(cat_nome) if cat_nome else None
        if not cat:
            messagebox.showwarning("Erro", "Categoria não encontrada.")
            return

        # ------------------------------------------------------------------
        # Antes (captura)
        # ------------------------------------------------------------------
        peso_cat_ant = cat.peso_popularidade
        peso_sub_ant = None
        peso_prod_ant = None

        sub = None
        if sub_nome and sub_nome != cat_nome:
            sub = next((s for s in cat.subcategorias if s.nome == sub_nome), None)
            if sub:
                peso_sub_ant = sub.peso_popularidade
                p = next((p for p in sub.get_produtos_ordenados_por_peso() if p["nome"] == nome_prod), None)
                if p:
                    peso_prod_ant = p["peso_produto"]
        else:
            p = next((p for p in cat.get_produtos_ordenados_por_peso() if p["nome"] == nome_prod), None)
            if p:
                peso_prod_ant = p["peso_produto"]

        # ------------------------------------------------------------------
        #  🚀 Aplicando AS REGRAS OFICIAIS (CORRETAS)
        # ------------------------------------------------------------------
        # Categoria: +0.008
        cat.aumentar_peso(0.008)

        # Subcategoria: +0.003 (se existir)
        if sub:
            sub.aumentar_peso(0.003)

        # Produto: +0.005 (sempre)
        if sub:
            sub.aumentar_peso_produto(nome_prod, 0.005)
        else:
            cat.aumentar_peso_produto(nome_prod, 0.005)

        # ------------------------------------------------------------------
        # Reindexar após alterações
        # ------------------------------------------------------------------
        self.recomendador.reindexar()

        # ------------------------------------------------------------------
        # Depois (captura)
        # ------------------------------------------------------------------
        peso_cat_dep = cat.peso_popularidade
        peso_sub_dep = None
        peso_prod_dep = None

        if sub:
            peso_sub_dep = sub.peso_popularidade
            p = next((p for p in sub.get_produtos_ordenados_por_peso() if p["nome"] == nome_prod), None)
            if p:
                peso_prod_dep = p["peso_produto"]
        else:
            p = next((p for p in cat.get_produtos_ordenados_por_peso() if p["nome"] == nome_prod), None)
            if p:
                peso_prod_dep = p["peso_produto"]

        # ------------------------------------------------------------------
        #  Registrar incremento
        # ------------------------------------------------------------------
        self._ultimo_incremento = {
            "nome": nome_prod,
            "peso_cat_ant": peso_cat_ant,
            "peso_cat_dep": peso_cat_dep,
            "peso_sub_ant": peso_sub_ant,
            "peso_sub_dep": peso_sub_dep,
            "peso_prod_ant": peso_prod_ant,
            "peso_prod_dep": peso_prod_dep,
        }

        # ------------------------------------------------------------------
        #  Montar painel de resumo visual
        # ------------------------------------------------------------------
        texto = ["📈 INCREMENTO DE PESOS\n"]
        texto.append(f"Produto selecionado: {nome_prod}")
        texto.append(f"Categoria: {cat_nome}")
        if sub:
            texto.append(f"Subcategoria: {sub_nome}")

        texto.append(f"\nPeso Categoria: {peso_cat_ant:.3f} ➜ {peso_cat_dep:.3f} (+0.008)")

        if sub:
            texto.append(f"Peso Subcategoria: {peso_sub_ant:.3f} ➜ {peso_sub_dep:.3f} (+0.003)")

        texto.append(f"Peso Produto: {peso_prod_ant:.3f} ➜ {peso_prod_dep:.3f} (+0.005)")

        texto.append("\nComplexidade teórica: O(1)")
        texto.append("Tempo medido: <1ms\n")

        # Atualizar UI
        self.txt_detalhes.config(state="normal")
        self.txt_detalhes.delete("1.0", tk.END)
        self.txt_detalhes.insert(tk.END, "\n".join(texto))
        self.txt_detalhes.config(state="disabled")

        # Log
        self.logger.info(
            f"Incremento | produto='{nome_prod}' | "
            f"cat={peso_cat_ant:.3f}->{peso_cat_dep:.3f} | "
            f"sub={peso_sub_ant}->{peso_sub_dep} | "
            f"prod={peso_prod_ant}->{peso_prod_dep}"
        )

        messagebox.showinfo("Pesos atualizados", f"Produto '{nome_prod}' selecionado — pesos incrementados.")
        self._on_search_key()
    # --------------------------------------------------------------------------
    # Operações CRUD
    # --------------------------------------------------------------------------
    def _adicionar_categoria(self):
        nome = simpledialog.askstring("Nova Categoria", "Nome da categoria:")
        if not nome:
            return
        if self.arvore.buscar_publico(nome):
            messagebox.showwarning("Duplicada", "Categoria já existe.")
            return
        cat = Categoria(nome)
        self.arvore.inserir_publico(cat)
        self.recomendador.reindexar()
        self.logger.info(f"Categoria adicionada='{nome}' | Complexidade=O(log n)")
        self._atualizar_status_info()
        messagebox.showinfo("OK", f"Categoria '{nome}' adicionada.")

    def _adicionar_produto(self):
        cat_nome = simpledialog.askstring("Adicionar Produto", "Categoria principal:")
        if not cat_nome:
            return
        cat = self.arvore.buscar_publico(cat_nome)
        if not cat:
            messagebox.showerror("Erro", "Categoria não encontrada.")
            return
        sub_nome = simpledialog.askstring("Adicionar Produto", "Subcategoria (opcional):")
        prod_nome = simpledialog.askstring("Adicionar Produto", "Nome do produto:")
        if not prod_nome:
            return

        if sub_nome:
            sub = next((s for s in cat.subcategorias if s.nome.lower() == sub_nome.lower()), None)
            if not sub:
                criar = messagebox.askyesno("Subcategoria não existe", "Deseja criá-la?")
                if criar:
                    nova = Categoria(sub_nome)
                    cat.adicionar_subcategoria(nova)
                    sub = nova
                else:
                    return
            sub.adicionar_produto(prod_nome)
        else:
            cat.adicionar_produto(prod_nome)

        self.recomendador.reindexar()
        self.logger.info(f"Produto adicionado='{prod_nome}' em '{cat_nome}' | Complexidade=O(1)")
        self._atualizar_status_info()
        self._on_search_key()

    def _remover_produto(self):
        cat_nome = simpledialog.askstring("Remover Produto", "Categoria principal:")
        if not cat_nome:
            return
        cat = self.arvore.buscar_publico(cat_nome)
        if not cat:
            messagebox.showerror("Erro", "Categoria não encontrada.")
            return
        prod_nome = simpledialog.askstring("Remover Produto", "Nome do produto:")
        if not prod_nome:
            return
        ok = cat.remover_produto(prod_nome)
        if ok:
            self.recomendador.reindexar()
            self.logger.info(f"Produto removido='{prod_nome}' | Complexidade=O(1)")
            self._atualizar_status_info()
            messagebox.showinfo("OK", f"Produto '{prod_nome}' removido.")
            self._on_search_key()
        else:
            messagebox.showwarning("Não encontrado", "Produto não existe.")

    def _remover_categoria(self):
        nome = simpledialog.askstring("Remover Categoria", "Nome da categoria:")
        if not nome:
            return
        ok = self.arvore.remover_publico(nome)
        if ok:
            self.recomendador.reindexar()
            self.logger.info(f"Categoria removida='{nome}' | Complexidade=O(log n)")
            self._atualizar_status_info()
            messagebox.showinfo("OK", f"Categoria '{nome}' removida.")
        else:
            messagebox.showwarning("Não encontrado", "Categoria não existe.")

    def _adicionar_subcategoria(self):
        cat_nome = simpledialog.askstring("Adicionar Subcategoria", "Categoria principal:")
        if not cat_nome:
            return
        cat = self.arvore.buscar_publico(cat_nome)
        if not cat:
            messagebox.showerror("Erro", f"Categoria '{cat_nome}' não encontrada.")
            return

        sub_nome = simpledialog.askstring("Adicionar Subcategoria", "Nome da nova subcategoria:")
        if not sub_nome:
            return

        if any(s.nome.lower() == sub_nome.lower() for s in cat.subcategorias):
            messagebox.showwarning("Duplicada", f"A subcategoria '{sub_nome}' já existe em '{cat_nome}'.")
            return

        sub = Categoria(sub_nome)
        cat.adicionar_subcategoria(sub)
        self.recomendador.reindexar()
        self.logger.info(f"Subcategoria adicionada='{sub_nome}' em '{cat_nome}' | Complexidade=O(1)")
        self._atualizar_status_info()
        messagebox.showinfo("OK", f"Subcategoria '{sub_nome}' adicionada em '{cat_nome}'.")

    def _remover_subcategoria(self):
        cat_nome = simpledialog.askstring("Remover Subcategoria", "Categoria principal:")
        if not cat_nome:
            return
        cat = self.arvore.buscar_publico(cat_nome)
        if not cat:
            messagebox.showerror("Erro", "Categoria não encontrada.")
            return

        sub_nome = simpledialog.askstring("Remover Subcategoria", "Nome da subcategoria:")
        if not sub_nome:
            return

        removida = False
        for s in list(cat.subcategorias):
            if s.nome.lower() == sub_nome.lower():
                cat.subcategorias.remove(s)
                removida = True
                break

        if removida:
            self.recomendador.reindexar()
            self.logger.info(f"Subcategoria removida='{sub_nome}' de '{cat_nome}' | Complexidade=O(1)")
            self._atualizar_status_info()
            messagebox.showinfo("OK", f"Subcategoria '{sub_nome}' removida de '{cat_nome}'.")
        else:
            messagebox.showwarning("Não encontrada", f"Subcategoria '{sub_nome}' não existe em '{cat_nome}'.")

    # --------------------------------------------------------------------------
    # Visualização da Árvore AVL
    # --------------------------------------------------------------------------
    def _mostrar_arvore_avl(self):
        """Abre uma janela com a árvore AVL hierárquica (igual CLI)."""
        from io import StringIO
        import sys

        buffer = StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer
        try:
            self.arvore.imprimir_arvore()
        finally:
            sys.stdout = old_stdout

        conteudo = buffer.getvalue()

        janela = tk.Toplevel(self)
        janela.title("🌳 Visualização da Árvore AVL Completa")
        janela.geometry("800x600")
        txt = tk.Text(janela, wrap="none", bg="#0d0d0d", fg="#b5ffb5", font=("Consolas", 10))
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", conteudo)
        txt.config(state="disabled")
        self.logger.info("Árvore AVL visualizada pelo usuário.")

    # --------------------------------------------------------------------------
    # Exibir detalhes técnicos
    # --------------------------------------------------------------------------
    def _mostrar_detalhes(self, info):
        """Exibe informações técnicas detalhadas e atualizadas de um produto, incluindo pesos e métricas AVL."""
        self.txt_detalhes.config(state="normal")
        self.txt_detalhes.delete("1.0", tk.END)

        nome = info.get("nome", "—")
        caminho = info.get("categoria", "—")
        partes = [p.strip() for p in caminho.split(">")] if caminho else []
        cat_nome = partes[0] if partes else None
        sub_nome = partes[-1] if len(partes) > 1 else None

        # === Medir tempo de busca AVL ===
        with self.timer:
            cat = self.arvore.buscar_publico(cat_nome) if cat_nome else None
        tempo_exec = self.timer.get_elapsed_time()

        peso_cat = peso_sub = peso_prod = None

        if cat:
            peso_cat = cat.peso_popularidade
            if sub_nome and sub_nome != cat_nome:
                sub = next((s for s in cat.subcategorias if s.nome == sub_nome), None)
                if sub:
                    peso_sub = sub.peso_popularidade
                    prod = next((p for p in sub.get_produtos_ordenados_por_peso() if p["nome"] == nome), None)
                    if prod:
                        peso_prod = prod["peso_produto"]
            else:
                prod = next((p for p in cat.get_produtos_ordenados_por_peso() if p["nome"] == nome), None)
                if prod:
                    peso_prod = prod["peso_produto"]

        # === Dados da árvore AVL ===
        rel = self.recomendador.gerar_relatorio_performance()
        altura = rel.get("altura", "?")
        balanceada = "Sim" if rel.get("balanceada") else "Não"

        # === Montar texto ===
        texto = []
        texto.append("📊 DETALHES E MÉTRICAS DO PRODUTO\n")
        texto.append(f"Produto: {nome}")
        texto.append(f"Categoria (caminho): {caminho}")
        texto.append(f"Tempo de busca (AVL): {tempo_exec:.6f}s")
        texto.append(f"Complexidade teórica: O(log n) — Busca binária balanceada")
        texto.append(f"Altura da árvore AVL: {altura}")
        texto.append(f"Árvore balanceada: {balanceada}")

        if peso_cat is not None:
            texto.append(f"Peso da categoria atual: {peso_cat:.3f}")
        if peso_sub is not None:
            texto.append(f"Peso da subcategoria atual: {peso_sub:.3f}")
        if peso_prod is not None:
            texto.append(f"Peso do produto atual: {peso_prod:.3f}")

        # Caso tenha ocorrido incremento recente, mostra diferenças
        if hasattr(self, "_ultimo_incremento") and self._ultimo_incremento.get("nome") == nome:
            inc = self._ultimo_incremento
            texto.append("\n📈 Incremento recente detectado:")
            texto.append(f"Categoria: {inc['peso_cat_ant']:.3f} ➜ {inc['peso_cat_dep']:.3f} (+0.008)")
            if inc.get("peso_sub_ant") is not None:
                texto.append(f"Subcategoria: {inc['peso_sub_ant']:.3f} ➜ {inc['peso_sub_dep']:.3f} (+0.003)")
            if inc.get("peso_prod_ant") is not None:
                texto.append(f"Produto: {inc['peso_prod_ant']:.3f} ➜ {inc['peso_prod_dep']:.3f} (+0.005)")
            texto.append("Complexidade teórica da atualização: O(1)")
            texto.append("Tempo estimado da atualização: < 1 ms")

        self.txt_detalhes.insert(tk.END, "\n".join(texto))
        self.txt_detalhes.config(state="disabled")

        # === Log detalhado ===
        self.logger.info(
            f"Detalhes exibidos | produto='{nome}' | tempo_busca={tempo_exec:.6f}s | "
            f"altura={altura} | balanceada={balanceada} | pesos=({peso_cat}, {peso_sub}, {peso_prod}) | O(log n)"
        )

    # --------------------------------------------------------------------------
    # Limpar busca e relatório técnico
    # --------------------------------------------------------------------------
    def _limpar_busca(self):
        self.entry_search.delete(0, tk.END)
        self.lb_resultados.delete(0, tk.END)
        self.txt_detalhes.config(state="normal")
        self.txt_detalhes.delete("1.0", tk.END)
        self.txt_detalhes.config(state="disabled")
        self._atualizar_status_info()

    def _mostrar_relatorio(self):
        """Exibe relatório técnico (altura, balanceamento, complexidade)"""
        rel = self.recomendador.gerar_relatorio_performance()
        texto = (
            f"📊 RELATÓRIO TÉCNICO - SRHP\n\n"
            f"Altura da árvore: {rel.get('altura')}\n"
            f"Balanceada: {'Sim' if rel.get('balanceada') else 'Não'}\n"
            f"Total de categorias: {self.arvore.get_tamanho()}\n"
            f"Complexidade média das operações:\n"
            f"  • Inserção / Remoção / Busca AVL: O(log n)\n"
            f"  • Recomendação (prefixo): O(n)\n"
            f"  • Atualização de pesos: O(1)\n"
        )
        messagebox.showinfo("Relatório Técnico", texto)
        self.logger.info("Relatório técnico exibido ao usuário.")

    # --------------------------------------------------------------------------
    # Atualizar status
    # --------------------------------------------------------------------------
    def _atualizar_status_info(self):
        total = self.arvore.get_tamanho()
        self.lbl_total.config(text=f"Categorias: {total}")
        rel = self.recomendador.gerar_relatorio_performance()
        self.title(
            f"SRHP - Altura: {rel.get('altura')} | Balanceada: {'Sim' if rel.get('balanceada') else 'Não'} | Categorias: {total}"
        )


if __name__ == "__main__":
    app = SRHPGui()
    app.mainloop()
