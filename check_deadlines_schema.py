# -*- coding: utf-8 -*-
"""
Проверка структуры таблицы deadlines в БД
"""
import sqlite3

db_path = 'database/kkt_services.db'

conn = sqlite3.connect(db_path)
c = conn.cursor()

print("=" * 80)
print("СТРУКТУРА ТАБЛИЦЫ deadlines")
print("=" * 80)

# Получить информацию о таблице
c.execute("PRAGMA table_info(deadlines)")
columns = c.fetchall()

print("\nКолонки:")
for col in columns:
    col_id, name, type_, notnull, default, pk = col
    nullable = "NULL" if not notnull else "NOT NULL"
    pk_mark = " (PRIMARY KEY)" if pk else ""
    print(f"  {name}: {type_} {nullable}{pk_mark}")
    
    if name == 'deadline_type_id':
        if notnull:
            print("    ⚠️ ПРОБЛЕМА: Поле NOT NULL - нужно изменить на NULL")
        else:
            print("    ✅ Поле nullable - можно удалять типы")

# Получить foreign keys
print("\nFOREIGN KEYS:")
c.execute("PRAGMA foreign_key_list(deadlines)")
fks = c.fetchall()

for fk in fks:
    fk_id, seq, table, from_col, to_col, on_update, on_delete, match = fk
    print(f"  {from_col} -> {table}({to_col}) ON DELETE {on_delete}")
    
    if from_col == 'deadline_type_id':
        if on_delete == 'RESTRICT':
            print("    ⚠️ ПРОБЛЕМА: ON DELETE RESTRICT - блокирует удаление")
        elif on_delete == 'SET NULL':
            print("    ✅ ON DELETE SET NULL - автоматическая очистка")
        elif on_delete == 'NO ACTION':
            print("    ⚠️ ON DELETE NO ACTION - может блокировать")

# Проверить количество дедлайнов
c.execute("SELECT COUNT(*) FROM deadlines")
total = c.fetchone()[0]
print(f"\nВсего дедлайнов в БД: {total}")

# Проверить дедлайны с типами
c.execute("SELECT COUNT(*) FROM deadlines WHERE deadline_type_id IS NOT NULL")
with_type = c.fetchone()[0]
print(f"С указанным типом: {with_type}")

c.execute("SELECT COUNT(*) FROM deadlines WHERE deadline_type_id IS NULL")
without_type = c.fetchone()[0]
print(f"Без типа (NULL): {without_type}")

conn.close()

print("\n" + "=" * 80)
