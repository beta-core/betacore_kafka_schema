namespace:=betacore
package:=kafka/schema

# Documentation web server information
doc_web_port:=8000
doc_web_bind:=127.0.0.1

doc_source:=sphinx
doc_target:=docs

# Coverage web port
coverage_web_port:=8002
coverage_web_bind:=127.0.0.1

color_green:=\e[32m
color_reset:=\e[0m

test_folder:="./test"
test_pattern:="test_*.py"

.PHONY: test build

all: lint scan test coverage doc

help:
	@echo ""
	@echo "Make file to help with delovper operations"
	@echo "--------------------------"
	@echo "make <$(color_green)command$(color_reset)>"
	@echo "--------------------------"
	@echo "$(color_green)lint$(color_reset)      - runs pylint linter to check code quality"
	@echo "$(color_green)scan$(color_reset)      - runs bandit static code scanner"
	@echo "$(color_green)test$(color_reset)      - runs unit test"
	@echo "$(color_green)coverage$(color_reset)  - runs code coverage reprot"
	@echo "$(color_green)coveraged$(color_reset) - runs coverage web server on port $(coverage_web_port)"
	@echo "$(color_green)build$(color_reset)     - runs setup to create a wheel and sdist"
	@echo "$(color_green)doc$(color_reset)       - runs documentation generation"
	@echo "$(color_green)docd$(color_reset)      - runs document web server on port $(doc_web_port)"

test:
	python3 -m unittest discover -v -s $(test_folder) -p $(test_pattern)

coverage:
	python3 -m pytest --cov-report=html:$(doc_target)/coverage --cov=$(namespace)

lint:
	pylint --rcfile=.pylintrc $(namespace)/$(package)

scan:
	python3 -m bandit -r $(namespace)

doc: doc-refresh doc-web

doc-refresh:
	sphinx-apidoc -f -P -o $(doc_source)/source/ $(namespace)

doc-web:
	sphinx-build -M html $(doc_source)/source/ $(doc_source)/dist
	cp -a $(doc_source)/dist/html/. $(doc_target)/

build:
	python3 setup.py sdist bdist_wheel

# Creates a documentation web server on port
docd:
	python3 -m http.server $(doc_web_port) --bind $(doc_web_bind) --directory $(doc_target)/

coveraged:
	python3 -m http.server $(coverage_web_port) --bind $(coverage_web_bind) --directory $(doc_target)/coverage
