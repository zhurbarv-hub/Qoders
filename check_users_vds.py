import psycopg2

conn = psycopg2.connect("postgresql://kkt_user:KKT2024SecurePass@localhost:5432/kkt_production")
cur = conn.cursor()
cur.execute("SELECT email, role FROM users LIMIT 5")
print(cur.fetchall())
cur.close()
conn.close()
