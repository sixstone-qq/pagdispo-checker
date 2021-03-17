.PHONY: clean test help
APPS := checker recorder

help: # show info about targets
	@grep '^[^#[:space:]].*:' $(MAKEFILE_LIST)

checker-venv: # Creates the venv for pagdispo-checker
	$(MAKE) -C checker start-dev

recorder-venv: # Creates the venv for pagdispo-recorder
	$(MAKE) -C $(@:-venv=) start-dev

db-dev: # Create DB and migrate schemas
	docker exec pagdispo_postgres_1 createdb -U postgres -h localhost monitor_check 2> /dev/null || exit 0
	cd recorder && ./venv/bin/migrate-db

# This aim to run a set of containers with the dependencies + setting up the virtualenv to develop
start-dev:
	docker-compose -f docker-compose-dev.yaml up --detach
	$(MAKE) -j2 checker-venv recorder-venv
	$(MAKE) db-dev

stop-dev:
	docker-compose -f docker-compose-dev.yaml down

clean:
	rm -rf checker/venv recorder/venv
	$(MAKE) stop-dev

test:
	$(MAKE) -C checker test
	$(MAKE) -C recorder test

lint:
	$(MAKE) -C checker lint
	$(MAKE) -C recorder lint
