#!/bin/bash

# =============================================================================
# SYNAPSE LAUNCHPAD - DATABASE SEEDING SCRIPT
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}==============================================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}==============================================================================${NC}"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is required but not installed"
    exit 1
fi

print_header "SYNAPSE LAUNCHPAD DATABASE SEEDING"

# Install dependencies
print_status "Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if database is running
print_status "Checking database connection..."
if ! python3 -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://postgres:password@localhost:5432/synapse_db').close())" 2>/dev/null; then
    print_warning "Database connection failed. Make sure PostgreSQL is running and accessible."
    print_warning "Expected connection: postgresql://postgres:password@localhost:5432/synapse_db"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if feature store is running
print_status "Checking feature store connection..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_warning "Feature store service not accessible at http://localhost:8000"
    print_warning "Some features may not be populated in the feature store."
fi

# Run the seeding script
print_status "Starting database seeding..."
python3 seed-database.py

print_header "SEEDING COMPLETED SUCCESSFULLY"
print_status "Database has been populated with:"
echo "  • 50 diverse startups across 10 industries"
echo "  • 200 historical partnership outcomes"
echo "  • 5,000 synthetic user engagement events"
echo "  • 25 marketing campaigns"
echo ""
print_status "You can now:"
echo "  • Start the application services"
echo "  • Test partner recommendations"
echo "  • Generate marketing campaigns"
echo "  • View analytics dashboards"