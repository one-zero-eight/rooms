# Rooms API in InNoHassle ecosystem

## Development

### Getting started

1. Install Python 3.11+

2. Install Poetry

3. Install dependencies

```bash
poetry install
```

4. Set up pre-commit hook

```bash
poetry run pre-commit install
```

5. Set up settings file

```bash
cp example.env .env
```

6. Create postgres database

```bash
psql -c 'CREATE DATABASE rooms_api_108_test;'
```

7. Upgrade database schemas

```bash
poetry run alembic upgrade head
```

### Run

```bash
poetry run uvicorn src.main:app --reload
```
