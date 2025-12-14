#!/bin/bash

echo "Применение миграции для добавления поля модели ККТ..."
sudo -u postgres psql -d kkt_production -f /tmp/add_cash_register_model.sql

echo "Миграция завершена!"
