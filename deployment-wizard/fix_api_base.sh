#!/bin/bash
# Fix API base URL for test environment

cd /home/kktapp/kkt-test-system/web/app/static/js

# Fix API_BASE_URL to include /test prefix
sed -i "s|const API_BASE_URL = window.location.origin + '/api';|const API_BASE_URL = window.location.origin + '/test/api';|g" auth.js

# Verify
echo "Checking auth.js API_BASE_URL:"
grep "API_BASE_URL" auth.js

echo "Done"
