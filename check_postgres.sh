#!/bin/bash
# Получить параметры подключения postgres

echo "=== ПРОВЕРКА POSTGRES ==="

# Проверка peer authentication (без пароля через sudo)
echo "1. Проверка доступа через peer auth..."
sudo -u postgres psql -c "SELECT current_user, inet_server_addr(), inet_server_port();" 2>&1 | head -5

echo ""
echo "2. Проверка наличия пароля для postgres..."
sudo -u postgres psql -c "\du postgres" 2>&1 | grep postgres

echo ""
echo "=== РЕКОМЕНДАЦИЯ ==="
echo "Для восстановления БД используем одну из стратегий:"
echo "  A) Использовать sudo -u postgres (peer auth, без пароля)"
echo "  B) Установить пароль для postgres и использовать его"
echo ""
echo "Текущая конфигурация позволяет использовать вариант A"
