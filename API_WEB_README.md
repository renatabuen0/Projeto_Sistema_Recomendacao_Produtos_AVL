# SRHP - API Web REST

## Visão Geral

O Sistema de Recomendação Hierárquica de Produtos (SRHP) oferece uma API REST completa para integração web, permitindo operações CRUD completas sobre produtos, categorias e a coleção de dados.

## 🚀 Como Executar

### 1. Instalar Dependências
Recomendamos o uso de um ambiente virtual (`venv`) para isolar as dependências do projeto.

```bash
# 1. Criar o ambiente virtual
python -m venv venv

# 2. Ativar o ambiente virtual
# No Windows:
.\venv\Scripts\activate
# No Linux/macOS:
source venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt
```

### 2. Executar a Aplicação (GUI + API)
O arquivo `main.py` inicia a **Interface Gráfica (GUI)** do sistema e, simultaneamente, coloca o servidor da API Web em execução em uma thread separada.

```bash
cd app
python main.py
```

- A **Interface Gráfica** será aberta em uma nova janela.
- O **Servidor Web** estará disponível em: `http://127.0.0.1:5000`

### 3. Acessar a Interface Web
- Abra seu navegador em: `http://127.0.0.1:5000`
- A interface web mostra estatísticas em tempo real e documentação da API

## 📚 Endpoints da API

### 🔍 Busca e Listagem

#### `GET /api/produtos`
Lista todos os produtos com paginação opcional.

**Parâmetros de Query:**
- `pagina` (int, opcional): Página atual (padrão: 1)
- `limite` (int, opcional): Itens por página (padrão: 50)

**Exemplo:**
```bash
curl "http://localhost:5000/api/produtos?pagina=1&limite=10"
```

#### `GET /api/produtos/buscar`
Busca produtos por prefixo.

**Parâmetros de Query:**
- `q` (string, obrigatório): Termo de busca
- `limite` (int, opcional): Máximo de resultados (padrão: 15)

**Exemplo:**
```bash
curl "http://localhost:5000/api/produtos/buscar?q=banana&limite=5"
```

#### `GET /api/categorias`
Lista todas as categorias com detalhes.

#### `GET /api/colecao`
Obtém a coleção completa (árvore AVL inteira) com metadados.

### ➕ Criação (POST)

#### `POST /api/produtos`
Cria um novo produto.

**Body JSON:**
```json
{
  "nome": "Nome do Produto",
  "categoria": "Nome da Categoria",
  "subcategoria": "Nome da Subcategoria (opcional)"
}
```

**Exemplo:**
```bash
curl -X POST "http://localhost:5000/api/produtos" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Novo Produto", "categoria": "Bebidas"}'
```

#### `POST /api/categorias`
Cria uma nova categoria.

**Body JSON:**
```json
{
  "nome": "Nome da Categoria"
}
```

#### `POST /api/categorias/{categoria}/subcategorias`
Cria uma subcategoria dentro de uma categoria existente.

**Body JSON:**
```json
{
  "nome": "Nome da Subcategoria"
}
```

### ✏️ Atualização (PUT)

#### `PUT /api/produtos/{categoria}/{produto}`
Atualiza um produto incrementando sua popularidade conforme as regras SRHP:
- Categoria: +0.008
- Subcategoria: +0.003 (se existir)
- Produto: +0.005

**Exemplo:**
```bash
curl -X PUT "http://localhost:5000/api/produtos/Bebidas/Suco%20de%20Uva"
```

### 🗑️ Remoção (DELETE)

#### `DELETE /api/produtos/{categoria}/{produto}`
Remove um produto da categoria ou subcategoria.

#### `DELETE /api/categorias/{nome}`
Remove uma categoria completamente.

#### `DELETE /api/categorias/{categoria}/subcategorias/{subcategoria}`
Remove uma subcategoria de uma categoria.

### 🔧 Utilitários

#### `GET /api/estatisticas`
Obtém estatísticas gerais do sistema (altura da árvore, balanceamento, contadores, etc.).

#### `POST /api/colecao/reset`
Reseta a coleção completa para os dados iniciais de demonstração.

## 📊 Estrutura de Respostas

### Resposta de Produto
```json
{
  "nome": "Produto X",
  "categoria": "Categoria A > Subcategoria B",
  "peso_produto": 1.005
}
```

### Resposta de Categoria
```json
{
  "nome": "Bebidas",
  "peso_popularidade": 4.008,
  "produtos_count": 3,
  "subcategorias_count": 0,
  "subcategorias": []
}
```

### Resposta de Coleção
```json
{
  "metadata": {
    "total_categorias": 3,
    "altura_arvore": 2,
    "balanceada": true,
    "total_produtos": 12,
    "complexidade": {
      "insercao": "O(log n)",
      "busca": "O(log n)",
      "recomendacao": "O(n)"
    }
  },
  "categorias": [...]
}
```

## ⚠️ Tratamento de Erros

A API retorna códigos HTTP apropriados:

- `200`: Sucesso
- `201`: Criado com sucesso
- `400`: Dados inválidos
- `404`: Recurso não encontrado
- `409`: Conflito (recurso já existe)
- `500`: Erro interno do servidor

**Exemplo de erro:**
```json
{
  "erro": "Categoria 'X' não encontrada"
}
```

## 🧪 Testando a API

### Com cURL
```bash
# Ver coleção completa
curl "http://localhost:5000/api/colecao"

# Buscar produtos
curl "http://localhost:5000/api/produtos/buscar?q=cel"

# Criar produto
curl -X POST "http://localhost:5000/api/produtos" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Produto Teste", "categoria": "Eletrônicos"}'
```

### Com Python
```python
import requests

# Buscar produtos
response = requests.get('http://localhost:5000/api/produtos/buscar?q=banana')
produtos = response.json()
print(produtos)

# Criar categoria
nova_categoria = {'nome': 'Nova Categoria'}
response = requests.post('http://localhost:5000/api/categorias', json=nova_categoria)
print(response.json())
```

## 🔧 Desenvolvimento

### Estrutura do Projeto
```
app/flask/
├── app.py          # Configuração Flask e CORS
├── routes.py       # Todas as rotas da API
└── templates/
    ├── index.html  # Interface web
    └── pagina1.html
```

### Logs
Todos os logs são gravados no diretório `logs/` com timestamps detalhados.

## 📈 Performance

- **Busca AVL**: O(log n)
- **Recomendação por prefixo**: O(n)
- **Atualização de pesos**: O(1)
- **Inserção/Remoção**: O(log n)

A árvore AVL mantém o balanceamento automático para garantir performance ótima.