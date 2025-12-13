#!/bin/bash
# ============================================
# Backup Automation Setup
# Скрипт для настройки автоматических бэкапов
# ============================================

set -e

echo "=================================================="
echo "Backup Automation Setup"
echo "=================================================="

APP_USER="kktapp"
BACKUP_DIR="/home/$APP_USER/backups"
DB_NAME="kkt_production"
DB_USER="kkt_user"

# ============================================
# 1. Создание скрипта бэкапа
# ============================================
echo ""
echo ">>> Шаг 1/3: Создание скрипта бэкапа..."

cat > /home/$APP_USER/backup-database.sh <<'EOF'
#!/bin/bash
# Автоматический бэкап PostgreSQL базы данных

BACKUP_DIR="/home/kktapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="kkt_production"
DB_USER="kkt_user"

# Создание директории
mkdir -p $BACKUP_DIR

# Создание бэкапа
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/kkt_backup_$DATE.sql.gz

# Проверка успешности
if [ $? -eq 0 ]; then
    echo "✓ Бэкап создан: $BACKUP_DIR/kkt_backup_$DATE.sql.gz"
    
    # Размер файла
    du -h $BACKUP_DIR/kkt_backup_$DATE.sql.gz
    
    # Удаление старых бэкапов (старше 7 дней)
    find $BACKUP_DIR -name "kkt_backup_*.sql.gz" -mtime +7 -delete
    echo "✓ Старые бэкапы удалены (>7 дней)"
else
    echo "✗ Ошибка создания бэкапа" >&2
    exit 1
fi
EOF

# Установка прав
chmod +x /home/$APP_USER/backup-database.sh
chown $APP_USER:$APP_USER /home/$APP_USER/backup-database.sh

echo "✓ Скрипт бэкапа создан: /home/$APP_USER/backup-database.sh"

# ============================================
# 2. Настройка cron задачи
# ============================================
echo ""
echo ">>> Шаг 2/3: Настройка cron задачи..."

# Создание cron задачи для пользователя kktapp
sudo -u $APP_USER bash <<'EOF'
# Добавление задачи в crontab (если её ещё нет)
(crontab -l 2>/dev/null | grep -v "backup-database.sh"; echo "0 3 * * * /home/kktapp/backup-database.sh >> /var/log/kkt-system/backup.log 2>&1") | crontab -
EOF

echo "✓ Cron задача создана (ежедневно в 3:00)"

# Показать текущие задачи
echo ""
echo "Текущие cron задачи для $APP_USER:"
sudo -u $APP_USER crontab -l

# ============================================
# 3. Тестовый запуск бэкапа
# ============================================
echo ""
echo ">>> Шаг 3/3: Тестовый запуск бэкапа..."

sudo -u $APP_USER /home/$APP_USER/backup-database.sh

echo "✓ Тестовый бэкап выполнен успешно"

# Показать список бэкапов
echo ""
echo "Существующие бэкапы:"
ls -lh $BACKUP_DIR/kkt_backup_*.sql.gz 2>/dev/null || echo "  (пока нет бэкапов)"

# ============================================
# Итоговая информация
# ============================================
echo ""
echo "=================================================="
echo "✅ Backup Automation - COMPLETE"
echo "=================================================="
echo ""
echo "Настройки бэкапа:"
echo "  Скрипт: /home/$APP_USER/backup-database.sh"
echo "  Директория: $BACKUP_DIR"
echo "  Расписание: Ежедневно в 3:00 AM"
echo "  Хранение: 7 дней"
echo "  Логи: /var/log/kkt-system/backup.log"
echo ""
echo "Ручной запуск бэкапа:"
echo "  sudo -u $APP_USER /home/$APP_USER/backup-database.sh"
echo ""
echo "Восстановление из бэкапа:"
echo "  gunzip < backup_file.sql.gz | psql -U $DB_USER -d $DB_NAME"
echo "=================================================="
