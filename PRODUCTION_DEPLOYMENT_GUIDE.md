# Руководство по развертыванию проекта KKT на VDS

## ✅ Завершённые этапы (Phase 1)

### Pre-Migration Preparation - COMPLETE

- ✅ Создан бэкап базы данных: `backups/kkt_backup_20251213_234012.zip`
- ✅ Создан Git коммит с текущим состоянием
- ✅ Удалены все тестовые файлы (27 файлов)
- ✅ Удалены все batch скрипты (8 файлов)
- ✅ Удалены утилиты разработки (40 файлов)
- ✅ Удалена временная документация (22 файла)
- ✅ Удалены неиспользуемые папки (frontend, logs, scheduler)
- ✅ Код отправлен в GitHub

**Всего удалено:** 100 файлов  
**Репозиторий:** https://github.com/zhurbarv-hub/Qoders.git

---

## 📋 Следующие этапы миграции

### Phase 2: VDS Environment Setup (4-6 часов)

**Задачи на VDS сервере (Ubuntu 22.04):**

1. **Первоначальная настройка безопасности:**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Создание пользователя приложения
sudo adduser kktapp
sudo usermod -aG sudo kktapp

# Настройка SSH ключа
mkdir -p /home/kktapp/.ssh
# Скопируйте ваш публичный ключ в /home/kktapp/.ssh/authorized_keys

# Настройка firewall
sudo ufw allow 22/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

2. **Установка необходимых пакетов:**
```bash
# Системные утилиты
sudo apt install -y build-essential git curl wget unzip htop net-tools

# Python
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib libpq-dev

# Nginx и SSL
sudo apt install -y nginx
sudo apt install -y certbot python3-certbot-nginx
```

3. **Настройка PostgreSQL:**
```bash
# Переключение на пользователя postgres
sudo -u postgres psql

# В psql консоли:
CREATE DATABASE kkt_production;
CREATE USER kkt_user WITH PASSWORD 'СИЛЬНЫЙ_ПАРОЛЬ';
GRANT ALL PRIVILEGES ON DATABASE kkt_production TO kkt_user;
\q
```

4. **Клонирование репозитория:**
```bash
# Переключение на пользователя kktapp
su - kktapp

# Клонирование проекта
cd /home/kktapp
git clone https://github.com/zhurbarv-hub/Qoders.git kkt-system
cd kkt-system
```

---

### Phase 3: Database Migration (SQLite → PostgreSQL) (4-6 часов)

1. **Экспорт данных из SQLite (на локальной машине):**
```bash
# Экспорт в SQL дамп
sqlite3 database/kkt_services.db .dump > kkt_sqlite_dump.sql

# Скопировать на VDS
scp kkt_sqlite_dump.sql kktapp@YOUR_VDS_IP:/home/kktapp/
```

2. **Адаптация схемы для PostgreSQL:**
   - Файл схемы: `database/schema_kkt.sql`
   - Необходимые изменения:
     - `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY`
     - `BOOLEAN DEFAULT 1` → `BOOLEAN DEFAULT TRUE`
     - Функции дат: `julianday()` → использовать PostgreSQL date arithmetic

3. **Создание схемы и импорт данных (на VDS):**
```bash
# Создание таблиц
psql -U kkt_user -d kkt_production -f database/schema_kkt_postgres.sql

# Импорт данных (после адаптации дампа)
psql -U kkt_user -d kkt_production -f kkt_sqlite_dump_adapted.sql
```

4. **Обновление конфигурации:**
   - Создать `.env` файл с PostgreSQL connection string:
```env
DATABASE_URL=postgresql://kkt_user:СИЛЬНЫЙ_ПАРОЛЬ@localhost:5432/kkt_production
```

---

### Phase 4: Application Deployment (6-8 часов)

1. **Создание виртуального окружения:**
```bash
cd /home/kktapp/kkt-system

# Создание venv
python3.11 -m venv venv

# Активация
source venv/bin/activate

# Обновление pip
pip install --upgrade pip

# Установка зависимостей + psycopg2
pip install -r requirements.txt
pip install -r requirements-web.txt
pip install psycopg2-binary
```

2. **Конфигурация .env файла:**
```bash
# Скопировать пример
cp .env.example .env

# Редактировать (nano или vim)
nano .env
```

Обязательные переменные:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - сгенерировать сильный ключ
- `TELEGRAM_BOT_TOKEN` - токен бота
- `TELEGRAM_ADMIN_IDS` - ID администраторов
- `WEB_API_BASE_URL=http://localhost:8000`
- `API_RELOAD=False`

3. **Создание директорий:**
```bash
sudo mkdir -p /var/log/kkt-system
sudo chown kktapp:kktapp /var/log/kkt-system
```

4. **Тестовый запуск:**
```bash
# Активировать venv
source venv/bin/activate

# Запустить веб-приложение
cd /home/kktapp/kkt-system
python -m uvicorn web.app.main:app --host 127.0.0.1 --port 8000

# В другом терминале - запустить бота
python bot/main.py
```

---

### Phase 5: Infrastructure Services (4-6 часов)

1. **Создание systemd сервиса для веб-приложения:**

Файл: `/etc/systemd/system/kkt-web.service`
```ini
[Unit]
Description=KKT Web Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=kktapp
WorkingDirectory=/home/kktapp/kkt-system
Environment="PATH=/home/kktapp/kkt-system/venv/bin"
EnvironmentFile=/home/kktapp/kkt-system/.env
ExecStart=/home/kktapp/kkt-system/venv/bin/uvicorn web.app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Создание systemd сервиса для Telegram бота:**

Файл: `/etc/systemd/system/kkt-bot.service`
```ini
[Unit]
Description=KKT Telegram Bot
After=network.target kkt-web.service
Requires=kkt-web.service

