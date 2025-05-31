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

# Custom plot of arbitrary series
# Usage: make plot-custom ARGS="--series UNRATE CPIAUCSL --start 2000-01-01"
plot-custom:
        ./startup.sh python scripts/custom_chart.py $(ARGS)

# Run tests
test:
	./startup.sh pytest -q

# Clean up any outputs (no venv to delete)
clean:
	rm -rf outputs
