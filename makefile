venv:
	virtualenv --no-site-packages venv

init: venv
	source venv/bin/activate; \
	pip install -r requirements.txt; \
	pip install https://storage.googleapis.com/tensorflow/mac/gpu/tensorflow-0.11.0rc1-py3-none-any.whl

test:
	py.test tests

.PHONY: init test
