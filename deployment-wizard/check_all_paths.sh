#!/bin/bash

echo "=== Checking all window.location references ==="
find /home/kktapp/kkt-test-system/web/app/static/js -name '*.js' -exec grep -H 'window.location' {} \;

echo ""
echo "=== Checking all API_BASE_URL definitions ==="
find /home/kktapp/kkt-test-system/web/app/static/js -name '*.js' -exec grep -H 'API_BASE_URL' {} \;

echo ""
echo "=== Checking all hardcoded /api paths ==="
find /home/kktapp/kkt-test-system/web/app/static/js -name '*.js' -exec grep -H "'/api" {} \;

echo ""
echo "=== Checking all hardcoded /static paths ==="
find /home/kktapp/kkt-test-system/web/app/static/js -name '*.js' -exec grep -H "'/static" {} \;

echo ""
echo "=== Checking fetch and axios calls ==="
find /home/kktapp/kkt-test-system/web/app/static/js -name '*.js' -exec grep -H 'fetch\|axios' {} \;
