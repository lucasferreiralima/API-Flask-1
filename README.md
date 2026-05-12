# APIFlask Project

Esta é uma base estrutural para uma API Flask seguindo as melhores práticas, preparada para Docker e PostgreSQL.

## Estrutura do Projeto

O projeto utiliza o padrão **Application Factory** para melhor escalabilidade e testabilidade.

- `app/`: Pacote principal contendo a lógica da aplicação.
- `app/api/`: Blueprint para os endpoints da API.
- `app/models/`: Onde os modelos do SQLAlchemy devem ser criados.
- `tests/`: Testes automatizados com Pytest.
- `Dockerfile` & `docker-compose.yml`: Configurações para deploy e desenvolvimento em containers.

## Requisitos

- Docker e Docker Compose
- Python 3.11+ (se rodar localmente)

## Como rodar com Docker

1. Certifique-se de que o Docker está instalado e rodando.
2. Clone o repositório.
3. Execute o comando:
   ```bash
   docker-compose up --build
   ```
4. A API estará disponível em `http://localhost:5000/api`.

Endpoints disponíveis inicialmente:
- `GET /api/ping`: Verifica se a API está respondendo.
- `GET /api/health`: Verifica a saúde da API e a conexão com o banco de dados.

## Desenvolvimento Local (sem Docker)

1. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente no arquivo `.env` (baseie-se no `.env.example`).
4. Execute a aplicação:
   ```bash
   flask run
   ```

## Testes

Para rodar os testes:
```bash
pytest
```
