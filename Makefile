all: Pipfile.lock
	pipenv run ./tgif.py

gif: Pipfile.lock
	pipenv run ./tgif.py --duration 100 --gif 50

Pipfile.lock:
	pipenv install
