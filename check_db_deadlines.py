import sqlite3
import os

# Путь к базе данных
db_path = r"d:\QoProj\KKT\database\kkt_services.db"

if not os.path.exists(db_path):
    print(f"База данных не найдена: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Получаем все дедлайны
    cursor.execute("""
        SELECT 
            d.id,
            c.name as client_name,
            dt.type_name,
            d.expiration_date,
            d.client_id,
            d.deadline_type_id
        FROM deadlines d
        LEFT JOIN clients c ON d.client_id = c.id
        LEFT JOIN deadline_types dt ON d.deadline_type_id = dt.id
        ORDER BY d.id
    """)
    
    deadlines = cursor.fetchall()
    
    print(f"=== ДЕДЛАЙНЫ В БАЗЕ ДАННЫХ ===")
    print(f"Всего дедлайнов: {len(deadlines)}\n")
    
    for idx, (id, client, type_name, exp_date, client_id, type_id) in enumerate(deadlines, 1):
        client_display = client if client else f"NULL (client_id={client_id})"
        type_display = type_name if type_name else f"NULL (type_id={type_id})"
        print(f"{idx}. ID={id}, Клиент=\"{client_display}\", Тип=\"{type_display}\", Дата={exp_date}")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"Ошибка работы с БД: {e}")
