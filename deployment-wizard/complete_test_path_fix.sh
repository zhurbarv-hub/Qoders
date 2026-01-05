#!/bin/bash

# Complete fix for test environment path isolation
# This script fixes ALL path issues causing redirects to production

TEST_JS_DIR="/home/kktapp/kkt-test-system/web/app/static/js"

echo "=== Fixing Test Environment Path Issues ==="
cd "$TEST_JS_DIR"

# Backup all JS files first
echo "Creating backups..."
for file in *.js; do
    cp "$file" "$file.backup_$(date +%Y%m%d_%H%M%S)"
done

echo ""
echo "=== Fix 1: API_BASE_URL with window.location.origin ==="
# Find and fix all instances of API_BASE_URL that use window.location.origin without /test
find . -name "*.js" -type f -exec sed -i "s|const API_BASE_URL = window.location.origin + '/api'|const API_BASE_URL = window.location.origin + '/test/api'|g" {} \;
find . -name "*.js" -type f -exec sed -i 's|const API_BASE_URL = window\.location\.origin + "/api"|const API_BASE_URL = window.location.origin + "/test/api"|g' {} \;

echo "Fix 1 applied"

echo ""
echo "=== Fix 2: window.location.href redirects ==="
# Fix direct window.location.href assignments that don't include /test
sed -i "s|window.location.href = '/dashboard'|window.location.href = '/test/dashboard'|g" *.js
sed -i "s|window.location.href = '/login'|window.location.href = '/test/login'|g" *.js
sed -i "s|window.location.href = '/'|window.location.href = '/test/'|g" *.js
sed -i 's|window\.location\.href = "/dashboard"|window.location.href = "/test/dashboard"|g' *.js
sed -i 's|window\.location\.href = "/login"|window.location.href = "/test/login"|g' *.js
sed -i 's|window\.location\.href = "/"|window.location.href = "/test/"|g' *.js

echo "Fix 2 applied"

echo ""
echo "=== Fix 3: Static file paths ==="
# Fix any remaining static paths
sed -i "s|'/static/|'/test/static/|g" *.js
sed -i 's|"/static/|"/test/static/|g' *.js

echo "Fix 3 applied"

echo ""
echo "=== Fix 4: API paths in fetch calls ==="
# Fix hardcoded API paths
sed -i "s|fetch('/api/|fetch('/test/api/|g" *.js
sed -i 's|fetch("/api/|fetch("/test/api/|g' *.js
sed -i "s|axios.get('/api/|axios.get('/test/api/|g" *.js
sed -i "s|axios.post('/api/|axios.post('/test/api/|g" *.js
sed -i 's|axios.get("/api/|axios.get("/test/api/|g' *.js
sed -i 's|axios.post("/api/|axios.post("/test/api/|g' *.js

echo "Fix 4 applied"

echo ""
echo "=== Fix 5: History API navigation ==="
# Fix history.pushState and replaceState
sed -i "s|history.pushState({}, '', '/dashboard')|history.pushState({}, '', '/test/dashboard')|g" *.js
sed -i "s|history.pushState({}, '', '/')|history.pushState({}, '', '/test/')|g" *.js

echo "Fix 5 applied"

echo ""
echo "=== Verification: Checking for remaining issues ==="
echo ""
echo "--- Any window.location.origin + '/api' without /test: ---"
grep -n "window.location.origin + '/api'" *.js || echo "None found - Good!"
echo ""
echo "--- Any window.location.href = '/' without /test: ---"
grep -n "window.location.href = '/'" *.js | grep -v '/test/' || echo "None found - Good!"
echo ""
echo "--- Any fetch('/api/ without /test: ---"
grep -n "fetch('/api/" *.js | grep -v '/test/' || echo "None found - Good!"
echo ""

echo "=== Summary of all API base patterns found: ==="
grep -n "API_BASE" *.js | sort -u

echo ""
echo "=== All window.location patterns: ==="
grep -n "window.location" *.js | sort -u

echo ""
echo "=== Fix complete! Please test login at https://kkt-box.net/test/ ==="
