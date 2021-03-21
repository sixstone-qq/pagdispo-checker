MODULES := pagdispo

help: # show info about targets
	@grep '^[^#[:space:]].*:' $(MAKEFILE_LIST)

start-dev:
	[ -d venv ] || python -m venv venv
	venv/bin/pip install --upgrade -r requirements.txt -r requirements-test.txt
	venv/bin/python setup.py develop

test:
	@venv/bin/pytest -vv --cov=pagdispo

lint:
	venv/bin/flake8 $(MODULES)
	venv/bin/mypy $(MODULES) || exit 0 # Just informative by now

