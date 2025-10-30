# Tecsys Backend

Um backend moderno desenvolvido em **FastAPI** para processamento inteligente de documentos, retornando os dados necessários para preencher o Registro de Importação e persistir no banco de dados para reutilização, equipado com capacidades de OCR, web scraping, comunicação em tempo real via WebSockets e integração com modelos de linguagem de grande escala (LLMs). O sistema utiliza PostgreSQL para armazenamento estruturado e ChromaDB para vector store e RAG, oferecendo APIs RESTful completas.

---

## Índice

1. [Requisitos do Sistema](#requisitos-do-sistema)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Instalação Manual](#instalação-manual)
   - [Pré-requisitos](#pré-requisitos)
   - [Configuração do Ambiente](#configuração-do-ambiente)
   - [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
   - [Execução da Aplicação](#execução-da-aplicação)
4. [Instalação com Docker](#instalação-com-docker)
5. [Configuração de Ambiente](#configuração-de-ambiente)
6. [Arquitetura e Componentes](#arquitetura-e-componentes)
7. [Documentação da API](#documentação-da-api)
8. [Desenvolvimento e Testes](#desenvolvimento-e-testes)
9. [Referências Técnicas](#referências-técnicas)

---

## Requisitos do Sistema

### Dependências Principais
- **Python**: Versão 3.9 ou superior (recomendado 3.9 a 3.13)
- **Poetry**: >=2.0 (gerenciamento de dependências)
- **PostgreSQL**: >=13 (banco de dados relacional)
- **ChromaDB**: >=0.4.0 (vector store para embeddings)

### Dependências Opcionais
- **Docker**: >=20.0
- **Docker Compose**: >=2.0

> **Ambientes Testados**: Windows 10/11, Linux (Ubuntu 20.04+, macOS 14+)

---

## Estrutura do Projeto

```
tecsys-backend/
├── 📁 app/                           # Código principal da aplicação
│   ├── 📁 api/                       # Definições de endpoints
│   │   ├── router_global.py          # Roteador principal
│   │   └── 📁 v1/                    # API versão 1
│   │       ├── routes.py             # Agregador de rotas
│   │       ├── description.py        # Geração de descrições
│   │       ├── imports.py            # Importação de dados
│   │       ├── manufacturer.py       # Fabricantes
│   │       ├── ncm.py                # Nomenclatura Comum do Mercosul
│   │       ├── order.py              # Ordens/pedidos
│   │       ├── pdf.py                # Processamento de PDF
│   │       ├── product.py            # Produtos
│   │       ├── supplier.py           # Fornecedores
│   │       ├── supplier_product.py   # Produtos por fornecedor
│   │       └── ws.py                 # WebSocket endpoints
│   ├── 📁 core/                      # Configurações centrais
│   │   ├── config.py                 # Configurações da aplicação
│   │   ├── dependencies.py           # Injeção de dependências
│   │   └── security.py               # Autenticação e segurança
│   ├── 📁 db/                        # Camada de dados
│   │   ├── database.py               # Configuração do PostgreSQL
│   │   └── 📁 chroma_db/             # Vector store (ChromaDB)
│   │       ├── config.py             # Configuração do Chroma
│   │       ├── embedding.py          # Geração de embeddings
│   │       ├── manager.py            # Gerenciamento do vector store
│   │       ├── model.py              # Modelos do Chroma
│   │       └── 📁 collection/        # Dados persistidos do Chroma
│   ├── 📁 libs/                      # Bibliotecas e utilitários
│   │   ├── 📁 extract_pdf/           # Processamento de PDF com OCR
│   │   │   ├── enterPDF.py           # Entrada de PDF
│   │   │   ├── extract_json.py       # Extração de JSON
│   │   │   ├── find_info.py          # Busca de informações
│   │   │   └── pdf2txt.py            # Conversão PDF para texto
│   │   ├── 📁 final_description/     # Geração de descrições
│   │   │   ├── generate_final_desc.py # Geração final
│   │   │   ├── clean_response.py     # Limpeza de respostas
│   │   │   └── modelfile_*           # Modelos para LLMs
│   │   ├── 📁 ncm/                   # Utilidades NCM
│   │   │   └── setup.py              # Setup da tabela NCM
│   │   ├── 📁 webscraping/           # Web scraping
│   │   │   ├── extractor.py          # Extrator de dados
│   │   │   ├── scrapper.py           # Scrapper principal
│   │   │   └── test_extractor.py     # Testes do extrator
│   │   └── 📁 websocket/             # Comunicação em tempo real
│   │       ├── manager.py            # Gerenciamento de conexões
│   │       └── worker.py             # Workers assíncronos
│   ├── 📁 log/                       # Sistema de logging
│   │   └── logger.py                 # Configuração de logs
│   ├── 📁 model/                     # Modelos SQLAlchemy
│   │   ├── base.py                   # Modelo base
│   │   ├── imports.py                # Modelo de importações
│   │   ├── manufacturer.py           # Modelo de fabricantes
│   │   ├── order.py                  # Modelo de ordens
│   │   ├── product.py                # Modelo de produtos
│   │   ├── supplier.py               # Modelo de fornecedores
│   │   └── supplier_product.py       # Modelo de produtos por fornecedor
│   ├── 📁 repositories/              # Padrão Repository
│   │   ├── repository_interface.py   # Interface base
│   │   ├── imports_repository.py     # Repositório de importações
│   │   ├── manufacturer_repository.py # Repositório de fabricantes
│   │   ├── order_repository.py       # Repositório de ordens
│   │   ├── product_repository.py     # Repositório de produtos
│   │   ├── supplier_repository.py    # Repositório de fornecedores
│   │   └── supplier_product_repository.py # Repositório de produtos por fornecedor
│   ├── 📁 schemas/                   # Schemas Pydantic
│   │   ├── imports.py                # Schemas de importação
│   │   ├── manufacturer.py           # Schemas de fabricantes
│   │   ├── order.py                  # Schemas de ordens
│   │   ├── product.py                # Schemas de produtos
│   │   ├── supplier.py               # Schemas de fornecedores
│   │   └── supplier_product.py       # Schemas de produtos por fornecedor
│   ├── 📁 services/                  # Lógica de negócio
│   ├── 📁 scripts/                   # Scripts de setup
│   │   └── setup.py                  # Setup inicial do sistema
│   ├── 📁 util/                      # Utilitários diversos
│   │   └── 📁 tipi/                  # Tabela TIPI (NCM)
│   │       ├── table_tipi.py         # Processamento da tabela
│   │       └── tipi_chapter_85.csv   # Dados do capítulo 85
│   └── main.py                       # Entry point da aplicação
├── 📁 migrations/                    # Migrações do Alembic
│   ├── env.py                        # Ambiente do Alembic
│   ├── script.py.mako                # Template de migrações
│   └── 📁 versions/                  # Histórico de migrações
│       └── 07d94313683a_initial_tables.py # Migração inicial
├── 📁 tests/                         # Testes automatizados
│   ├── 📁 crud/                      # Testes de CRUD
│   │   ├── test_imports_crud.py      # Testes de importação
│   │   ├── test_manufacturer_crud.py # Testes de fabricantes
│   │   ├── test_order_crud.py        # Testes de ordens
│   │   ├── test_product_crud.py      # Testes de produtos
│   │   ├── test_supplier_crud.py     # Testes de fornecedores
│   │   └── test_supplier_product_crud.py # Testes de produtos por fornecedor
│   ├── 📁 others/                    # Outros testes
│   │   ├── extract_info.py           # Testes de extração
│   │   ├── generate_desc.py          # Testes de geração de descrição
│   │   └── tipi.py                   # Testes da tabela TIPI
│   └── conftest.py                   # Configuração do pytest
├── 📄 .dockerignore                  # Ignorados no Docker
├── 📄 .env.example                   # Template de variáveis de ambiente
├── 📄 .gitignore                     # Padrões ignorados pelo Git
├── 📄 alembic.ini                    # Configuração do Alembic
├── 📄 docker-compose.yml             # Orquestração de containers
├── 📄 docker-entrypoint.py           # Script de inicialização Docker
├── 📄 Dockerfile                     # Definição da imagem Docker
├── 📄 LICENSE                        # Licença MIT
├── 📄 poetry.lock                    # Lock file do Poetry
├── 📄 pyproject.toml                 # Configuração do Poetry
└── 📄 README.md                      # Este arquivo
```

---

## Instalação Manual

### Pré-requisitos

#### 1. Instalação do Python

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev

# Windows
# Baixe do site oficial: https://www.python.org/downloads/

# Dica: Certifique-se de adicionar o pyhton ao PATH das variáveis de ambiente, normalmente fica em uma checkbox no início da instalação
```

Verifique a instalação:
```bash
python --version
# ou
python3 --version
```

#### 2. Instalação do Poetry

```bash
# Instalação via pip
pip install poetry

# Ou use o script oficial
curl -sSL https://install.python-poetry.org | python3 -
```

Verifique a instalação:
```bash
poetry --version
```

### Configuração do Ambiente

#### 3. Clonagem do Repositório

```bash
git clone https://github.com/CodeDontBlow/Tecsys-backend.git
cd Tecsys-backend
```

#### 4. Instalação de Dependências

```bash
# Instala todas as dependências do projeto
poetry install
```

#### 5. Ativação do Ambiente Virtual e env

```bash
# Ativar o ambiente virtual
poetry env activate
# Copie e cole o path retornado.
# Nota: No windowns, adicione o & para executar os comandos no poweshell.
# Caso esteja no linux/bash, adicione source no início.

# Alternativa: executar comandos diretamente com poetry run
poetry run python --version
```

```bash
# Copiar e configurar variáveis de ambiente
cp .env.example .env
# Editar o arquivo .env com suas configurações
```


### Configuração do Banco de Dados

#### 6. Instalação e Configuração do PostgreSQL

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# Windows
# Baixe do site oficial: https://www.postgresql.org/download/windows/
# Dica: Novamente, certifique-se de adicionar o PATH nas variáveis de ambiente, para poder usar os comandos do postgre no terminal
```

#### 7. Criação do Banco de Dados

```bash
# Acessar o PostgreSQL
sudo -u postgres psql

# Comando SQL para criar o banco 
CREATE DATABASE descriptum;
\d
```

#### 8. Configuração de Migrations

```bash
# Aplicar migrações existentes
alembic upgrade head
```

#### 9. Setup Inicial do Sistema

```bash
# Executar script de setup para preparar as dependencias internas do servidor.
poetry run python -m app.scripts.setup
```

> **Nota**: Este comando baixa e processa a tabela NCM, inicializa o ChromaDB e popula o banco vetorial. Baixa as llm necessárias para tradução e geração de descrições finais, e instala o chromium, para utilizar no websockets. Execute apenas na primeira instalação.

### Execução da Aplicação

#### 10. Iniciar o Servidor

```bash
# Desenvolvimento 
uvicorn app.main:app

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
> **Nota**: A opção --reload não é indicada pois está causando conflito com as operações assíncronas do servidor. 

---

## Instalação com Docker

### Configuração Rápida

#### 1. Clonagem do Repositório

```bash
git clone https://github.com/CodeDontBlow/Tecsys-backend.git
cd Tecsys-backend
```

#### 2. Configuração de Ambiente

```bash
# Copiar e configurar variáveis de ambiente
cp .env.example .env
# Editar o arquivo .env com suas configurações
```

#### 3. Build e Execução

```bash
# Build e execução dos containers
docker-compose up --build -d
```

> 1º Nota: A opcão --build força o rebuild das imagens antes de iniciar os containers e o -d executa os conainers em segundo plano.

> 2º Nota: Como o docker utiliza o mínimo para rodar a aplicação, será necessário baixar e instalar todas as dependencias externas e internas do projeto, tal qual llm's e popular o banco de dados vetorial, por isso, o processo pode demorar.


#### 4. Verificação dos Serviços

```bash
# Verificar status dos containers
docker-compose ps

# Ver logs da aplicação
docker-compose logs backend
# Pode usar o silgle dash -f para atualizar em tempo real os logs no terminal


# Ver logs do banco de dados
docker-compose logs db
```

#### 5. Parar e iniciar containers

```bash
# Para parar os containers
docker-compose down

# Para iniciar os containers
docker-compose up -d

```


### Configuração do Docker Compose

O arquivo `docker-compose.yml` define os seguintes serviços:

- **app**: Aplicação FastAPI na porta 8000
- **db**: Banco de dados PostgreSQL na porta 5432

---

## Configuração de Ambiente

### Variáveis de Ambiente Críticas

Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD= 
POSTGRES_DB=descriptum

# Caso esteja usando localhost, o host do db será localhost
POSTGRES_HOST=db
POSTGRES_PORT=5432




DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB} 
```

---

## Arquitetura e Componentes

### Camadas da Aplicação

1. **API Layer** (`app/api/`): Endpoints REST e WebSocket.
2. **Service Layer** (`app/services/`): Lógica de negócio.
3. **Repository Layer** (`app/repositories/`): Abstração de acesso a dados.
4. **Model Layer** (`app/model/`): Modelos de domínio e SQLAlchemy.
5. **Schema Layer** (`app/schemas/`): Schemas Pydantic para validação.
6. **Libs Layer** (`app/libs/`):Bibliotecas criadas para o desenvolvimento. 

### Componentes Principais

- **PDF Processing**: OCR e extração de texto com pypdf2 e Tesseract.
- **Web Scraping**: Coleta automatizada de dados de fornecedores e fabricantes.
- **Vector Search**: Busca semântica com ChromaDB.
- **LLM Integration**: Geração de descrições e traduções com modelos de linguagem.
- **WebSocket**: Atualizações em tempo real do processamento.
- **NCM Classification**: Classificação automática de produtos.

### Padrões de Design

- **Repository Pattern**: Isolamento da camada de dados.
- **Dependency Injection**: Gerenciamento nativo do FastAPI.
- **Factory Pattern**: Criação de serviços especializados.
- **Observer Pattern**: Notificações via WebSocket.

---

## Documentação da API

### Acessando a Documentação

Com o servidor rodando, acesse:

- **Swagger UI**: http://localhost:8000/docs

### Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/pdf/upload` | Upload e processamento de PDF |
| GET | `/api/v1/pdf/{id}` | Status do processamento |
| GET | `/api/v1/products` | Listagem de produtos |
| POST | `/api/v1/products` | Criação de produto |
| GET | `/api/v1/ncm/search` | Busca na tabela NCM |
| WS | `/ws/documents/{id}` | WebSocket para atualizações |

<!-- acredito que tenha que conferir ou colocar mais -->

### Exemplo de Upload de PDF

```bash
curl -X POST "http://localhost:8000/api/v1/pdf/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
```
> Ou se preferir, pode enviar o pdf via localhost:8000/docs. Encontre a rota upload pdf e clique em try out, coloque seu pdf na box e clique em execute.

---

## Desenvolvimento e Testes

### Executando Testes

```bash
# Todos os testes
poetry run pytest

# Testes específicos
poetry run pytest tests/crud/test_product_crud.py
```

### Estrutura de Testes

- **tests/crud/**: Testes de operações CRUD
- **tests/others/**: Testes de funcionalidades específicas
- **conftest.py**: Fixtures e configurações do pytest

---

## Referências Técnicas

### Frameworks e Bibliotecas Principais

- **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web moderno para APIs com Python 3.7+
- **[SQLAlchemy](https://www.sqlalchemy.org/)**: ORM e toolkit SQL para Python
- **[Alembic](https://alembic.sqlalchemy.org/)**: Ferramenta de migração de banco de dados
- **[Pydantic](https://docs.pydantic.dev/)**: Validação de dados usando type hints
- **[Poetry](https://python-poetry.org/)**: Gerenciamento de dependências e empacotamento

### Processamento de Documentos e Dados

- **[Tesseract OCR](https://github.com/tesseract-ocr/tesseract)**: Motor OCR para extração de texto
- **[ChromaDB](https://www.trychroma.com/)**: Vector store open-source para embeddings
- **[Ollama](https://www.ollama.com/)**: Framework para aplicações com LLMs
- **[Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)**: Web scraping e parsing HTML

### Banco de Dados

- **[PostgreSQL](https://www.postgresql.org/)**: Banco de dados relacional
- **[SQLite](https://www.sqlite.org/)**: Banco embutido para desenvolvimento

### Desenvolvimento e Deployment

- **[Docker](https://www.docker.com/)**: Containerização da aplicação
- **[Uvicorn](https://www.uvicorn.org/)**: Servidor ASGI de alta performance
- **[Pytest](https://docs.pytest.org/)**: Framework de testes para Python

### Integrações com LLMs

<!-- - **[OpenAI API](https://platform.openai.com/docs/api-reference)**: Integração com modelos GPT
- **[Anthropic Claude](https://docs.anthropic.com/claude/reference/)**: API para modelos Claude -->
- **[Ollama](https://ollama.ai/)**: Execução local de LLMs
- **[Ollama Model File](https://ollama.readthedocs.io/en/modelfile/)**: Modelfile para criar e configurar modelos de llm baseado em um existente.

### Boas Práticas Implementadas

- **12-Factor App**: Configuração via environment variables
- **Repository Pattern**: Separação entre lógica de negócio e acesso a dados
- **Dependency Injection**: Gerenciamento nativo do FastAPI
- **Async/Await**: Operações assíncronas para melhor performance
- **Type Hints**: Tipagem estática para melhor manutenibilidade
- **Testing Pyramid**: Testes unitários, de integração e e2e
- **API Versioning**: Versionamento claro da API
- **Comprehensive Logging**: Sistema de logs estruturado

### Padrões de API

- **RESTful Design**: Endpoints claros e métodos HTTP semânticos
- **WebSocket Support**: Comunicação bidirecional em tempo real
- **OpenAPI Documentation**: Documentação automática da API
- **Error Handling**: Tratamento consistente de erros

---

## Troubleshooting

### Problemas Comuns

1. **Erro de conexão com PostgreSQL**:
   - Verifique se o serviço do PostgreSQL está rodando
   - Confirme as credenciais no arquivo `.env`


3. **Erros de migração**:
   ```bash
   # Recriar do zero 
   alembic downgrade base
   alembic upgrade head
   ```

4. **Problemas com ChromaDB**:
   ```bash
   # Limpar e recriar o vector store
   rm -rf app/db/chroma_db/collection/*
   poetry run python -m app.scripts.setup
   ```

### Logs e Debug

```bash
# Ver logs da aplicação
docker-compose logs backend

# Logs com mais detalhes
docker-compose logs backend --tail=50 -f

# Acessar container para debugging
docker-compose exec -it backend bash
```

### Suporte

Para issues e dúvidas técnicas, consulte a documentação das tecnologias mencionadas ou abra uma issue no repositório do projeto.

# Com carinho, Code Don't Blow💣