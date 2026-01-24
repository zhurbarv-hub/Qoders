# Инструкция по развертыванию KKT системы на VDS

## Параметры сервера

**IP:** 185.185.71.18  
**ОС:** Ubuntu 24.04 LTS  
**Доступ:** root / iDGZJ6ygXN3RlOwX

## Быстрое развертывание (30 минут)

### Шаг 1: Подключение к VDS

Используйте любой SSH клиент (PuTTY, MobaXterm, или встроенный терминал):

```bash
ssh root@185.185.71.18
# Пароль: iDGZJ6ygXN3RlOwX
```

### Шаг 2: Загрузка deployment файлов

На сервере выполните:

```bash
# Создать директорию для deployment
mkdir -p /root/kkt-deployment
cd /root/kkt-deployment

# Скачать deployment скрипт и .env файл с GitHub
wget https://raw.githubusercontent.com/zhurbarv-hub/Qoders/main/deployment/deploy_production.sh
wget https://raw.githubusercontent.com/zhurbarv-hub/Qoders/main/deployment/.env.production -O .env.production

# Сделать скрипт исполняемым
chmod +x deploy_production.sh
```

**Альтернатива:** Загрузите файлы через SFTP:
1. Подключитесь через FileZilla/WinSCP к `185.185.71.18`
2. Загрузите файлы из `d:\QoProj\KKT\deployment\` в `/root/kkt-deployment/`

### Шаг 3: Запуск автоматического развертывания

```bash
cd /root/kkt-deployment
./deploy_production.sh
```

**Время выполнения:** ~20-30 минут

Скрипт автоматически:
- ✅ Обновит систему Ubuntu
- ✅ Установит Python 3.11, PostgreSQL, Nginx
- ✅ Настроит firewall (UFW)
- ✅ Создаст базу данных и пользователя
- ✅ Склонирует репозиторий
- ✅ Установит все зависимости
- ✅ Применит схему БД
- ✅ Создаст systemd сервисы
- ✅ Настроит Nginx
- ✅ Настроит автоматические бэкапы

### Шаг 4: Обновление администратора

После успешного развертывания обновите Telegram ID администратора:

```bash
# Подключитесь к базе данных
su - kktapp
cd kkt-system

# Применить SQL скрипт
PGPASSWORD=ChangeThisStrongPassword123! psql -U kkt_user -d kkt_production -h localhost -f deployment/update_admin.sql
```

**Ожидаемый вывод:**
```
     status                |       email        | telegram_id  
---------------------------+--------------------+-------------
 Администратор обновлен    | admin@kkt-system.ru| 5064340711
```

### Шаг 5: Проверка работоспособности

#### Проверка сервисов:

```bash
sudo systemctl status kkt-web
sudo systemctl status kkt-bot
```

Оба должны быть: `active (running)`

#### Проверка веб-доступа:

```bash
curl http://localhost:8000/health
# Ожидается: {"status":"healthy"}
```

#### Проверка в браузере:

Откройте: **http://185.185.71.18:8080**

Войдите:
- Email: `admin@kkt-system.ru`
- Пароль: `admin`

#### Проверка Telegram бота:

1. Найдите бота в Telegram (используя токен или имя бота)
2. Отправьте команду: `/start`
3. Бот должен ответить приветственным сообщением

### Шаг 6: Смена пароля администратора (рекомендуется)

В веб-интерфейсе:
1. Войдите под admin
2. Перейдите в "Управление пользователями" или "Настройки"
3. Смените пароль на более безопасный

---

## Ручное развертывание (если нужен полный контроль)

Если хотите выполнять каждый этап отдельно, используйте скрипты:

```bash
cd /root/kkt-deployment

# 1. Базовая настройка
./01_vds_setup.sh

# 2. База данных
export DB_PASSWORD="ChangeThisStrongPassword123!"
./02_database_setup.sh

# 3. Приложение
./03_app_setup.sh

# 4. Systemd сервисы
./04_services_setup.sh

# 5. Nginx (без SSL, только HTTP на порту 8080)
./05_nginx_setup.sh

# 6. Автоматические бэкапы
./06_backup_setup.sh
```

---

## Полезные команды

### Управление сервисами:

```bash
# Перезапуск
sudo systemctl restart kkt-web kkt-bot

