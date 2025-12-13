# -*- coding: utf-8 -*-
"""
Проверка загруженной версии сервиса в работающем веб-сервере
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def check_server():
    """Проверка состояния сервера"""
    
    print("\n" + "="*70)
    print("ДИАГНОСТИКА: Проверка веб-сервера")
    print("="*70 + "\n")
    
    # 1. Проверка доступности сервера
    print("1️⃣ Проверка доступности сервера...")
    try:
        response = requests.get(f"{BASE_URL}/api/deadline-types", timeout=5)
        print(f"✅ Сервер доступен (код ответа: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"❌ Сервер НЕ доступен на {BASE_URL}")
        print(f"   Запустите сервер командой: start_web.bat")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    
    # 2. Проверка времени запуска сервера
    print(f"\n2️⃣ Информация о процессах...")
    import subprocess
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             "Get-Process | Where-Object {$_.ProcessName -like '*uvicorn*'} | Select-Object Id, ProcessName, StartTime | Format-Table"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(result.stdout)
        
        # Пытаемся извлечь время запуска
        lines = result.stdout.split('\n')
        for line in lines:
            if 'uvicorn' in line.lower():
                print(f"⚠️ ВАЖНО: Если сервер был запущен до исправления кода,")
                print(f"   необходимо перезапустить его для применения изменений!")
                break
    except Exception as e:
        print(f"   Не удалось получить информацию о процессах: {e}")
    
    # 3. Проверка типов дедлайнов через API
    print(f"\n3️⃣ Проверка типов дедлайнов через API...")
    print("   (Требуется авторизация - пропускаем)")
    
    print("\n" + "="*70)
    print("РЕКОМЕНДАЦИИ:")
    print("="*70)
    print()
    print("🔄 ПЕРЕЗАПУСТИТЕ ВЕБ-СЕРВЕР для применения изменений:")
    print()
    print("   1. Нажмите Ctrl+C в окне, где запущен сервер")
    print("   2. Выполните: .\\start_web.bat")
    print()
    print("   ИЛИ в PowerShell:")
    print("   Get-Process -Name uvicorn | Stop-Process -Force")
    print("   cd d:\\QoProj\\KKT")
    print("   .\\start_web.bat")
    print()
    print("✅ После перезапуска попробуйте снова изменить дату в карточке ККТ")
    print("="*70 + "\n")
    
    return True

if __name__ == "__main__":
    check_server()
