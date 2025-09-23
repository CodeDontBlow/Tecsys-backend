# Tecsys Backend

Backend em **FastAPI** para processamento de PDFs, OCR, web scraping e integração com LLMs, utilizando banco de dados para armazenar os resultados.

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
cd tecsys-backend
```

---

### 4. Criar/instalar dependências com Poetry

```powershell
poetry install
```

Isso criará um **ambiente virtual** isolado.

---

### 5. Ativar o ambiente virtual do Poetry

No Windows:

```powershell
poetry env info  # mostra o caminho do virtualenv
poetry env activate
```

No Linux/macOS:

```bash
source $(poetry env info --path)/bin/activate
```

---

### 6. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/descriptum
```

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

### 5. Rodar o projeto

```powershell
uvicorn app.main:app --reload
```

* FastAPI disponível em [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Auto-reload ativado para desenvolvimento.

---

### Observações importantes

* Sempre ative o **virtualenv do Poetry** antes de rodar comandos.
---

### Referências

* [FastAPI](https://fastapi.tiangolo.com/)
* [Poetry](https://python-poetry.org/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [PostgreSQL](https://www.postgresql.org/)
