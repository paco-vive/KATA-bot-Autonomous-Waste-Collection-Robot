# Convenience targets. Run from the repository root.
.PHONY: test test-python test-firmware install

test: test-python test-firmware

test-python:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q

test-firmware:
	$(MAKE) -C firmware/test

install:
	python3 -m pip install -e ".[dev]"
