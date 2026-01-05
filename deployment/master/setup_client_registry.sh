#!/bin/bash
# Setup Client Registry Database

set -e

echo "=========================================="
echo "Client Registry Database Setup"
echo "=========================================="

DB_NAME="kkt_master_registry"
DB_USER="kkt_user"
SCHEMA_FILE="client_registry_schema.sql"

if [[ $EUID -ne 0 ]]; then
   echo "Требуются права root/sudo"
   exit 1
fi

echo "Создание базы данных..."
sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

echo "Применение схемы..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sudo -u postgres psql -d $DB_NAME -f "$SCRIPT_DIR/$SCHEMA_FILE"

echo "Проверка..."
sudo -u postgres psql -d $DB_NAME -c "SELECT email, role FROM admin_users;"

echo "✅ Готово! БД: $DB_NAME"
