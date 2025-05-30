.PHONY: install data plot plot-custom test clean

# Install dependencies & fetch data
install:
	./startup.sh

# Download FRED data (if needed)
data:
	./startup.sh scripts/refresh_data.py

# Default 18-month lag plot
plot:
	./startup.sh

# Custom plot
# Usage: make plot-custom ARGS="--offset 12 --end 2025-05-31 --extend-years 5"
plot-custom:
	./startup.sh $(ARGS)

# Run tests
test:
	./startup.sh pytest -q

# Clean up any outputs (no venv to delete)
clean:
	rm -rf outputs
