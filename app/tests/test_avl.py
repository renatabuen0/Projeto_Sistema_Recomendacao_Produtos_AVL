# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# from app.core.arvore_avl import ArvoreAVL
# from app.core.categoria import Categoria

# print("======= TESTE AVL =======")

# # Inicialização
# arvore = ArvoreAVL()

# # Categorias
# cat1 = Categoria("Pokébolas", ["Poké ball", "Great Ball", "Ultra ball"], 3)
# cat2 = Categoria("Medicamentos", ["Poção", "Super Poção", "Hiper Poção"], 2)
# cat3 = Categoria("Itens de Batalha", ["X-Attack", "X-Defense"])
# cat4 = Categoria("Itens de Evolução", ["Magmarizer", "Metal Coat"], 5)

# # Subcategorias
# sub1 = Categoria("Pokébolas Especiais", ["Dream Ball", "Beast Ball"], 4)
# sub2 = Categoria("Pokébolas de Johto", ["Moon Ball", "Fast Ball"], 3)
# cat1.adicionar_subcategoria(sub1)
# cat1.adicionar_subcategoria(sub2)

# sub3 = Categoria("Pedras Evolutivas", ["Fire Stone", "Leaf Stone"], 7)
# cat4.adicionar_subcategoria(sub3)

# print("======= TESTE 1: INSERÇÃO =======")
# arvore.inserir_publico(cat1)
# arvore.inserir_publico(cat2)
# arvore.inserir_publico(cat3)
# arvore.inserir_publico(cat4)
# arvore.imprimir_arvore()

# print("======= TESTE 2: REMOÇÃO SIMPLES =======")
# arvore.remover_publico("Itens de Batalha")
# arvore.imprimir_arvore()

# print("======= TESTE 3: NOVA INSERÇÃO =======")
# cat5 = Categoria("TMs", ["TM01", "TM44"])
# arvore.inserir_publico(cat5)
# arvore.imprimir_arvore()

# print("======= TESTE 4: PRODUTOS =======")
# arvore.buscar_publico("Pokébolas").adicionar_produto("Master Ball")
# arvore.buscar_publico("Pokébolas").subcategorias[0].adicionar_produto("Safari Ball")
# arvore.imprimir_arvore()




import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.arvore_avl import ArvoreAVL
from app.core.categoria import Categoria


def test_inserir_e_buscar_remover():
    arv = ArvoreAVL()
    c1 = Categoria("Bebidas")
    c2 = Categoria("Eletrônicos")
    c3 = Categoria("Acessórios")

    arv.inserir_publico(c1)
    arv.inserir_publico(c2)
    arv.inserir_publico(c3)

    assert arv.get_tamanho() == 3
    assert arv.buscar_publico("Bebidas") is not None
    assert arv.buscar_publico("Eletrônicos") is not None

    ok = arv.remover_publico("Acessórios")
    assert ok is True
    assert arv.buscar_publico("Acessórios") is None
    assert arv.get_tamanho() == 2


def test_rotacao_basica_balanceamento():
    arv = ArvoreAVL()

    arv.inserir_publico(Categoria("C"))
    arv.inserir_publico(Categoria("B"))
    arv.inserir_publico(Categoria("A"))  # deve provocar rotação simples

    # raiz deve existir e árvore balanceada
    assert arv.raiz is not None
    assert arv.buscar_publico("B") is not None


def test_listar_todas_ordenacao():
    arv = ArvoreAVL()
    arv.inserir_publico(Categoria("B"))
    arv.inserir_publico(Categoria("A"))
    arv.inserir_publico(Categoria("C"))

    lista = arv.listar_todas()
    nomes = [c.nome for c in lista]
    assert nomes == ["A", "B", "C"]
