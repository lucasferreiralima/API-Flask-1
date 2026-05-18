#!/bin/bash
# boot.sh - Automatização de Inicialização da VettoreFlow

echo "Iniciando processo de boot da aplicação..."

# 1. Tentar inicializar o diretório de migrações se não existir
if [ ! -d "migrations" ]; then
    echo "Inicializando sistema de migrações..."
    flask db init
fi

# 2. Gerar e Aplicar Migrações (Cria as tabelas no Postgres/SQLite)
echo "Gerando e aplicando migrações..."
flask db migrate -m "Auto migration via boot"
flask db upgrade

# 3. Alimentar o Banco com o Seed (15 registros)
echo "Executando seeding de dados..."
python seed.py

# 4. Iniciar o servidor Gunicorn
echo "Subindo servidor de produção (Gunicorn)..."
exec gunicorn --bind 0.0.0.0:5000 --access-logfile - --error-logfile - wsgi:app
