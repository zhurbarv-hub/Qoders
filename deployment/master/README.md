# Master Distribution Server Setup

Файлы для настройки Master Distribution Server на kkt-box.net.

## Файлы

- `client_registry_schema.sql` - SQL схема для базы данных реестра клиентов
- `setup_client_registry.sh` - Bash скрипт для создания БД на VDS
- `deploy_client_registry.ps1` - PowerShell скрипт для автоматического развертывания

## Быстрый старт

### Windows (PowerShell)

```powershell
cd deployment\master
.\deploy_client_registry.ps1
```

### Linux/Mac (или вручную на VDS)

```bash
# 1. Скопировать файлы на VDS
scp client_registry_schema.sql root@185.185.71.248:/tmp/
scp setup_client_registry.sh root@185.185.71.248:/tmp/

# 2. Подключиться к VDS
ssh root@185.185.71.248

# 3. Выполнить setup
cd /tmp
chmod +x setup_client_registry.sh
./setup_client_registry.sh
```

## Что создается

### База данных: `kkt_master_registry`

**Таблицы:**
- `admin_users` - администраторы системы развертывания
- `deployed_instances` - реестр развернутых инсталляций
- `deployment_history` - история всех операций
- `available_releases` - каталог релизов из GitHub

**Начальные данные:**
- Суперадмин: `admin@kkt-master.local` / `admin123`

## Проверка

После установки проверьте БД:

```bash
# На VDS
sudo -u postgres psql -d kkt_master_registry

# Просмотр таблиц
\dt

# Проверка админа
SELECT email, role FROM admin_users;

# Выход
\q
```

## Следующие шаги

После создания Client Registry:
1. ✅ Создать первый GitHub Release (v1.0.0)
2. ✅ Развернуть тестовую инсталляцию
3. ✅ Создать Deployment Wizard Backend
