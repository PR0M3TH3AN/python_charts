# Makefile for python_charts
# Defines standard targets for Codex/CI to use startup.sh

.PHONY: install data plot test clean

# Install dependencies into venv and prepare data
install:
	./startup.sh pip install

# Download FRED data (if needed)
data:
	./startup.sh scripts/refresh_data.py

# Generate the default chart (18-month lag)
plot:
	./startup.sh

# Generate a custom chart	
# Usage: make plot ARGS="--offset 12 --end 2025-05-31 --extend-years 5"
plot-custom:
	./startup.sh $(ARGS)

# Run test suite
test:
	./startup.sh pytest -q

# Remove virtual environment and outputs
clean:
	rm -rf venv data outputs
