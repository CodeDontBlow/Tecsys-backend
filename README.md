# Tecsys Backend

Backend em **FastAPI** para processamento de PDFs, OCR, web scraping e integração com LLMs, utilizando banco de dados para armazenar os resultados.

---

## Requisitos

* **Python**: >=3.9, recomendado 3.9 a 3.13
* **Poetry**: >=2.0

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

### 4. Definir versão do Python para o projeto (opcional)

Se quiser usar uma versão específica (ex: Python 3.13):

```powershell
pyenv install 3.13.5   # se estiver usando pyenv
pyenv local 3.13.5
```

> Confirme:

```powershell
python --version
```

---

### 5. Criar/instalar dependências com Poetry

Instale as dependências listadas no `pyproject.toml`:

```powershell
poetry install
```

Isso criará um **ambiente virtual** isolado.

---

### 6. Ativar o ambiente virtual do Poetry

No Windows:

```powershell
poetry env info  # mostra o caminho do virtualenv
poetry env activate
```

No Linux/macOS:

```bash
source $(poetry env info --path)/bin/activate
```

> Depois disso, `python` e `pip` apontam para o ambiente do Poetry.

---

### 7. Instalar novas dependências (desenvolvimento)

Para instalar uma nova biblioteca e atualizar o `pyproject.toml`:

```powershell
poetry add <nome-da-biblioteca>
```

---

### 8. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz ou dentro de `core/`:

```env
DATABASE_URL=sqlite:///./db.sqlite3
```

---

### 9. Rodar o projeto

No terminal do ambiente virtual ativado:

```powershell
uvicorn app.main:app --reload
```

* O FastAPI estará disponível em [http://127.0.0.1:8000](http://127.0.0.1:8000)
* O parâmetro `--reload` ativa o auto-reload para desenvolvimento.

---

### 10. Acessar documentações

Acesse:

```powershell
http://127.0.0.1:8000/docs
```

Você verá a **interface Swagger** do FastAPI.

---

### Observações importantes

* Sempre ative o **virtualenv do Poetry** antes de rodar o `uvicorn`.
* Todas as bibliotecas do projeto estão isoladas nesse ambiente.
* Ao clonar o projeto em outro computador, basta rodar `poetry install` e ativar o ambiente.

---

### Referências

* [FastAPI](https://fastapi.tiangolo.com/)
* [Poetry](https://python-poetry.org/)
* [pydantic-settings](https://pydantic-docs.helpmanual.io/usage/settings/)
* [Uvicorn](https://www.uvicorn.org/)
