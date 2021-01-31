.PHONY: tests
tests:
	python -m unittest discover tests

.PHONY: coverage
coverage:
	coverage run -m unittest discover tests && coverage html
