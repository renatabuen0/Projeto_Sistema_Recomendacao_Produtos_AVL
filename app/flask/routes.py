import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from flask import Flask, request, jsonify, render_template
from app.core.arvore_avl import ArvoreAVL
from app.core.categoria import Categoria
from app.services.recomendacao_service import RecomendacaoService
from app.utils.logger import Logger

app = Flask(__name__)

# Inicializar componentes core
logger = Logger("SRHP-Web")
arvore = ArvoreAVL()
recomendador = RecomendacaoService(arvore)

def _carregar_dados_iniciais():
    """Carrega dados iniciais na árvore"""
    bebidas = Categoria("Bebidas", ["Suco de Uva", "Refrigerante", "Água Mineral"], peso_popularidade=4.0)
    eletronicos = Categoria("Eletrônicos", ["Celular", "Notebook", "Fone JBL"], peso_popularidade=3.0)
    acessorios = Categoria("Acessórios", ["Cabo HDMI", "Mouse Gamer"], peso_popularidade=2.0)
    eletronicos.adicionar_subcategoria(acessorios)
    bananinha = Categoria("Bananinha", ["Banana Chips", "Banana Passa"], peso_popularidade=5.0)
    bananas_gourmet = Categoria("Bananas Gourmet", ["Banana Flambada", "Banana com Chocolate"], peso_popularidade=2.0)
    bananinha.adicionar_subcategoria(bananas_gourmet)
    for c in [bebidas, eletronicos, bananinha]:
        arvore.inserir_publico(c)
    recomendador.reindexar()

# Carregar dados iniciais
_carregar_dados_iniciais()

# ==========================================
# ROTAS WEB (Interface)
# ==========================================

@app.route('/')
def homepage():
    return render_template('index.html')

# ==========================================
# API REST - PRODUTOS
# ==========================================

