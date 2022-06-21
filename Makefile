.PHONY: test
test:
	coverage run
	coverage html

.PHONY: lint
lint:
	black .
	flake8
	pylint gdipak/*.py
	bandit -b -bandit_baseline -r *.py .