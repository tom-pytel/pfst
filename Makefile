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


.PHONY: docs
docs:  ## Compile documentation
	python make_docs.py fst.fst fst.fstview fst.shared fst.astutil
	# pdoc -o docs -d markdown fst.fst fst.fstview fst.shared fst.astutil


.PHONY: all-docs
all-docs:  ## Compile all documentation, including private functions, for dev
	python make_docs.py --private fst.fst fst.fstview fst.shared fst.astutil fst.fst_parse fst.fst_raw fst.fst_slice_old fst.fst_slice fst.fst_one fst.fst_reconcile fst.fst_walk fst.fst_misc fst.srcedit


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
