.PHONY: flake8 test coverage

flake8:
	flake8 selenium_panel tests

test:
	python ./tests/manage.py test $${TEST_ARGS:-tests}
	
coverage:
	python --version
	coverage erase
	coverage run ./tests/manage.py test -v2 $${TEST_ARGS:-tests}
	coverage report
	coverage html
