VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: venv install run clean

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

run: install
	$(PYTHON) main.py https://browser.engineering/examples/xiyouji.html

clean:
	rm -rf $(VENV)
