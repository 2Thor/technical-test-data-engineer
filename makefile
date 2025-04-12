
test: venv
	.venv/bin/pytest -v

run_pipeline: venv
	PYTHONPATH=. .venv/bin/python src/data_pipeline/main.py

run_api: venv
	cd src/moovitamix_fastapi && ../../.venv/bin/python -m uvicorn main:app
	
venv: .venv/bin/activate

.venv/bin/activate: requirements.txt
	python3 -m venv .venv
	source .venv/bin/activate && pip install -Ur requirements.txt



