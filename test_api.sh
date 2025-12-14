#!/bin/bash

# Get auth token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "=== Token obtained: ${TOKEN:0:30}..."
echo ""

# Test deadlines endpoint
echo "=== Testing /api/deadlines ===" 
curl -s "http://localhost:8000/api/deadlines?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# Test clients endpoint
echo "=== Testing /api/clients ==="
curl -s "http://localhost:8000/api/clients?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Done ==="
