"""
Диагностика HTML-форматирования сообщений
Находит все проблемные символы < и >
"""
import sys
import os
from datetime import date

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.models import Client, Deadline
from bot.services.formatter import format_statistics

print("=" * 60)
print("ДИАГНОСТИКА HTML-ФОРМАТИРОВАНИЯ")
print("=" * 60)

try:
    # Получаем сессию
    db_session = SessionLocal()
    
    # Собираем статистику (как в admin.py)
    stats = {}
    
    stats['active_clients_count'] = db_session.query(Client).filter(
        Client.is_active == True
    ).count()
    
    all_deadlines = db_session.query(Deadline).filter(
        Deadline.status == 'active'
    ).all()
    
    stats['total_deadlines_count'] = len(all_deadlines)
    
    # Подсчёт по цветам
    today = date.today()
    green_count = 0
    yellow_count = 0
    red_count = 0
    expired_count = 0
    
    for deadline in all_deadlines:
        days_remaining = (deadline.expiration_date - today).days
        
        if days_remaining < 0:
            expired_count += 1
        elif days_remaining < 7:
            red_count += 1
        elif days_remaining < 14:
            yellow_count += 1
        else:
            green_count += 1
    
    stats['green_count'] = green_count
    stats['yellow_count'] = yellow_count
    stats['red_count'] = red_count
    stats['expired_count'] = expired_count
    
    # Ближайшие дедлайны
    upcoming = db_session.query(Deadline).join(
        Client
    ).filter(
        Deadline.status == 'active',
        Deadline.expiration_date >= today
    ).order_by(
        Deadline.expiration_date.asc()
    ).limit(5).all()
    
    print("\n🔍 ПРОВЕРКА ДАННЫХ ИЗ БД:\n")
    for i, d in enumerate(upcoming, 1):
        client_name = d.client.name
        type_name = d.deadline_type.type_name
        
        print(f"{i}. Client: {repr(client_name)}")
        print(f"   Type: {repr(type_name)}")
        
        # Ищем опасные символы
        if '<' in client_name or '>' in client_name:
            print(f"   ⚠️ ОПАСНО: Символ < или > в названии клиента!")
        if '<' in type_name or '>' in type_name:
            print(f"   ⚠️ ОПАСНО: Символ < или > в типе дедлайна!")
        print()
    
    stats['upcoming_deadlines'] = [
        {
            'client_name': d.client.name,
            'type_name': d.deadline_type.type_name,
            'expiration_date': d.expiration_date
        }
        for d in upcoming
    ]
    
    # Генерируем сообщение
    message = format_statistics(stats)
    
    # Показываем полное сообщение
    print("=" * 60)
    print("\n📝 ПОЛНОЕ СООБЩЕНИЕ:\n")
    print(message)
    print("\n" + "=" * 60)
    
    # Ищем проблемные символы
    print("\n🔍 ПОИСК ПРОБЛЕМНЫХ HTML-ТЕГОВ:\n")
    
    problems_found = 0
    
    for i, char in enumerate(message):
        if char == '<':
            # Проверяем, это HTML-тег или проблема?
            next_chars = message[i:min(len(message), i+15)]
            
            # Список разрешённых HTML-тегов
            valid_tags = ['<b>', '</b>', '<i>', '</i>', '<code>', '</code>', 
                         '<pre>', '</pre>', '<u>', '</u>', '<s>', '</s>',
                         '<a ', '<tg-spoiler>', '</tg-spoiler>']
            
            is_valid = any(next_chars.startswith(tag) for tag in valid_tags)
            
            if not is_valid:
                problems_found += 1
                start = max(0, i - 20)
                end = min(len(message), i + 30)
                context = message[start:end]
                
                print(f"❌ ПРОБЛЕМА #{problems_found} на позиции {i}:")
                print(f"   Контекст: ...{context}...")
                print(f"   Следующие символы: {next_chars}")
                print()
    
    if problems_found == 0:
        print("✅ Проблемных символов '<' не найдено!")
    
    # Показываем байт-оффсет 380
    print("=" * 60)
    print(f"\n📍 СИМВОЛ НА ПОЗИЦИИ 380 (из ошибки Telegram):\n")
    if len(message) > 380:
        context_380 = message[max(0, 360):min(len(message), 400)]
        print(f"Контекст: ...{context_380}...")
        print(f"Символ [380]: '{message[380]}' (ASCII: {ord(message[380])})")
        
        # Проверяем окружение
        if message[380] == '<':
            next_10 = message[380:min(len(message), 390)]
            print(f"❗ Следующие 10 символов: {next_10}")
    else:
        print(f"⚠️ Сообщение короче 380 символов (длина: {len(message)})")
    
    print("\n" + "=" * 60)
    print(f"📊 ДЛИНА СООБЩЕНИЯ: {len(message)} символов")
    print(f"📊 НАЙДЕНО ПРОБЛЕМ: {problems_found}")
    print("=" * 60)
    
    # Закрываем сессию
    db_session.close()
    
except Exception as e:
    print(f"\n❌ ОШИБКА ПРИ ВЫПОЛНЕНИИ:\n")
    print(f"{type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()