# Логи в реальном времени
sudo journalctl -u kkt-web -f
sudo journalctl -u kkt-bot -f

# Логи последние 100 строк
sudo journalctl -u kkt-web -n 100
```

### База данных:

```bash
# Подключение
PGPASSWORD=ChangeThisStrongPassword123! psql -U kkt_user -d kkt_production -h localhost

# Проверка пользователей
SELECT * FROM users;

# Проверка клиентов
SELECT * FROM clients;
```

### Бэкапы:

```bash
# Список бэкапов
ls -lh /home/kktapp/backups/

# Ручной бэкап
sudo -u kktapp /home/kktapp/backup-database.sh

# Восстановление из бэкапа
gunzip -c /home/kktapp/backups/kkt_backup_YYYYMMDD_HHMMSS.sql.gz | \
  PGPASSWORD=ChangeThisStrongPassword123! psql -U kkt_user -d kkt_production -h localhost
```

### Nginx:

```bash
# Проверка конфигурации
sudo nginx -t

# Перезагрузка
sudo systemctl reload nginx

# Логи доступа
sudo tail -f /var/log/nginx/access.log

# Логи ошибок
sudo tail -f /var/log/nginx/error.log
```

---

## Решение проблем

### Сервис не запускается:

```bash
# Смотрим детальные логи
sudo journalctl -u kkt-web -xe

# Проверяем .env файл
cat /home/kktapp/kkt-system/.env

# Проверяем права
ls -la /home/kktapp/kkt-system/.env
# Должно быть: -rw------- kktapp kktapp
```

### Бот не отвечает:

```bash
# Проверяем логи бота
sudo journalctl -u kkt-bot -n 50

# Проверяем токен в .env
grep TELEGRAM_BOT_TOKEN /home/kktapp/kkt-system/.env

# Перезапускаем бота
sudo systemctl restart kkt-bot
```

### Не работает веб-интерфейс:

```bash
# Проверяем Nginx
sudo nginx -t
sudo systemctl status nginx

# Проверяем backend
curl http://localhost:8000/health

# Проверяем firewall
sudo ufw status
```

---

## Чек-лист развертывания

- [ ] Подключился к VDS через SSH
- [ ] Загрузил deployment файлы
- [ ] Запустил `deploy_production.sh`
- [ ] Дождался завершения (без ошибок)
- [ ] Обновил Telegram ID администратора
- [ ] Проверил статус сервисов (оба `active`)
- [ ] Открыл веб-интерфейс в браузере (http://185.185.71.18:8080)
- [ ] Авторизовался под admin
- [ ] Проверил Telegram бота (команда `/start`)
- [ ] Сменил пароль администратора
- [ ] Создал тестового клиента
- [ ] Создал тестовый дедлайн

---

## Доступы после развертывания

**Веб-интерфейс:**
- URL: http://185.185.71.18:8080
- Email: admin@kkt-system.ru
- Пароль: admin (СМЕНИТЬ!)

**База данных:**
- Host: localhost
- Port: 5432
- Database: kkt_production
- User: kkt_user
- Password: ChangeThisStrongPassword123!

**Telegram бот:**
- Token: 8264704702:AAFeqS4ufig5r8yZmqdqzMiC786VO-kcf3U
- Admin ID: 5064340711

**SSH:**
- Host: 185.185.71.18
- User: root
- Password: iDGZJ6ygXN3RlOwX
- App user: kktapp (без пароля, только su/sudo)

---

## Следующие шаги (опционально)

### Настройка SSL (если есть домен):

```bash
# Установить certbot
sudo apt install certbot python3-certbot-nginx

# Получить сертификат
sudo certbot --nginx -d your-domain.com
```

### Настройка группы администраторов в Telegram:

1. Создайте группу в Telegram
2. Добавьтуда бота
3. Получите chat_id группы
4. Добавьте в .env: `ADMIN_GROUP_CHAT_ID=-1001234567890`
5. Перезапустите бота

### Настройка email уведомлений:

Отредактируйте `.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

**Примечание:** Вся настройка автоматизирована. Если что-то пошло не так, смотрите логи сервисов и раздел "Решение проблем".
