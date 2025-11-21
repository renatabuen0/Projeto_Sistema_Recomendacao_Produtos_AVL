import sys, os

class RecomendacaoService:
    def gerar_recomendacoes(self, categoria):
        return [f'Recomendação para {categoria}']


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.arvore_avl import ArvoreAVL
from app.utils.timer import Timer
from app.utils.logger import Logger
from typing import List, Dict, Optional


class RecomendacaoService:
    """
    Serviço de recomendação hierárquica de produtos (SRHP).
    Agora totalmente recursivo para indexar todas as categorias e subcategorias.
    """

    def __init__(self, arvore_avl: ArvoreAVL):
        self.arvore = arvore_avl
        self.timer = Timer()
        self.logger = Logger(__name__)

        self.indice_produtos = {}     # {'BA': [produtos...], 'N': [...]}
        self.indice_categorias = {}   # {'fone jbl': 'Eletrônicos > Acessórios'}

    # =============================================================
    # 🔧 CONSTRUÇÃO E MANUTENÇÃO DE ÍNDICES
    # =============================================================
    
    def _construir_indices(self):
        self.logger.info("Construindo índices de produtos...")
        self.indice_produtos.clear()
        self.indice_categorias.clear()

        def percorrer_categoria(categoria, caminho_pai=""):
            caminho = f"{caminho_pai} > {categoria.nome}" if caminho_pai else categoria.nome

            for produto in categoria.produtos:
                self._adicionar_ao_indice(produto, caminho)

            for subcat in categoria.subcategorias:
                percorrer_categoria(subcat, caminho)

        def percorrer_no(no):
            if not no:
                return
            percorrer_no(no.esquerda)
            percorrer_categoria(no.categoria)
            percorrer_no(no.direita)

        percorrer_no(self.arvore.raiz)

        total = len(self.indice_categorias)
        self.logger.info(f"Índices construídos com sucesso: {total} produtos indexados.")
        print(f"🧩 [DEBUG] Total de produtos indexados: {total}")
        if total > 0:
            print(f"🔑 Prefixos disponíveis: {list(self.indice_produtos.keys())[:10]}")

    def _adicionar_ao_indice(self, produto, caminho_categoria: str):
        if not produto:
            return

        if isinstance(produto, dict):
            produto_nome = produto.get("nome", "")
        else:
            produto_nome = str(produto)

        if not produto_nome:
            return

        produto_upper = produto_nome.upper()
        max_prefixo = min(len(produto_upper), 10)
        for i in range(1, max_prefixo + 1):
            prefixo = produto_upper[:i]
            if prefixo not in self.indice_produtos:
                self.indice_produtos[prefixo] = []

            produto_info = {
                "nome": produto_nome,
                "categoria": caminho_categoria
            }

            if not any(p['nome'] == produto_nome and p['categoria'] == caminho_categoria
                       for p in self.indice_produtos[prefixo]):
                self.indice_produtos[prefixo].append(produto_info)

        self.indice_categorias[produto_nome.lower()] = caminho_categoria


    # =============================================================
    # 🔍 BUSCA E RECOMENDAÇÃO
    # =============================================================
    def buscar_categoria_recursiva(self, nome: str) -> Optional[object]:
        self.timer.start()
        resultado = self.arvore.buscar(self.arvore.raiz, nome)
        self.timer.stop()

        if resultado:
            resultado.peso_popularidade += 1.0
            self.logger.info(f"Categoria '{nome}' encontrada (peso +1).")
        else:
            self.logger.warning(f"Categoria '{nome}' não encontrada.")
        return resultado

    def sugerir_por_prefixo(self, prefixo: str, limite: int = 7) -> List[Dict]:
        self.timer.start()

        if not prefixo:
            return []

        prefixo_upper = prefixo.upper()
        candidatos = self.indice_produtos.get(prefixo_upper, [])

        if not candidatos:
            print("  (Nenhum produto encontrado com esse prefixo)")
            return []

        def peso_do_produto(p):
            caminho = p.get("categoria", "")
            topo = caminho.split('>')[0].strip() if caminho else ""
            cat = self.arvore.buscar(self.arvore.raiz, topo) if topo else None
            if not cat:
                return 0.0
            if '>' in caminho:
                sub_nome = caminho.split('>')[-1].strip()
                for sc in cat.subcategorias:
                    if sc.nome == sub_nome:
                        return getattr(sc, "peso_popularidade", cat.peso_popularidade)
            return getattr(cat, "peso_popularidade", 0.0)

        candidatos_sorted = sorted(candidatos, key=lambda x: peso_do_produto(x), reverse=True)
        sugestoes = candidatos_sorted[:limite]

        # ============================================================
        # 🚀 REGRAS DE PESQUISA (SEU PEDIDO)
        # Produto: +0.001
        # Subcategoria: +0.001
        # Categoria: +0.002
        # ============================================================
        if sugestoes:
            primeiro = sugestoes[0]
            caminho = primeiro.get("categoria", "")
            partes = [p.strip() for p in caminho.split(">")] if caminho else []

            cat_nome = partes[0] if partes else None
            sub_nome = partes[-1] if len(partes) > 1 else None
            prod_nome = primeiro.get("nome")

            cat = self.arvore.buscar(self.arvore.raiz, cat_nome)
            if cat:
                # Categoria +0.002
                cat.peso_popularidade += 0.002

                # Produto +0.001
                cat.incrementar_peso_produto(prod_nome, 0.001)

                # Subcategoria +0.001
                if sub_nome and sub_nome != cat_nome:
                    sub = next((s for s in cat.subcategorias if s.nome == sub_nome), None)
                    if sub:
                        sub.peso_popularidade += 0.001
                        sub.incrementar_peso_produto(prod_nome, 0.001)

            # Atualizar índices
            self.reindexar()

        print("📦 Produtos encontrados:")
        for i, s in enumerate(sugestoes, start=1):
            print(f"  {i}. {s['nome']}  →  {s['categoria']}")

        self.timer.stop()
        tempo = self.timer.get_elapsed_time()

        self.logger.info(
            f"Sugestão '{prefixo}': {len(sugestoes)} resultados em {tempo:.6f}s"
        )

        return sugestoes


    # =============================================================
    # 🧮 RELATÓRIO DE PERFORMANCE
    # =============================================================
    def gerar_relatorio_performance(self) -> dict:
        def calcular_altura(no):
            if no is None:
                return 0
            return 1 + max(calcular_altura(no.esquerda), calcular_altura(no.direita))

        def verificar_balanceamento(no):
            if no is None:
                return True
            fb = self.arvore.fator_balanceamento(no)
            if fb < -1 or fb > 1:
                return False
            return verificar_balanceamento(no.esquerda) and verificar_balanceamento(no.direita)

        total_categorias = self.arvore.get_tamanho()
        altura_arvore = calcular_altura(self.arvore.raiz)
        balanceada = verificar_balanceamento(self.arvore.raiz)

        complexidade = {
            "total_categorias": "O(1)",
            "altura_arvore": "O(n)",
            "balanceada": "O(n)",
            "buscar_categoria": "O(log n)",
            "inserir_categoria": "O(log n)",
            "sugerir_por_prefixo": "O(1) + O(k)"
        }

        return {
            "total_categorias": total_categorias,
            "altura": altura_arvore,
            "balanceada": balanceada,
            "complexidade": complexidade
        }

    def reindexar(self):
        self.logger.warning("Reindexando produtos...")
        self._construir_indices()

    def listar_todos_produtos(self) -> List[Dict]:
        """Retorna uma lista plana de todos os produtos indexados"""
        todos = []
        # Usar o índice de categorias para evitar duplicatas
        # indice_categorias mapeia 'nome_produto_lower' -> 'caminho'
        # Mas precisamos dos nomes originais. Vamos reconstruir a partir da árvore.
        
        def coletar_produtos(categoria, caminho_pai=""):
            caminho = f"{caminho_pai} > {categoria.nome}" if caminho_pai else categoria.nome
            
            for produto in categoria.produtos:
                nome = produto.get("nome") if isinstance(produto, dict) else str(produto)
                peso = produto.get("peso_produto", 0.0) if isinstance(produto, dict) else 0.0
                todos.append({
                    "nome": nome,
                    "categoria": caminho,
                    "peso_popularidade": peso
                })
                
            for sub in categoria.subcategorias:
                coletar_produtos(sub, caminho)
                
        def percorrer_no(no):
            if not no: return
            percorrer_no(no.esquerda)
            coletar_produtos(no.categoria)
            percorrer_no(no.direita)
            
        percorrer_no(self.arvore.raiz)
        
        # Ordenar por peso global
        return sorted(todos, key=lambda x: x['peso_popularidade'], reverse=True)
