# test-healthcheck
Test task before an interview

## Task description:
Implement URL healthcheck service using python

Application should be started with the following params:
  - interval – Polling interval (seconds)
  - urls – List of URLs to check

"Healthcheck" means that HTTP GET request to the URL responds with
successful status code.

All checks are stored in the database - date, URL, status.

There also should be a public API with a single endpoint:

`/status` – All the data about checks from the DB, encoded as JSON

Technical requirements:
- PostgreSQL
- Python
- All services (including the DB) are wrapped into Docker container
- All services are managed via `docker-compose`

## Project structure
- `backend` – Public API for listing statuses. Written using `bottle` (cause it's
deadly simple server) and `SQLAlchemy`
- `worker` – Application for URLs polling. Written using `asyncio` and `asyncpg`
- `pg-init-scripts` – PostgreSQL helpers for bootstrapping multiple databases

There are 2 services which work with the common DB. To avoid any schema synchronization
problems, `backend` is the app responsible for tables bootstrapping as well as database
migrations. `worker` app is simply depends on the `backend` and starts only after backend
is started (and therefore after database is ready).

#### Pre-commit hooks
There are some [pre-commit](https://pre-commit.com/) hooks configured per this project.
To install them:
```shell script
pre-commit install-hooks
```

## Configuration

Configuration is achieved via .env file. After project checkout, create a copy
of `.env.tmpl` and call it `.env`.
```shell script
cp .env.tmpl .env
```
Modify it by your needs. All parameters should be self-explanatory.

## How to run
Make sure to [configure](##Configuration) `.env` file.
There are 2 docker-compose configuration files. To run service in production:
```bash
docker-compose up
```

Then check everything works as expected:
```shell script
curl localhost:8080/status
[
  {
    "ok": false,
    "code": 404,
    "elapsed": 0.439211,
    "date": "2020-07-02T11:41:07.029079",
    "url": "https://github.com/oops/mistake"
  },
  {
    "ok": true,
    "code": 200,
    "elapsed": 0.713434,
    "date": "2020-07-02T11:41:07.291180",
    "url": "https://getsitecontrol.com"
  }
]
```

To run service in local (development) mode:
```bash
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up
```

In the development mode:
- Debug is on by default
- Code sources are mounted as volumes
- Additional python libraries are installed (e.g `pytest`, `flake8` and `isort`)
- PostgreSQL creates different database (and one more for unit tests)
- Dockerfile has more user-friendly layers in terms of rebuilding

## Tests
There are unit tests written for both backend and worker apps. To run them:
```shell script
# Backend
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml run --rm backend pytest

# Worker
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml run --rm worker pytest
```

Also you can run flake8 & mypy checks as:
```shell script
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml run --rm <service> invoke check
```

Or both linters and tests:
```shell script
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml run --rm <service> invoke test
```


## TO-DOs
(Or better to say ways of improvements which intentionally were omitted cause
it's a test task, not a prod-ready app)

- Move some duplicated code into a shared python library
- Add migrations
- Set up CI
- Fix elapsed time, cause now it includes time for switching context
