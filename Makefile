VERSION ?= $(shell cat VERSION)
PYPI_REPO ?= https://test.pypi.org/

check-tag = !(git rev-parse -q --verify "refs/tags/v${VERSION}" > /dev/null 2>&1) || \
	(echo "the version: ${VERSION} has been released already" && exit 1)


.PHONY: help
help:  ## Get help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: install
install:  ## Install locally from current directory
	pip install -e ."[dev]"


.PHONY: test
test:  ## Run basic unit tests
	python -m unittest discover --verbose tests
	# pytest -vv tests


.PHONY: coverage
coverage:  ## Run basic unit tests
	pytest -v --cov=fst --cov-report=html tests


.PHONY: lint
lint:  ## Lint stuff
	ruff check --output-format=concise


.PHONY: regen-tests
regen-tests:  ## Regenerate test data
	python tests/test_fst.py --regen-all
	python tests/test_parse.py --regen-all
	python tests/test_fst_one.py --regen-all
	python tests/test_fst_slice.py --regen-all
	python tests/test_match.py --regen-all


.PHONY: docs
docs:  ## Compile documentation
	python make_docs.py


.PHONY: clean
clean:  ## Delete all generated files and directories
	rm -rf build/ dist/ src/pfst.egg-info/
	find . -name __pycache__ -type d -exec rm -rf {} +


.PHONY: check-version
check-version:  ## Check if VERSION has already been released/tagged
	@$(check-tag)


.PHONY: publish
publish:  ## Tag git commit with VERSION and push
	@$(check-tag)
	git tag v${VERSION}
	git push origin v${VERSION}


.PHONY: build-wheel
build-wheel:  ## Build python wheel
	python -m build --wheel


.PHONY: publish-wheel
publish-wheel:  ## Publish python wheel
	TWINE_USERNAME=${PYPI_USERNAME} TWINE_PASSWORD=${PYPI_API_KEY} twine upload --repository-url ${PYPI_REPO} dist/*
