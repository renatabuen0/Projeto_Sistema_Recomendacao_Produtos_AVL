from typing import List, Dict
from threading import Lock

class Categoria:
    # =============================================================
    # 🏷️ Inicialização da categoria
    # =============================================================
    def __init__(self, nome: str, produtos: List[str] = None, peso_popularidade: float = 1.0):
        self.nome = nome
        self._lock = Lock()

        # Cada produto é um dicionário com nome e peso
        self.produtos: List[Dict[str, float]] = []
        if produtos:
            for p in produtos:
                if isinstance(p, dict):
                    self.produtos.append(p)
                else:
                    self.produtos.append({"nome": p, "peso_produto": 1.0})

        self.subcategorias: List['Categoria'] = []
        self.peso_popularidade = peso_popularidade
        
    def incrementar_peso_produto(self, nome_produto: str, delta: float) -> bool:
        """Encontra produto pelo nome e incrementa peso_produto (retorna True se encontrado)."""
        with self._lock:
            for p in self.produtos:
                if p.get("nome") == nome_produto:
                    # garante chave peso_produto
                    p["peso_produto"] = float(p.get("peso_produto", 0.0)) + float(delta)
                    return True
        return False

    def incrementar_peso_popularidade_subcategoria(self, nome_subcategoria: str, delta: float) -> bool:
        """Se existir subcategoria com esse nome, incrementa seu peso_popularidade."""
        with self._lock:
            for sub in getattr(self, "subcategorias", []):
                if sub.nome == nome_subcategoria:
                    sub.peso_popularidade = float(getattr(sub, "peso_popularidade", 0.0)) + float(delta)
                    return True
        return False

    def incrementar_peso_popularidade_categoria(self, delta: float) -> None:
        """Incrementa o peso_popularidade desta categoria (sempre aplica)."""
        with self._lock:
            self.peso_popularidade = float(getattr(self, "peso_popularidade", 0.0)) + float(delta)
    # =============================================================
    # 🔧 Gerenciamento de produtos
    # =============================================================
    def adicionar_produto(self, produto: str, peso_produto: float = 1.0) -> None:
        """Adiciona produto à categoria (com peso individual)."""
        if not any(p["nome"] == produto for p in self.produtos):
            self.produtos.append({"nome": produto, "peso_produto": peso_produto})

    def remover_produto(self, produto: str) -> bool:
        """Remove produto da categoria."""
        for p in self.produtos:
            if p["nome"] == produto:
                self.produtos.remove(p)
                return True
        return False

    def aumentar_peso(self, incremento: float = 0.05) -> None:
        """Aumenta o peso de popularidade da categoria."""
        self.peso_popularidade = min(self.peso_popularidade + incremento, 10.0)

    def aumentar_peso_produto(self, produto_nome: str, incremento: float = 0.1) -> None:
        """Aumenta o peso de um produto específico."""
        for p in self.produtos:
            if p["nome"].lower() == produto_nome.lower():
                p["peso_produto"] = min(p["peso_produto"] + incremento, 10.0)
                break

    def get_total_produtos(self) -> int:
        """Total de produtos diretos nesta categoria."""
        return len(self.produtos)

    def get_produtos_ordenados_por_peso(self) -> List[Dict]:
        """Retorna os produtos ordenados do mais pesado ao mais leve."""
        return sorted(self.produtos, key=lambda x: x["peso_produto"], reverse=True)

    # =============================================================
    # 📂 Subcategorias
    # =============================================================
    def adicionar_subcategoria(self, subcategoria: 'Categoria') -> None:
        """Adiciona subcategoria, evitando duplicação."""
        if not any(sc.nome == subcategoria.nome for sc in self.subcategorias):
            self.subcategorias.append(subcategoria)

    def remover_subcategoria(self, nome_sub: str) -> bool:
        """Remove uma subcategoria pelo nome."""
        for sub in self.subcategorias:
            if sub.nome.lower() == nome_sub.lower():
                self.subcategorias.remove(sub)
                return True
        return False

    def imprimir_subcategorias(self, prefixo: str = "") -> None:
        """Imprime recursivamente subcategorias e produtos."""
        for i, subcat in enumerate(self.subcategorias):
            connector = "└── " if i == len(self.subcategorias) - 1 else "├── "
            linha = prefixo + connector + f"{subcat.nome} ({len(subcat.produtos)} produtos, peso={subcat.peso_popularidade:.2f})"
            print(linha)

            if subcat.produtos:
                produtos_preview = ', '.join(p["nome"] for p in subcat.produtos[:5])
                if len(subcat.produtos) > 5:
                    produtos_preview += "..."
                print(prefixo + ("    " if i == len(self.subcategorias) - 1 else "│   ") + f"└─ Produtos: {produtos_preview}")

            novo_prefixo = prefixo + ("    " if i == len(self.subcategorias) - 1 else "│   ")
            if subcat.subcategorias:
                subcat.imprimir_subcategorias(novo_prefixo)

    # =============================================================
    # 🧾 Representações e comparações
    # =============================================================
    def __str__(self) -> str:
        return f"Categoria({self.nome}, {len(self.produtos)} produtos)"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if isinstance(other, Categoria):
            return self.nome == other.nome
        return False

    def __lt__(self, other) -> bool:
        if isinstance(other, Categoria):
            return self.nome < other.nome
        return NotImplemented

    def __gt__(self, other) -> bool:
        if isinstance(other, Categoria):
            return self.nome > other.nome
        return NotImplemented

    def __le__(self, other) -> bool:
        if isinstance(other, Categoria):
            return self.nome <= other.nome
        return NotImplemented

    def __ge__(self, other) -> bool:
        if isinstance(other, Categoria):
            return self.nome >= other.nome
        return NotImplemented
