# Wallet Test Application

## Requirements:

- `Docker`
- `Compose Plugin` or `Docker Compose`

## Installation

### Create `.env` file:
```shell
$ cp .env.example .env
```

### Deploy containers:
```shell
$ docker compose up -d
```

## Run tests:
```shell
$ docker compose exec web python manage.py test --settings=config.settings.testing
```

## Run coverage:
```shell
$ docker compose exec web coverage run manage.py test --settings=config.settings.testing
```

## Run linter:
```shell
$ docker compose exec web pylint apps
```
