all:
	pipenv run ./tgif.py

gif:
	pipenv run ./tgif.py --duration 100 --gif 50