@app.route('/api/produtos', methods=['GET'])
def get_produtos():
    """Lista todos os produtos com paginação opcional"""
    try:
        pagina = int(request.args.get('pagina', 1))
        limite = int(request.args.get('limite', 50))

        todos_produtos = recomendador.listar_todos_produtos()
        inicio = (pagina - 1) * limite
        fim = inicio + limite

        produtos_paginados = todos_produtos[inicio:fim]

        return jsonify({
            'produtos': produtos_paginados,
            'total': len(todos_produtos),
            'pagina': pagina,
            'limite': limite,
            'paginas_totais': (len(todos_produtos) + limite - 1) // limite
        })
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/produtos/buscar', methods=['GET'])
def buscar_produtos():
    """Busca produtos por prefixo"""
    try:
        prefixo = request.args.get('q', '').strip()
        limite = int(request.args.get('limite', 15))

        if not prefixo:
            return jsonify({'erro': 'Parâmetro de busca "q" é obrigatório'}), 400

        resultados = recomendador.sugerir_por_prefixo(prefixo, limite=limite)

        return jsonify({
            'query': prefixo,
            'resultados': resultados,
            'total': len(resultados)
        })
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/produtos', methods=['POST'])
def criar_produto():
    """Cria um novo produto"""
    try:
        dados = request.get_json()

        if not dados or 'nome' not in dados:
            return jsonify({'erro': 'Nome do produto é obrigatório'}), 400

        categoria_nome = dados.get('categoria')
        subcategoria_nome = dados.get('subcategoria')

        if not categoria_nome:
            return jsonify({'erro': 'Nome da categoria é obrigatório'}), 400

        categoria = arvore.buscar_publico(categoria_nome)
        if not categoria:
            return jsonify({'erro': f'Categoria "{categoria_nome}" não encontrada'}), 404

        if subcategoria_nome:
            subcategoria = next((s for s in categoria.subcategorias if s.nome.lower() == subcategoria_nome.lower()), None)
            if not subcategoria:
                return jsonify({'erro': f'Subcategoria "{subcategoria_nome}" não encontrada'}), 404
            subcategoria.adicionar_produto(dados['nome'])
        else:
            categoria.adicionar_produto(dados['nome'])

        recomendador.reindexar()

        logger.info(f"Produto criado: {dados['nome']} em {categoria_nome}")
        return jsonify({
            'mensagem': 'Produto criado com sucesso',
            'produto': dados['nome'],
            'categoria': categoria_nome,
            'subcategoria': subcategoria_nome
        }), 201

    except Exception as e:
        logger.error(f"Erro ao criar produto: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/produtos/<categoria>/<produto>', methods=['PUT'])
def atualizar_produto(categoria, produto):
    """Atualiza um produto (incrementa peso)"""
    try:
        categoria_obj = arvore.buscar_publico(categoria)
        if not categoria_obj:
            return jsonify({'erro': f'Categoria "{categoria}" não encontrada'}), 404

        # Procurar produto na categoria ou subcategorias
        produto_encontrado = False
        subcategoria_nome = None

        # Verificar subcategorias primeiro
        for sub in categoria_obj.subcategorias:
            if sub.remover_produto(produto):  # remove temporariamente para verificar se existe
                sub.adicionar_produto(produto)  # readiciona
                subcategoria_nome = sub.nome
                produto_encontrado = True
                break

        # Se não encontrou em subcategorias, verificar na categoria principal
        if not produto_encontrado:
            if categoria_obj.remover_produto(produto):  # remove temporariamente
                categoria_obj.adicionar_produto(produto)  # readiciona
                produto_encontrado = True

        if not produto_encontrado:
            return jsonify({'erro': f'Produto "{produto}" não encontrado'}), 404

        # Aplicar incrementos conforme regras SRHP
        categoria_obj.aumentar_peso(0.008)

        if subcategoria_nome:
            subcategoria = next((s for s in categoria_obj.subcategorias if s.nome == subcategoria_nome), None)
            if subcategoria:
                subcategoria.aumentar_peso(0.003)
                subcategoria.aumentar_peso_produto(produto, 0.005)
        else:
            categoria_obj.aumentar_peso_produto(produto, 0.005)

        recomendador.reindexar()

        logger.info(f"Produto atualizado: {produto} em {categoria}")
        return jsonify({
            'mensagem': 'Produto atualizado com sucesso',
            'produto': produto,
            'categoria': categoria,
            'subcategoria': subcategoria_nome,
            'incrementos': {
                'categoria': '+0.008',
                'subcategoria': '+0.003' if subcategoria_nome else None,
                'produto': '+0.005'
            }
        })

    except Exception as e:
        logger.error(f"Erro ao atualizar produto: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/produtos/<categoria>/<produto>', methods=['DELETE'])
def deletar_produto(categoria, produto):
    """Remove um produto"""
    try:
        categoria_obj = arvore.buscar_publico(categoria)
        if not categoria_obj:
            return jsonify({'erro': f'Categoria "{categoria}" não encontrada'}), 404

        removido = categoria_obj.remover_produto(produto)

        if not removido:
            # Tentar remover de subcategorias
            for sub in categoria_obj.subcategorias:
                if sub.remover_produto(produto):
                    removido = True
                    break

        if not removido:
            return jsonify({'erro': f'Produto "{produto}" não encontrado'}), 404

        recomendador.reindexar()

        logger.info(f"Produto removido: {produto} de {categoria}")
        return jsonify({
            'mensagem': 'Produto removido com sucesso',
            'produto': produto,
            'categoria': categoria
        })

    except Exception as e:
        logger.error(f"Erro ao remover produto: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

# ==========================================
# API REST - CATEGORIAS
# ==========================================

@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    """Lista todas as categorias"""
    try:
        categorias = []
        for cat in arvore.listar_todas():
            categorias.append({
                'nome': cat.nome,
                'peso_popularidade': cat.peso_popularidade,
                'produtos_count': len(cat.get_produtos_ordenados_por_peso()),
                'subcategorias_count': len(cat.subcategorias),
                'subcategorias': [s.nome for s in cat.subcategorias]
            })

        return jsonify({
            'categorias': categorias,
            'total': len(categorias)
        })
    except Exception as e:
        logger.error(f"Erro ao listar categorias: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/categorias', methods=['POST'])
def criar_categoria():
    """Cria uma nova categoria"""
    try:
        dados = request.get_json()

        if not dados or 'nome' not in dados:
            return jsonify({'erro': 'Nome da categoria é obrigatório'}), 400

        nome = dados['nome'].strip()
        if not nome:
            return jsonify({'erro': 'Nome da categoria não pode ser vazio'}), 400

        if arvore.buscar_publico(nome):
            return jsonify({'erro': f'Categoria "{nome}" já existe'}), 409

        categoria = Categoria(nome)
        arvore.inserir_publico(categoria)
        recomendador.reindexar()

        logger.info(f"Categoria criada: {nome}")
        return jsonify({
            'mensagem': 'Categoria criada com sucesso',
            'categoria': {
                'nome': nome,
                'peso_popularidade': categoria.peso_popularidade
            }
        }), 201

    except Exception as e:
        logger.error(f"Erro ao criar categoria: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/categorias/<nome>', methods=['GET'])
def get_categoria(nome):
    """Obtém detalhes de uma categoria específica"""
    try:
        categoria = arvore.buscar_publico(nome)
        if not categoria:
            return jsonify({'erro': f'Categoria "{nome}" não encontrada'}), 404

        produtos = categoria.get_produtos_ordenados_por_peso()
        subcategorias = []

        for sub in categoria.subcategorias:
            subcategorias.append({
                'nome': sub.nome,
                'peso_popularidade': sub.peso_popularidade,
                'produtos': sub.get_produtos_ordenados_por_peso()
            })

        return jsonify({
            'categoria': {
                'nome': categoria.nome,
                'peso_popularidade': categoria.peso_popularidade,
                'produtos': produtos,
                'subcategorias': subcategorias
            }
        })

    except Exception as e:
        logger.error(f"Erro ao obter categoria: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/categorias/<nome>', methods=['DELETE'])
def deletar_categoria(nome):
    """Remove uma categoria"""
    try:
        removida = arvore.remover_publico(nome)
        if not removida:
            return jsonify({'erro': f'Categoria "{nome}" não encontrada'}), 404

        recomendador.reindexar()

        logger.info(f"Categoria removida: {nome}")
        return jsonify({
            'mensagem': 'Categoria removida com sucesso',
            'categoria': nome
        })

    except Exception as e:
        logger.error(f"Erro ao remover categoria: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

# ==========================================
# API REST - SUBCATEGORIAS
# ==========================================

@app.route('/api/categorias/<categoria>/subcategorias', methods=['GET'])
def get_subcategorias(categoria):
    """Lista as subcategorias de uma categoria"""
    try:
        categoria_obj = arvore.buscar_publico(categoria)
        if not categoria_obj:
            return jsonify({'erro': f'Categoria "{categoria}" não encontrada'}), 404

        subcategorias = []
        for sub in categoria_obj.subcategorias:
            subcategorias.append({
                'nome': sub.nome,
                'peso_popularidade': sub.peso_popularidade,
                'produtos_count': len(sub.get_produtos_ordenados_por_peso())
            })

        return jsonify({
            'categoria': categoria,
            'subcategorias': subcategorias,
            'total': len(subcategorias)
        })

    except Exception as e:
        logger.error(f"Erro ao listar subcategorias: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/categorias/<categoria>/subcategorias', methods=['POST'])
def criar_subcategoria(categoria):
    """Cria uma subcategoria dentro de uma categoria"""
    try:
        dados = request.get_json()

        if not dados or 'nome' not in dados:
            return jsonify({'erro': 'Nome da subcategoria é obrigatório'}), 400

        categoria_obj = arvore.buscar_publico(categoria)
        if not categoria_obj:
            return jsonify({'erro': f'Categoria "{categoria}" não encontrada'}), 404

        nome_sub = dados['nome'].strip()
        if not nome_sub:
            return jsonify({'erro': 'Nome da subcategoria não pode ser vazio'}), 400

        # Verificar se já existe
        if any(s.nome.lower() == nome_sub.lower() for s in categoria_obj.subcategorias):
            return jsonify({'erro': f'Subcategoria "{nome_sub}" já existe em "{categoria}"'}), 409

        subcategoria = Categoria(nome_sub)
        categoria_obj.adicionar_subcategoria(subcategoria)
        recomendador.reindexar()

        logger.info(f"Subcategoria criada: {nome_sub} em {categoria}")
        return jsonify({
            'mensagem': 'Subcategoria criada com sucesso',
            'categoria': categoria,
            'subcategoria': {
                'nome': nome_sub,
                'peso_popularidade': subcategoria.peso_popularidade
            }
        }), 201

    except Exception as e:
        logger.error(f"Erro ao criar subcategoria: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/categorias/<categoria>/subcategorias/<subcategoria>', methods=['DELETE'])
def deletar_subcategoria(categoria, subcategoria):
    """Remove uma subcategoria"""
    try:
        categoria_obj = arvore.buscar_publico(categoria)
        if not categoria_obj:
            return jsonify({'erro': f'Categoria "{categoria}" não encontrada'}), 404

        removida = False
        for s in list(categoria_obj.subcategorias):
            if s.nome.lower() == subcategoria.lower():
                categoria_obj.subcategorias.remove(s)
                removida = True
                break

        if not removida:
            return jsonify({'erro': f'Subcategoria "{subcategoria}" não encontrada em "{categoria}"'}), 404

        recomendador.reindexar()

        logger.info(f"Subcategoria removida: {subcategoria} de {categoria}")
        return jsonify({
            'mensagem': 'Subcategoria removida com sucesso',
            'categoria': categoria,
            'subcategoria': subcategoria
        })

    except Exception as e:
        logger.error(f"Erro ao remover subcategoria: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

# ==========================================
# API REST - COLEÇÃO (ÁRVORE COMPLETA)
# ==========================================

@app.route('/api/colecao', methods=['GET'])
def get_colecao():
    """Obtém a coleção completa (árvore AVL)"""
    try:
        relatorio = recomendador.gerar_relatorio_performance()

        colecao = {
            'metadata': {
                'total_categorias': arvore.get_tamanho(),
                'altura_arvore': relatorio.get('altura'),
                'balanceada': relatorio.get('balanceada'),
                'total_produtos': len(recomendador.listar_todos_produtos()),
                'complexidade': relatorio.get('complexidade', {})
            },
            'categorias': []
        }

        for cat in arvore.listar_todas():
            categoria_data = {
                'nome': cat.nome,
                'peso_popularidade': cat.peso_popularidade,
                'produtos': cat.get_produtos_ordenados_por_peso(),
                'subcategorias': []
            }

            for sub in cat.subcategorias:
                sub_data = {
                    'nome': sub.nome,
                    'peso_popularidade': sub.peso_popularidade,
                    'produtos': sub.get_produtos_ordenados_por_peso()
                }
                categoria_data['subcategorias'].append(sub_data)

            colecao['categorias'].append(categoria_data)

        return jsonify(colecao)

    except Exception as e:
        logger.error(f"Erro ao obter coleção: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/colecao/reset', methods=['POST'])
def reset_colecao():
    """Reseta a coleção para os dados iniciais"""
    try:
        # Limpar árvore atual
        for cat in arvore.listar_todas():
            arvore.remover_publico(cat.nome)

        # Recarregar dados iniciais
        _carregar_dados_iniciais()

        logger.info("Coleção resetada para dados iniciais")
        return jsonify({
            'mensagem': 'Coleção resetada com sucesso',
            'status': 'dados_iniciais_carregados'
        })

    except Exception as e:
        logger.error(f"Erro ao resetar coleção: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

# ==========================================
# API REST - ESTATÍSTICAS E RELATÓRIOS
# ==========================================

@app.route('/api/estatisticas', methods=['GET'])
def get_estatisticas():
    """Obtém estatísticas gerais do sistema"""
    try:
        relatorio = recomendador.gerar_relatorio_performance()
        produtos = recomendador.listar_todos_produtos()

        estatisticas = {
            'arvore_avl': {
                'altura': relatorio.get('altura'),
                'balanceada': relatorio.get('balanceada'),
                'total_categorias': arvore.get_tamanho()
            },
            'produtos': {
                'total': len(produtos),
                'categorias_com_produtos': len([c for c in arvore.listar_todas() if c.get_produtos_ordenados_por_peso()])
            },
            'complexidade': relatorio.get('complexidade', {}),
            'timestamp': str(request.args.get('timestamp', 'now'))
        }

        return jsonify(estatisticas)

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500