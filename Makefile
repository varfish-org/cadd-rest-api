SHELL = /bin/bash
MANAGE = time python manage.py

.PHONY: black serve _migrate migrate celery

black:
	black -l 100 --exclude '/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.?v?env|_build|buck-out|build|dist|src)/' .

serve:
	$(MANAGE) runserver

_migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

migrate: _migrate black

celery:
	celery worker -A config.celery_app -l info --concurrency=4

test:
	$(MANAGE) test --settings=config.settings.test -v2

