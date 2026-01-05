#!/bin/bash
cd /home/kktapp/kkt-test-system/web/app/static/js
echo '=== All window.location references ==='
grep -n 'window.location' *.js
echo ''
echo '=== All API_BASE_URL ==='
grep -n 'API_BASE_URL' *.js
echo ''
echo '=== All /api paths ==='
grep -n "'/api" *.js
