#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to test an endpoint
test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo "Testing: $description"
    
    # Make the request and capture the status code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000$endpoint)
    
    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ Success: $endpoint returned $status_code${NC}"
    else
        echo -e "${RED}✗ Failed: $endpoint returned $status_code (expected $expected_status)${NC}"
    fi
    echo
}

# Test each endpoint
test_endpoint "/" 404 "Root endpoint (should 404)"
test_endpoint "/api/v1/test" 200 "Test endpoint"
test_endpoint "/docs" 200 "Swagger documentation"
test_endpoint "/openapi.json" 200 "OpenAPI schema"

# Test the response content of the test endpoint
echo "Testing response content of /api/v1/test"
response=$(curl -s http://127.0.0.1:8000/api/v1/test)
expected='{"message":"API is working"}'

if [ "$response" == "$expected" ]; then
    echo -e "${GREEN}✓ Success: Test endpoint returned correct response${NC}"
else
    echo -e "${RED}✗ Failed: Test endpoint returned unexpected response: $response${NC}"
fi 