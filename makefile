
test: venv
	.venv/bin/pytest -v

run: venv
	PYTHONPATH=. .venv/bin/python src/data_pipeline/main.py
	
venv: .venv/bin/activate

.venv/bin/activate: requirements.txt
	python3 -m venv .venv
	source .venv/bin/activate && pip install -Ur requirements.txt



