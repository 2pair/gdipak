.PHONY: test
test:
	coverage run
	coverage html

.PHONY: lint
lint:
	black gdipak tests
	flake8
	bandit -b ".bandit_baseline" -r *.py gdipak
	pylint gdipak/*.py tests/*.py
