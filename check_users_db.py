import sqlite3

db_path = "database/kkt_services.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("ПОЛЬЗОВАТЕЛИ В БД")
    print("=" * 60)
    
    # Проверка всех пользователей
    cursor.execute("""
        SELECT id, username, email, role, is_active, password_hash IS NOT NULL as has_password
        FROM users
        ORDER BY role, id
    """)
    
    users = cursor.fetchall()
    
    if not users:
        print("❌ Пользователи не найдены!")
    else:
        print(f"\nВсего пользователей: {len(users)}\n")
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<10} {'Active':<8} {'HasPwd':<8}")
        print("-" * 90)
        
        for user in users:
            user_id, username, email, role, is_active, has_pwd = user
            print(f"{user_id:<5} {username:<20} {email:<30} {role:<10} {str(bool(is_active)):<8} {str(bool(has_pwd)):<8}")
    
    print("\n" + "=" * 60)
    
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка при работе с БД: {e}")
