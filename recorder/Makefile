help: # show info about targets
	@grep '^[^#[:space:]].*:' $(MAKEFILE_LIST)

start-dev:
	[ -d venv ] || python -m venv venv
	venv/bin/pip install --upgrade -r requirements.txt -r requirements-test.txt
	venv/bin/python setup.py develop
