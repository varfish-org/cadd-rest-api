SHELL = /bin/bash
MANAGE = time python manage.py

.PHONY: black
black:
	black -l 100 --exclude '/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.?v?env|_build|buck-out|build|dist|src)/' .

.PHONY: isort
isort:
	isort --force-sort-within-sections --profile=black .

.PHONY: flake8
flake8:
	flake8

.PHONY: serve
serve:
	$(MANAGE) runserver

.PHONY: _migrate
_migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

.PHONY: migrate
migrate: _migrate black

.PHONY: celery
celery:
	celery worker -A config.celery_app -l info --concurrency=4

.PHONY: test
test:
	$(MANAGE) test --settings=config.settings.test -v2

