#!/bin/bash
# Fix test environment redirects

cd /home/kktapp/kkt-test-system/web/app/static/js

# Fix auth.js redirects
sed -i "s|'/static/|'/test/static/|g" auth.js
sed -i "s|'/api/|'/test/api/|g" auth.js

# Fix other JS files
sed -i "s|'/static/|'/test/static/|g" database-management.js
sed -i "s|'/static/|'/test/static/|g" users-management.js

# Fix API base URL if exists
sed -i "s|const API_BASE = '/api'|const API_BASE = '/test/api'|g" *.js

echo "Test environment paths fixed"