[Service]
Type=simple
User=kktapp
WorkingDirectory=/home/kktapp/kkt-system
Environment="PATH=/home/kktapp/kkt-system/venv/bin"
EnvironmentFile=/home/kktapp/kkt-system/.env
ExecStart=/home/kktapp/kkt-system/venv/bin/python bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Активация сервисов:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable kkt-web.service
sudo systemctl enable kkt-bot.service
sudo systemctl start kkt-web.service
sudo systemctl start kkt-bot.service

# Проверка статуса
sudo systemctl status kkt-web.service
sudo systemctl status kkt-bot.service
```

4. **Настройка Nginx:**

Файл: `/etc/nginx/sites-available/kkt-system`
```nginx
upstream kkt_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# HTTP сервер (редирект на HTTPS)
server {
    listen 8080;
    server_name ВАШ_ДОМЕН;
    
    return 301 https://$server_name$request_uri;
}

# HTTPS сервер
server {
    listen 443 ssl http2;
    server_name ВАШ_ДОМЕН;

    # SSL сертификаты (будут добавлены certbot)
    # ssl_certificate /etc/letsencrypt/live/ВАШ_ДОМЕН/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/ВАШ_ДОМЕН/privkey.pem;

    # Статические файлы
    location /static/ {
        alias /home/kktapp/kkt-system/web/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API и динамический контент
    location / {
        proxy_pass http://kkt_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
```

5. **Активация Nginx конфигурации:**
```bash
sudo ln -s /etc/nginx/sites-available/kkt-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

6. **Настройка SSL с Let's Encrypt:**
```bash
sudo certbot --nginx -d ВАШ_ДОМЕН
```

---

### Phase 6: Testing & Validation (4-8 часов)

1. **Health checks:**
```bash
# Проверка веб-приложения
curl http://localhost:8000/health

# Проверка через Nginx (HTTPS)
curl https://ВАШ_ДОМЕН/health
```

2. **Функциональное тестирование:**
   - Открыть https://ВАШ_ДОМЕН в браузере
   - Войти с учётными данными
   - Проверить все основные функции
   - Проверить работу Telegram бота (команды /start, /list)

3. **Проверка логов:**
```bash
# Логи веб-приложения
sudo journalctl -u kkt-web.service -f

# Логи бота
sudo journalctl -u kkt-bot.service -f

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

### Phase 7: Production Launch (2-4 часа)

1. **Настройка автоматических бэкапов:**

Файл: `/home/kktapp/backup-db.sh`
```bash
#!/bin/bash
BACKUP_DIR="/home/kktapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U kkt_user kkt_production | gzip > $BACKUP_DIR/kkt_backup_$DATE.sql.gz

# Удалить бэкапы старше 7 дней
find $BACKUP_DIR -name "kkt_backup_*.sql.gz" -mtime +7 -delete
```

Добавить в crontab:
```bash
crontab -e
# Добавить строку (бэкап каждый день в 3:00)
0 3 * * * /home/kktapp/backup-db.sh
```

2. **Мониторинг:**
   - Настроить мониторинг uptime
   - Настроить алерты на ошибки
   - Проверять логи регулярно

---

## 🔐 Важные замечания по безопасности

1. **Пароли и ключи:**
   - JWT_SECRET_KEY: минимум 64 символа, случайный
   - PostgreSQL пароль: сложный, уникальный
   - .env файл: права 600 (только владелец может читать)

2. **Firewall:**
   - Открыты только порты 22, 8080, 443
   - PostgreSQL (5432) доступен только локально
   - Web app (8000) доступен только локально

3. **Обновления:**
   - Регулярно обновлять систему: `sudo apt update && sudo apt upgrade`
   - Обновлять Python пакеты: `pip install --upgrade -r requirements.txt`

---

## 📊 Полезные команды

### Управление сервисами:
```bash
# Перезапуск веб-приложения
sudo systemctl restart kkt-web.service

# Перезапуск бота
sudo systemctl restart kkt-bot.service

# Просмотр логов
sudo journalctl -u kkt-web.service -n 100
sudo journalctl -u kkt-bot.service -n 100

# Статус всех сервисов
sudo systemctl status kkt-*
```

### PostgreSQL:
```bash
# Подключение к базе
psql -U kkt_user -d kkt_production

# Бэкап вручную
pg_dump -U kkt_user kkt_production > backup.sql

# Восстановление
psql -U kkt_user -d kkt_production < backup.sql
```

### Nginx:
```bash
# Проверка конфигурации
sudo nginx -t

# Перезагрузка конфигурации
sudo systemctl reload nginx

# Просмотр логов ошибок
sudo tail -f /var/log/nginx/error.log
```

---

## 📞 Поддержка

В случае проблем:
1. Проверьте логи сервисов
2. Проверьте статус systemd служб
3. Проверьте подключение к базе данных
4. Проверьте права доступа к файлам

---

## ✅ Чеклист финальной проверки

- [ ] PostgreSQL запущен и доступен
- [ ] Веб-приложение запущено (systemd)
- [ ] Telegram бот запущен (systemd)
- [ ] Nginx настроен и работает
- [ ] SSL сертификат установлен
- [ ] Firewall настроен корректно
- [ ] Статические файлы доступны
- [ ] API endpoints отвечают
- [ ] Авторизация работает
- [ ] Telegram бот отвечает на команды
- [ ] Автоматические бэкапы настроены
- [ ] Логирование работает
- [ ] Все сервисы автостартуют после перезагрузки

---

**Дата подготовки:** 2025-12-13  
**Версия проекта:** Production-ready  
**Целевая платформа:** Ubuntu 22.04 LTS + PostgreSQL 14+  
**Документ создан автоматически на основе:** `.qoder/quests/project-migration.md`
