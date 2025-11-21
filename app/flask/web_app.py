import sys
import os

# Adicionar o diretório raiz do projeto ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from flask import Flask
from flask_cors import CORS
from app.services.recomendacao_service import RecomendacaoService

# Configurações da aplicação
# app.config['JSON_SORT_KEYS'] = False  # Movido para depois do import
# app.config['JSON_AS_ASCII'] = False

try:
    from app.flask.routes import app
    import app.flask.routes as routes_module
except ImportError:
    from routes import app
    import routes as routes_module

# Habilitar CORS para todas as rotas
CORS(app)

app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False

def run_api(arvore_compartilhada=None):
    """
    Inicia a API.
    :param arvore_compartilhada: Instância opcional de ArvoreAVL para compartilhar estado.
    """
    if arvore_compartilhada:
        print("🔗 Conectando Web API à árvore compartilhada...")
        routes_module.arvore = arvore_compartilhada
        routes_module.recomendador = RecomendacaoService(arvore_compartilhada)
        # Reindexar para garantir sincronia inicial
        routes_module.recomendador.reindexar()

    print("🚀 Iniciando SRHP Web API...")
    print("📡 Servidor rodando em: http://127.0.0.1:5000")
    print("📚 Documentação da API disponível em: /api/colecao")
    # use_reloader=False é necessário para rodar em thread
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == '__main__':
    run_api()


