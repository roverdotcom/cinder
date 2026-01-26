.PHONY: regenerate-client clean-client regenerate-models test test-verbose test-coverage test-watch requirements help

help:
	@echo "Available targets:"
	@echo ""
	@echo "Models Only (datamodel-code-generator):"
	@echo "  regenerate-models       - Generate Pydantic models only (1 file, clean names)"
	@echo "                            → Creates: src/cinder/generated/models.py"
	@echo "                            → Includes: Just Pydantic models"
	@echo ""
	@echo "Testing:"
	@echo "  test                    - Run all tests"
	@echo "  test-verbose            - Run tests with verbose output"
	@echo "  test-coverage           - Run tests with coverage report"
	@echo "  test-watch              - Run tests in watch mode (re-run on file changes)"
	@echo ""
	@echo "Dependencies:"
	@echo "  requirements            - Generate requirements.txt from uv.lock"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean-models            - Remove all generated code"
	@echo ""

regenerate-models:
	@echo "Regenerating Pydantic models from openapi.json..."
	@echo "→ Using datamodel-code-generator (single file with clean names)"
	rm -rf src/cinder/generated
	mkdir -p src/cinder/generated
	uv run datamodel-codegen \
		--input openapi.json \
		--output src/cinder/generated/models.py \
		--output-model-type pydantic_v2.BaseModel \
		--input-file-type openapi
	@echo "✓ Models regenerated successfully!"
	@echo "  Generated: src/cinder/generated/models.py (single file)"

clean-models:
	@echo "Removing generated code..."
	rm -rf src/cinder/generated
	@echo "✓ Generated code removed!"

test:
	@echo "Running tests..."
	uv run pytest
	@echo "✓ Tests completed!"

test-verbose:
	@echo "Running tests with verbose output..."
	uv run pytest -v

test-coverage:
	@echo "Running tests with coverage report..."
	uv run pytest --cov=cinder --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "✓ Coverage report generated!"
	@echo "  View HTML report: open htmlcov/index.html"

test-watch:
	@echo "Running tests in watch mode..."
	@echo "Press Ctrl+C to stop"
	uv run pytest-watch

requirements:
	@echo "Generating requirements.txt from uv.lock..."
	uv export --format requirements-txt --no-dev > requirements.txt
	@echo "✓ requirements.txt generated!"
	@echo ""
	@echo "To include dev dependencies, run:"
	@echo "  uv export --format requirements-txt > requirements-dev.txt"
