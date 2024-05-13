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

5. Set up settings file.
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
poetry run fastapi dev src/main.py
```

## Via Docker

Check the `DB_URL` setting in `.env` file.
```bash
docker build . -t innohassle-rooms-api
```
```bash
docker run --rm -ti -d -p 80:80 --env-file .env innohassle-rooms-api
```

## Usage

Send requests with `X-Token` header (generated by `src.api.auth.utils.create_jwt({'sub': 'tgbot'})`) to verify you are the bot.
