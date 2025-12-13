# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('database/kkt_services.db')
c = conn.cursor()
c.execute('SELECT COUNT(*), SUM(CASE WHEN is_system=1 THEN 1 ELSE 0 END) FROM deadline_types')
total, system = c.fetchone()
print(f"Total types: {total}, System types: {system or 0}")

# Update all to non-system
c.execute('UPDATE deadline_types SET is_system = 0 WHERE is_system = 1')
conn.commit()
updated = c.rowcount
print(f"Updated: {updated} types")

# Check again
c.execute('SELECT COUNT(*), SUM(CASE WHEN is_system=1 THEN 1 ELSE 0 END) FROM deadline_types')
total, system = c.fetchone()
print(f"After update - Total: {total}, System: {system or 0}")

conn.close()
print("Done!")
