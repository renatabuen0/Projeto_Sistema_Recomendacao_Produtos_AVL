#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface de Linha de Comando (CLI) para o Sistema de Recomendação Hierárquica de Produtos (SRHP)
Execute: python interface_cli.py
"""

import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.arvore_avl import ArvoreAVL
from app.core.categoria import Categoria
from app.services.recomendacao_service import RecomendacaoService


def carregar_dados_iniciais(arvore: ArvoreAVL):
    """Cria categorias, subcategorias e produtos iniciais para teste."""
    bebidas = Categoria("Bebidas", ["Suco de Uva", "Refrigerante", "Água Mineral"], peso_popularidade=4.0)
    eletronicos = Categoria("Eletrônicos", ["Celular", "Notebook", "Fone JBL"], peso_popularidade=3.0)
    acessorios = Categoria("Acessórios", ["Cabo HDMI", "Mouse Gamer"], peso_popularidade=2.0)
    eletronicos.adicionar_subcategoria(acessorios)

    bananinha = Categoria("Bananinha", ["Banana Chips", "Banana Passa"], peso_popularidade=5.0)
    bananas_gourmet = Categoria("Bananas Gourmet", ["Banana Flambada", "Banana com Chocolate"], peso_popularidade=2.0)
    bananinha.adicionar_subcategoria(bananas_gourmet)

    for cat in [bebidas, eletronicos, bananinha]:
        arvore.inserir_publico(cat)


def exibir_menu():
    print("\n==============================")
    print("🌳  SISTEMA SRHP - Interface CLI")
    print("==============================")
    print("1. Inserir nova categoria")
    print("2. Inserir subcategoria")
    print("3. Inserir produto")
    print("4. Exibir árvore completa")
    print("5. Pesquisar produto (autocomplete dinâmico)")
    print("6. Remover categoria")
    print("7. Remover subcategoria")
    print("8. Remover produto")
    print("9. Relatório de desempenho")
    print("0. Sair")
    print("==============================")


def interface_cli():
    arvore = ArvoreAVL()
    carregar_dados_iniciais(arvore)
    recomendador = RecomendacaoService(arvore)
    recomendador.reindexar()

    print("\n🚀 Sistema SRHP iniciado com dados de demonstração.")
    arvore.imprimir_arvore()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        # 1️⃣ Inserir nova categoria
        if opcao == "1":
            nome = input("Nome da nova categoria: ").strip()
            if not nome:
                print("Nome vazio. Abortando.")
                continue
            cat = Categoria(nome)
            arvore.inserir_publico(cat)
            recomendador.reindexar()
            print(f"✅ Categoria '{nome}' adicionada com sucesso!")

        # 2️⃣ Inserir subcategoria
        elif opcao == "2":
            nome_cat = input("Categoria principal: ").strip()
            categoria = arvore.buscar_publico(nome_cat)
            if not categoria:
                print("❌ Categoria não encontrada.")
                continue
            nome_sub = input("Nome da subcategoria: ").strip()
            if not nome_sub:
                print("Nome vazio. Abortando.")
                continue
            sub = Categoria(nome_sub)
            categoria.adicionar_subcategoria(sub)
            recomendador.reindexar()
            print(f"✅ Subcategoria '{nome_sub}' adicionada em '{nome_cat}'.")

        # 3️⃣ Inserir produto
        elif opcao == "3":
            nome_cat = input("Categoria principal: ").strip()
            categoria = arvore.buscar_publico(nome_cat)
            if not categoria:
                print("❌ Categoria não encontrada.")
                continue

            sub_nome = input("Adicionar a uma subcategoria? (deixe vazio se não): ").strip()
            nome_produto = input("Nome do produto: ").strip()
            if not nome_produto:
                print("Produto vazio. Abortando.")
                continue

            # Inserção no nível correto
            if sub_nome:
                sub = next((s for s in categoria.subcategorias if s.nome.lower() == sub_nome.lower()), None)
                if not sub:
                    print(f"❌ Subcategoria '{sub_nome}' não encontrada em '{nome_cat}'.")
                    continue
                sub.adicionar_produto(nome_produto)
                print(f"✅ Produto '{nome_produto}' adicionado em subcategoria '{sub_nome}'.")
            else:
                categoria.adicionar_produto(nome_produto)
                print(f"✅ Produto '{nome_produto}' adicionado em categoria '{nome_cat}'.")

            # Reindexar produtos após inserção
            recomendador.reindexar()

            # Exibir atualização imediata
            print("\n📦 Atualização da árvore após inserção:")
            arvore.imprimir_arvore()


        # 4️⃣ Exibir árvore
        elif opcao == "4":
            arvore.imprimir_arvore()

        # 5️⃣ Pesquisar produto (autocomplete)
        elif opcao == "5":
            print("\n🔍 Pesquisar produto (autocomplete). Digite letras; ENTER para voltar ao menu.")
            prefixo = ""
            while True:
                letra = input("Próxima letra (ou ENTER para sair): ").strip()
                if letra == "":
                    print("Saindo do modo de pesquisa.\n")
                    break
                prefixo += letra
                sugestoes = recomendador.sugerir_por_prefixo(prefixo, limite=7)
                if not sugestoes:
                    print("  (Nenhuma sugestão encontrada)")
                time.sleep(0.2)

        # 6️⃣ Remover categoria
        elif opcao == "6":
            nome = input("Nome da categoria a remover: ").strip()
            if not nome:
                print("Nome vazio. Abortando.")
                continue
            if arvore.remover_publico(nome):
                recomendador.reindexar()
                print(f"✅ Categoria '{nome}' removida com sucesso!")
            else:
                print(f"❌ Categoria '{nome}' não encontrada.")

        # 7️⃣ Remover subcategoria
        elif opcao == "7":
            nome_cat = input("Nome da categoria principal: ").strip()
            categoria = arvore.buscar_publico(nome_cat)
            if not categoria:
                print("❌ Categoria não encontrada.")
                continue
            nome_sub = input("Nome da subcategoria a remover: ").strip()
            if categoria.remover_subcategoria(nome_sub):
                recomendador.reindexar()
                print(f"✅ Subcategoria '{nome_sub}' removida de '{nome_cat}'.")
            else:
                print(f"❌ Subcategoria '{nome_sub}' não encontrada em '{nome_cat}'.")

        # 8️⃣ Remover produto
        elif opcao == "8":
            nome_cat = input("Nome da categoria principal: ").strip()
            categoria = arvore.buscar_publico(nome_cat)
            if not categoria:
                print("❌ Categoria não encontrada.")
                continue

            sub_nome = input("Remover de uma subcategoria? (deixe vazio se não): ").strip()
            nome_produto = input("Nome do produto a remover: ").strip()
            if not nome_produto:
                print("Produto vazio. Abortando.")
                continue

            if sub_nome:
                sub = next((s for s in categoria.subcategorias if s.nome == sub_nome), None)
                if sub and sub.remover_produto(nome_produto):
                    recomendador.reindexar()
                    print(f"✅ Produto '{nome_produto}' removido de subcategoria '{sub_nome}'.")
                else:
                    print(f"❌ Produto ou subcategoria não encontrados.")
            else:
                if categoria.remover_produto(nome_produto):
                    recomendador.reindexar()
                    print(f"✅ Produto '{nome_produto}' removido de categoria '{nome_cat}'.")
                else:
                    print(f"❌ Produto '{nome_produto}' não encontrado em '{nome_cat}'.")

        # 9️⃣ Relatório de desempenho
        elif opcao == "9":
            relatorio = recomendador.gerar_relatorio_performance()
            print("\n📊 Relatório de Desempenho")
            print("=============================")
            print(f"Total de categorias: {relatorio['total_categorias']}")
            print(f"Altura da árvore: {relatorio['altura']}")
            print(f"Árvore balanceada: {'Sim' if relatorio['balanceada'] else 'Não'}")
            print("\nComplexidade estimada:")
            for k, v in relatorio["complexidade"].items():
                print(f" - {k}: {v}")

        # 0️⃣ Sair
        elif opcao == "0":
            print("👋 Encerrando sistema SRHP...")
            break

        else:
            print("❌ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    interface_cli()
