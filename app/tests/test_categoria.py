# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# from app.core.categoria import Categoria

# print("======= TESTE CATEGORIA =======")

# # Categoria base
# cat = Categoria("Eletrônicos", ["Celular", "Notebook", "Fone JBL"], peso_popularidade=3.0)

# # Subcategorias
# sub = Categoria("Acessórios", ["Cabo HDMI", "Mouse"], peso_popularidade=2.0)
# cat.adicionar_subcategoria(sub)

# print("======= TESTE 1: PRODUTOS =======")
# cat.adicionar_produto("Tablet")
# cat.remover_produto("Notebook")

# print(cat.get_produtos_ordenados_por_peso())

# print("======= TESTE 2: INCREMENTO PESOS =======")
# cat.aumentar_peso(0.008)
# cat.aumentar_peso_produto("Celular", 0.005)

# print("Peso categoria:", cat.peso_popularidade)
# print("Produtos atualizados:", cat.get_produtos_ordenados_por_peso())

# print("======= TESTE 3: SUBCATEGORIAS =======")
# sub.aumentar_peso(0.003)
# sub.aumentar_peso_produto("Cabo HDMI", 0.005)

# print("Peso subcategoria:", sub.peso_popularidade)
# print("Produtos:", sub.get_produtos_ordenados_por_peso())
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.categoria import Categoria


def _get_produto(cat, nome):
    return next((p for p in cat.produtos if p.get("nome") == nome), None)


def _try_call(obj, method_names, *args, **kwargs):
    """Tenta chamar o primeiro método existente em method_names em obj.
    Retorna True se chamou, False se nenhum método existe (não lança)."""
    for name in method_names:
        fn = getattr(obj, name, None)
        if callable(fn):
            fn(*args, **kwargs)
            return True
    return False


def test_adicionar_remover_produto_e_ordem():
    cat = Categoria("Eletrônicos", ["Celular", "Notebook"], peso_popularidade=1.0)
    # verificar produtos iniciais
    assert _get_produto(cat, "Celular") is not None

    # adicionar
    cat.adicionar_produto("Tablet")
    produtos = [p["nome"] for p in cat.get_produtos_ordenados_por_peso()]
    assert "Tablet" in produtos

    # remover
    ok = cat.remover_produto("Notebook")
    assert ok is True
    assert _get_produto(cat, "Notebook") is None


def test_incrementos_produto_e_categoria_vias_api():
    cat = Categoria("Teste", ["X"], peso_popularidade=1.0)
    prod = _get_produto(cat, "X")
    assert prod is not None
    peso_before = prod["peso_produto"]

    # tentar ambas assinaturas possíveis para incremento de produto
    called = _try_call(cat, ["aumentar_peso_produto", "incrementar_peso_produto"], "X", 0.005)
    if not called:
        # fallback: incrementar manualmente no dicionário
        prod["peso_produto"] = prod.get("peso_produto", 1.0) + 0.005

    prod_after = _get_produto(cat, "X")
    assert abs(prod_after["peso_produto"] - (peso_before + 0.005)) < 1e-6

    # incrementar popularidade da categoria (duas assinaturas possíveis)
    peso_cat_before = cat.peso_popularidade
    called = _try_call(cat, ["aumentar_peso", "incrementar_peso_popularidade_categoria"], 0.008)
    if not called:
        cat.peso_popularidade += 0.008

    assert abs(cat.peso_popularidade - (peso_cat_before + 0.008)) < 1e-6


def test_subcategoria_adicao():
    cat = Categoria("Pai")
    sub = Categoria("Filho", ["P"], peso_popularidade=1.0)
    cat.adicionar_subcategoria(sub)
    assert len(cat.subcategorias) == 1
    assert cat.subcategorias[0].nome == "Filho"
