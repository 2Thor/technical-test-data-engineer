
test: venv
	.venv/bin/pytest -v

run_prefect_server: venv
	@echo "Lancement du serveur Prefect"
	source .venv/bin/activate && prefect server start

run_scheduler: venv
	@echo "Lancement du scheduler Prefect"
	PYTHONPATH=. .venv/bin/python src/data_pipeline/main.py

run_pipeline: venv
	@echo "Lancement de la pipeline de données pour testing"
	source .venv/bin/activate && prefect deployment run 'ETL Pipeline - Prefect/daily-etl'

run_api: venv
	cd src/moovitamix_fastapi && ../../.venv/bin/python -m uvicorn main:app
	
venv: .venv/bin/activate

.venv/bin/activate: requirements.txt
	python3 -m venv .venv
	source .venv/bin/activate && pip install -Ur requirements.txt



