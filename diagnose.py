import sys
import subprocess

print("=" * 60)
print("ДИАГНОСТИКА ОКРУЖЕНИЯ PYTHON")
print("=" * 60)

print(f"\nPython версия: {sys.version}")
print(f"Python путь: {sys.executable}")
print(f"Python prefix: {sys.prefix}")

print("\n" + "=" * 60)
print("ПОПЫТКА УСТАНОВКИ ТЕСТОВОГО ПАКЕТА")
print("=" * 60)

try:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "requests"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Установка работает!")
        print(result.stdout)
    else:
        print("❌ Ошибка установки:")
        print(result.stderr)
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")

print("\n" + "=" * 60)
print("ПРОВЕРКА СЕТЕВОГО ПОДКЛЮЧЕНИЯ К PyPI")
print("=" * 60)

try:
    import urllib.request
    response = urllib.request.urlopen('https://pypi.org', timeout=5)
    print(f"✅ PyPI доступен (статус: {response.status})")
except Exception as e:
    print(f"❌ PyPI недоступен: {e}")