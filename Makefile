.PHONY: install data plot plot-custom test clean

# Install dependencies & fetch data
install:
	./startup.sh lagged_oil_unrate

# Download FRED data (if needed)
data:
	./startup.sh refresh_data

# Default 18-month lag plot
plot:
	./startup.sh lagged_oil_unrate

# Custom plot of arbitrary series
# Usage: make plot-custom ARGS="--series UNRATE CPIAUCSL --start 2000-01-01"
plot-custom:
	./startup.sh custom_chart $(ARGS)

# Run tests
test:
	./startup.sh pytest -q

# Clean up any outputs (no venv to delete)
clean:
	rm -rf outputs
