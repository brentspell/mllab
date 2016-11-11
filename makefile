UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	TFURI = https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.11.0-cp35-cp35m-linux_x86_64.whl
endif
ifeq ($(UNAME_S),Darwin)
	TFURI = https://storage.googleapis.com/tensorflow/mac/gpu/tensorflow-0.11.0rc1-py3-none-any.whl
endif

venv:
	virtualenv --no-site-packages venv

init: venv
	source venv/bin/activate; \
	pip install -r requirements.txt; \
	pip install $(TFURI)

test:
	py.test tests

.PHONY: init test
