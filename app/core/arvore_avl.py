import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from typing import Optional, List, Tuple
from app.core.categoria import Categoria


class No:
    
    # Inicialização do nó
    def __init__(self, categoria: Categoria):
        self.categoria = categoria
        self.esquerda: Optional[No] = None
        self.direita: Optional[No] = None
        self.altura: int = 1
    
    # Representação em string
    def __str__(self) -> str:
        return f"No({self.categoria.nome}, altura={self.altura})"


class ArvoreAVL:
    
    # Inicialização da árvore
    def __init__(self):
        self.raiz: Optional[No] = None
        self.tamanho: int = 0
    
    # Métodos auxiliares
    
    # Retorna altura do nó
    def obter_altura(self, no: Optional[No]) -> int:
        return no.altura if no else 0
    
    # Atualiza altura do nó
    def atualizar_altura(self, no: No) -> None:
        no.altura = 1 + max(self.obter_altura(no.esquerda), 
                            self.obter_altura(no.direita))
    
    # Calcula fator de balanceamento
    def fator_balanceamento(self, no: Optional[No]) -> int:
        if no is None:
            return 0
        return self.obter_altura(no.esquerda) - self.obter_altura(no.direita)
    
    # Rotações
    
    # Rotação simples à direita
    def rotacao_direita(self, z: No) -> No:
        y = z.esquerda
        B = y.direita
        
        y.direita = z
        z.esquerda = B
        
        self.atualizar_altura(z)
        self.atualizar_altura(y)
        
        return y
    
    # Rotação simples à esquerda
    def rotacao_esquerda(self, z: No) -> No:
        y = z.direita
        B = y.esquerda
        
        y.esquerda = z
        z.direita = B
        
        self.atualizar_altura(z)
        self.atualizar_altura(y)
        
        return y
    
    # Inserção recursiva
    
    # Insere categoria recursivamente
    def inserir(self, no: Optional[No], categoria: Categoria) -> No:
        # Caso base: posição encontrada
        if not no:
            self.tamanho += 1
            return No(categoria)
        
        # Passo recursivo: desce pela árvore
        if categoria.nome < no.categoria.nome:
            no.esquerda = self.inserir(no.esquerda, categoria)
        elif categoria.nome > no.categoria.nome:
            no.direita = self.inserir(no.direita, categoria)
        else:
            return no
        
        # Atualiza altura
        self.atualizar_altura(no)
        
        # Calcula fator de balanceamento
        fb = self.fator_balanceamento(no)
        
        # Balanceamento: 4 casos
        # Caso 1: Left-Left
        if fb > 1 and categoria.nome < no.esquerda.categoria.nome:
            return self.rotacao_direita(no)
        
        # Caso 2: Right-Right
        if fb < -1 and categoria.nome > no.direita.categoria.nome:
            return self.rotacao_esquerda(no)
        
        # Caso 3: Left-Right
        if fb > 1 and categoria.nome > no.esquerda.categoria.nome:
            no.esquerda = self.rotacao_esquerda(no.esquerda)
            return self.rotacao_direita(no)
        
        # Caso 4: Right-Left
        if fb < -1 and categoria.nome < no.direita.categoria.nome:
            no.direita = self.rotacao_direita(no.direita)
            return self.rotacao_esquerda(no)
        
        return no
    
    # Busca recursiva
    
    # Busca categoria recursivamente
    def buscar(self, no: Optional[No], nome: str) -> Optional[Categoria]:
        # Caso base: não encontrou ou achou
        if no is None:
            return None
        
        if nome == no.categoria.nome:
            return no.categoria
        
        # Passo recursivo: continua buscando
        if nome < no.categoria.nome:
            return self.buscar(no.esquerda, nome)
        else:
            return self.buscar(no.direita, nome)
    
    # Remoção recursiva
    
    # Encontra nó com menor valor
    def menor_valor(self, no: No) -> No:
        atual = no
        while atual.esquerda:
            atual = atual.esquerda
        return atual
    
    # Remove categoria recursivamente
    def remover(self, no: Optional[No], nome: str, removido: List[bool]) -> Optional[No]:
        # Caso base: não encontrou
        if not no:
            return no
        
        # Passo recursivo: procura o nó
        if nome < no.categoria.nome:
            no.esquerda = self.remover(no.esquerda, nome, removido)
        elif nome > no.categoria.nome:
            no.direita = self.remover(no.direita, nome, removido)
        else:
            # Encontrou - Remove
            if not removido[0]:
                self.tamanho -= 1
                removido[0] = True
            
            # Caso 1: nó com 0 ou 1 filho
            if not no.esquerda:
                return no.direita
            elif not no.direita:
                return no.esquerda
            
            # Caso 2: nó com 2 filhos
            temp = self.menor_valor(no.direita)
            no.categoria = temp.categoria
            no.direita = self.remover(no.direita, temp.categoria.nome, removido)
        
        if not no:
            return no
        
        # Atualiza altura
        self.atualizar_altura(no)
        
        # Calcula fator de balanceamento
        fb = self.fator_balanceamento(no)
        
        # Rebalanceamento: 4 casos
        if fb > 1 and self.fator_balanceamento(no.esquerda) >= 0:
            return self.rotacao_direita(no)
        
        if fb > 1 and self.fator_balanceamento(no.esquerda) < 0:
            no.esquerda = self.rotacao_esquerda(no.esquerda)
            return self.rotacao_direita(no)
        
        if fb < -1 and self.fator_balanceamento(no.direita) <= 0:
            return self.rotacao_esquerda(no)
        
        if fb < -1 and self.fator_balanceamento(no.direita) > 0:
            no.direita = self.rotacao_direita(no.direita)
            return self.rotacao_esquerda(no)
        
        return no
    
    # Percursos recursivos
    
    # Percurso em ordem
    def em_ordem(self, no: Optional[No], resultado: List = None) -> List[Tuple[str, int]]:
        if resultado is None:
            resultado = []
        
        if no:
            self.em_ordem(no.esquerda, resultado)
            resultado.append((no.categoria.nome, no.altura))
            self.em_ordem(no.direita, resultado)
        
        return resultado
    
    # Percurso pré-ordem
    def pre_ordem(self, no: Optional[No], resultado: List = None) -> List[Tuple[str, int]]:
        if resultado is None:
            resultado = []
        
        if no:
            resultado.append((no.categoria.nome, no.altura))
            self.pre_ordem(no.esquerda, resultado)
            self.pre_ordem(no.direita, resultado)
        
        return resultado
    
    # Lista todas as categorias recursivamente
    def _listar_recursivo(self, no: Optional[No], lista: List[Categoria]) -> None:
        if no:
            self._listar_recursivo(no.esquerda, lista)
            lista.append(no.categoria)
            self._listar_recursivo(no.direita, lista)
    
    # Imprime árvore recursivamente (agora incluindo produtos e subcategorias)
    def _imprimir_recursivo(self, no: Optional[No], nivel_avl: int = 0, lado: str = "Raiz") -> None:
        """Imprime a árvore AVL hierárquica com rótulos alinhados e produtos garantidos."""
        if not no:
            return

        fb = self.fator_balanceamento(no)
        categoria = no.categoria

        lado_formatado = f"[{lado:<5}]"
        indent_nivel = "    " * nivel_avl
        print(f"{indent_nivel}{lado_formatado} {categoria.nome} (h={no.altura}, FB={fb}, peso={categoria.peso_popularidade:.3f})")

        indent_conteudo = "    " * (nivel_avl + 1)

        # Produtos
        print(f"{indent_conteudo}├─ Produtos:")
        if categoria.produtos:
            for p in categoria.get_produtos_ordenados_por_peso():
                print(f"{indent_conteudo}│   • {p['nome']} (peso_produto={p['peso_produto']:.3f})")
        else:
            print(f"{indent_conteudo}│   (nenhum produto)")

        # Subcategorias
        if categoria.subcategorias:
            print(f"{indent_conteudo}├─ Subcategorias:")
            for i, sub in enumerate(categoria.subcategorias):
                conector = "└─" if i == len(categoria.subcategorias) - 1 else "├─"
                print(f"{indent_conteudo}│   {conector} {sub.nome} (peso={sub.peso_popularidade:.3f})")
                if sub.produtos:
                    for p in sub.get_produtos_ordenados_por_peso():
                        print(f"{indent_conteudo}│      • {p['nome']} (peso_produto={p['peso_produto']:.3f})")
                else:
                    print(f"{indent_conteudo}│      (nenhum produto)")

        # Recursão AVL
        if no.esquerda:
            self._imprimir_recursivo(no.esquerda, nivel_avl + 1, "Esq")
        if no.direita:
            self._imprimir_recursivo(no.direita, nivel_avl + 1, "Dir")



    
    
    # Métodos públicos
    
    # Insere categoria (método público)
    def inserir_publico(self, categoria: Categoria) -> None:
        self.raiz = self.inserir(self.raiz, categoria)
    
    # Busca categoria (método público)
    def buscar_publico(self, nome: str) -> Optional[Categoria]:
        return self.buscar(self.raiz, nome)
    
    # Remove categoria (método público)
    def remover_publico(self, nome: str) -> bool:
        removido = [False]
        self.raiz = self.remover(self.raiz, nome, removido)
        return removido[0]
    
    # Lista todas as categorias
    def listar_todas(self) -> List[Categoria]:
        categorias = []
        self._listar_recursivo(self.raiz, categorias)
        return categorias
    
    # Imprime árvore visualmente + subcategorias e produtos
    def imprimir_arvore(self) -> None:
        """Imprime toda a árvore AVL (categorias, subcategorias e produtos) com indentação alinhada."""
        print("\n=== Árvore AVL Detalhada (categorias, subcategorias e produtos) ===\n")
        if not self.raiz:
            print("(vazia)")
            return
        # chamada corrigida
        self._imprimir_recursivo(self.raiz, 0, "Raiz")
        print(f"\nTotal: {self.tamanho} categorias")

    
    # Verifica se árvore está vazia
    def esta_vazia(self) -> bool:
        return self.raiz is None
    
    # Retorna tamanho da árvore
    def get_tamanho(self) -> int:
        return self.tamanho
    
    # Retorna percurso em ordem
    def get_em_ordem(self) -> List[Tuple[str, int]]:
        return self.em_ordem(self.raiz)
    
    # Retorna percurso pré-ordem
    def get_pre_ordem(self) -> List[Tuple[str, int]]:
        return self.pre_ordem(self.raiz)
