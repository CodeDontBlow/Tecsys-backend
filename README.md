# Tecsys Backend

Backend em **FastAPI** para processamento de PDFs com OCR, web scraping, web sockets e integração com LLMs, utilizando banco de dados para armazenar os resultados.

---

## Requisitos

* **Python**: >=3.9, recomendado 3.9 a 3.13
* **Poetry**: >=2.0
* **PostgreSQL**: >=13

> Testado no Windows 10/11 e Linux.

---

## Passo a passo para rodar o projeto

### 1. Instalar Python (se necessário)

Baixe e instale a versão recomendada do Python:
[https://www.python.org/downloads/](https://www.python.org/downloads/)

Confirme a versão:

```powershell
python --version
```

Deve ser >=3.9.

---

### 2. Instalar Poetry

Se você ainda não tiver o Poetry:

```powershell
pip install poetry
```

Verifique a instalação:

```powershell
poetry --version
```

---

### 3. Clonar o projeto

```powershell
git clone https://github.com/CodeDontBlow/Tecsys-backend.git
cd Tecsys-backend
```

---

### 4. Criar/instalar dependências com Poetry

```powershell
poetry install
```

Isso criará um **ambiente virtual** isolado.

---

### 5. Ativar o ambiente virtual do Poetry

```powershell
poetry env info  # mostra o caminho do virtualenv
poetry env activate # mostra o caminho para ativar o ambiente virtual
# copie e cole o comando retornado no terminal
```

| Caso não queira sempre ativar o ambiente virtual, você pode rodar os comandos com "poetry run" para sempre rodar com o ambiente virtual do poetry
``` bash
# exemplo
poetry run pip freeze
```

### 6. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto baseado no arquivo .env.example

---

## Dependências de banco de dados

### 1. Instalar PostgreSQL

Baixe e instale o PostgreSQL:
[https://www.postgresql.org/download/](https://www.postgresql.org/download/)

### 2. Criar o banco de dados

No terminal `psql`:

```sql
CREATE DATABASE descriptum;
```

### 3. Criar migrations via alembic

```powershell
alembic revision --autogenerate -m "message"
```

### 4. Aplicar migrations

```powershell
alembic upgrade head
```

> Isso criará todas as tabelas no banco PostgreSQL.
---

### 5. Setup inicial
Antes de rodar a API pela primeira vez, você precisa baixar a tabela NCM e popular o banco vetorial.

```bash
# run script
python -m app.scripts.setup 
```
---


### 6. Rodar o projeto

No terminal do ambiente virtual ativado:

```powershell
uvicorn app.main:app
```

* O FastAPI estará disponível em [http://127.0.0.1:8000](http://127.0.0.1:8000)


---

### 6. Acessar documentações

Acesse:

```powershell
http://127.0.0.1:8000/docs
```

Você verá a **interface Swagger** do FastAPI.

---

### Observações importantes

* Sempre ative o **virtualenv do Poetry** antes de rodar o `uvicorn`, ou utilize `poetry run uvicorn app.main:app`
* Todas as bibliotecas do projeto estão isoladas nesse ambiente.
* Ao clonar o projeto em outro computador, basta rodar `poetry install` e ativar o ambiente.
* Rode o `script.setup` **uma única vez** antes de iniciar a API.

---

### Referências

* [FastAPI](https://fastapi.tiangolo.com/)
* [Poetry](https://python-poetry.org/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [PostgreSQL](https://www.postgresql.org/)
