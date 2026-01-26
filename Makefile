.PHONY: regenerate-client clean-client regenerate-models help

help:
	@echo "Available targets:"
	@echo ""
	@echo "Models Only (datamodel-code-generator):"
	@echo "  regenerate-models       - Generate Pydantic models only (1 file, clean names)"
	@echo "                            → Creates: src/cinder/generated/models.py"
	@echo "                            → Includes: Just Pydantic models"
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
