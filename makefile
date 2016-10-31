venv:
	virtualenv --no-site-packages venv

init: venv
	source venv/bin/activate; \
	pip install -r requirements.txt

test:
	py.test tests

.PHONY: init test
