# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('web/app/kkt.db')
c = conn.cursor()

# List all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()
