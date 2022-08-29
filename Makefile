.PHONY: test
test:
	coverage run
	coverage html

.PHONY: lint
lint:
	black gdipak tests
	flake8 gdipak tests
	bandit -b ".bandit_baseline" -r *.py gdipak
	pylint gdipak tests
