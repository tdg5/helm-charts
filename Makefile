.PHONY: docs
docs:
	@scripts/helm-docs.sh

.PHONY: quality
quality:
	@echo "Running helm lint on charts..."
	@scripts/lint-charts.sh

.PHONY: style
style:
	@pre-commit run --all-files -c .pre-commit-config.yaml

.PHONY: test
test:
	@pytest
