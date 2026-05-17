# Template básico com estrutura do projeto
- VirtualEnv para Python
- Crie e ative um ambiente virtual antes de instalar dependências:

```sh
python3 -m venv venv
source venv/bin/activate
```

# Ordem de execução
1. Subir o banco de dados:

```sh
docker compose up -d
```

2. Executar ingestão do PDF:

```sh
python src/ingest.py
```

3. Rodar o chat:

```sh
python src/chat.py
```