#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для деплоя исправлений Telegram бота на VDS
"""

import paramiko
import os
import sys

# Настройки подключения
VDS_HOST = "185.185.71.248"
VDS_PORT = 40022
VDS_USER = "root"
VDS_PASSWORD = None  # Будет использоваться SSH ключ

# Файлы для деплоя
FILES_TO_DEPLOY = [
    {
        'local': r'd:\QoProj\KKT\bot\services\notifier.py',
        'remote': '/root/kkt_system/bot/services/notifier.py'
    },
    {
        'local': r'd:\QoProj\KKT\bot\services\formatter.py',
        'remote': '/root/kkt_system/bot/services/formatter.py'
    }
]

def deploy_files():
    """Деплой файлов на VDS"""
    print("=" * 60)
    print("🚀 ДЕПЛОЙ ИСПРАВЛЕНИЙ TELEGRAM БОТА")
    print("=" * 60)
    
    try:
        # Создаем SSH клиент
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"\n📡 Подключение к {VDS_HOST}:{VDS_PORT}...")
        
        # Подключаемся
        ssh.connect(
            hostname=VDS_HOST,
            port=VDS_PORT,
            username=VDS_USER,
            look_for_keys=True,
            allow_agent=True
        )
        
        print("✅ Подключено успешно!\n")
        
        # Создаем SFTP клиент
        sftp = ssh.open_sftp()
        
        # Копируем файлы
        for file_info in FILES_TO_DEPLOY:
            local_path = file_info['local']
            remote_path = file_info['remote']
            
            if not os.path.exists(local_path):
                print(f"❌ Локальный файл не найден: {local_path}")
                continue
            
            print(f"📤 Копирую: {os.path.basename(local_path)}")
            print(f"   Источник: {local_path}")
            print(f"   Назначение: {remote_path}")
            
            sftp.put(local_path, remote_path)
            print(f"✅ Скопировано!\n")
        
        sftp.close()
        
        # Перезапускаем бота
        print("🔄 Перезапуск Telegram бота...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart kkt_bot')
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code == 0:
            print("✅ Бот перезапущен успешно!\n")
        else:
            print(f"⚠️ Код возврата: {exit_code}")
            error_output = stderr.read().decode('utf-8')
            if error_output:
                print(f"Ошибка: {error_output}\n")
        
        # Проверяем статус бота
        print("📊 Проверка статуса бота...")
        stdin, stdout, stderr = ssh.exec_command('systemctl status kkt_bot --no-pager')
        status_output = stdout.read().decode('utf-8')
        
        if 'active (running)' in status_output:
            print("✅ Бот работает!\n")
        else:
            print("⚠️ Проблема со статусом бота:")
            print(status_output[:500])
        
        ssh.close()
        
        print("=" * 60)
        print("✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО")
        print("=" * 60)
        print("\n📝 Изменения:")
        print("  1. Добавлен parse_mode='HTML' в send_notification()")
        print("  2. Улучшено форматирование уведомлений с детализацией")
        print("  3. Добавлены уровни срочности и призывы к действию")
        print("\n🔔 Теперь HTML-теги будут правильно отображаться!")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    deploy_files()
