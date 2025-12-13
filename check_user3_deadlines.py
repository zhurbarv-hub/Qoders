import sqlite3

conn = sqlite3.connect('D:/QoProj/KKT/database/kkt_services.db')
cur = conn.cursor()

print('\n=== Deadlines для user_id=3 ===')
for row in cur.execute('SELECT id, user_id, cash_register_id, expiration_date FROM deadlines WHERE user_id=3'):
    print(f"ID: {row[0]}, user_id: {row[1]}, cash_register_id: {row[2]}, expiration: {row[3]}")

print('\n=== Кассы для user_id=3 ===')
for row in cur.execute('SELECT id, serial_number, register_name FROM cash_registers WHERE user_id=3'):
    print(f"ID: {row[0]}, serial: {row[1]}, name: {row[2]}")

print('\n=== Все дедлайны с cash_register_id не NULL ===')
for row in cur.execute('SELECT id, user_id, cash_register_id FROM deadlines WHERE cash_register_id IS NOT NULL LIMIT 10'):
    print(f"ID: {row[0]}, user_id: {row[1]}, cash_register_id: {row[2]}")

conn.close()
