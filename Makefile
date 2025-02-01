VERSION ?= $(shell cat VERSION)


.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: install
install:  ## Install locally from current directory
	pip install -e .


.PHONY: test
test:  ## Run basic unit tests
	python -m unittest discover --verbose -s tests


.PHONY: clean
clean:  ## Delete all generated files and directories
	rm -rf src/f_ast.egg-info/
	find . -name __pycache__ -type d -exec rm -rf {} +
