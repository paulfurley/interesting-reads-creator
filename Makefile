.PHONY: run
run: venv/bin/activate
	. venv/bin/activate ; \
	python run.py

venv/bin/activate:
	virtualenv -p /usr/bin/python3 venv
	. venv/bin/activate ; \
	pip install -r requirements.txt
