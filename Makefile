LOCALPATH = $(CURDIR)
VIRTUAL_ENV = $(HOME)/.virtualenvs/strats
MANAGE_PY = $(LOCALPATH)/manage.py

SUPERUSER_LOGIN = 'admin'
SUPERUSER_PASSWORD = 'qweqwe'

PYTHON_BIN = venv/bin/
PYTHON = $(PYTHON_BIN)/python
PIP = $(PYTHON_BIN)/pip


initdb:
	$(PYTHON) $(MANAGE_PY) reset_db
	$(PYTHON) $(MANAGE_PY) migrate


create_superuser:
	@echo "from django.contrib.auth.models import User; User.objects.create_superuser($(SUPERUSER_LOGIN), 'admin@example.com', $(SUPERUSER_PASSWORD))" | $(PYTHON) manage.py shell
	@echo "Superuser \"admin\" created"


resetdb: initdb create_superuser


runserver:
	$(PYTHON) $(MANAGE_PY) runserver


schemamigrations:
	$(PYTHON) $(MANAGE_PY) makemigrations


migrate:
	$(PYTHON) $(MANAGE_PY) migrate


shell:
	$(PYTHON) $(MANAGE_PY) shell_plus


import_activities:
	@$(PYTHON) $(MANAGE_PY) import_activities --limit=$(limit) --fast=$(fast)


recreatevenv:
	rm -rf venv && \
	python3 -m venv venv && \
	$(PIP) install --upgrade pip && \
	$(PIP) install -r requirements.txt

updatevenv:
	$(PIP) install -r requirements.txt

shell:
	${PYTHON} manage.py shell_plus
