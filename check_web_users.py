import sqlite3

db_path = "database/kkt_services.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("WEB ПОЛЬЗОВАТЕЛИ (web_users)")
    print("=" * 60)
    
    cursor.execute("""
        SELECT id, username, email, full_name, role, is_active, 
               password_hash IS NOT NULL as has_password
        FROM web_users
        ORDER BY id
    """)
    
    users = cursor.fetchall()
    
    if not users:
        print("❌ Web-пользователи не найдены!")
    else:
        print(f"\nВсего web-пользователей: {len(users)}\n")
        print(f"{'ID':<5} {'Username':<15} {'Email':<30} {'FullName':<20} {'Role':<10} {'Active':<8} {'HasPwd':<8}")
        print("-" * 110)
        
        for user in users:
            user_id, username, email, full_name, role, is_active, has_pwd = user
            print(f"{user_id:<5} {username:<15} {email:<30} {(full_name or 'N/A'):<20} {role:<10} {str(bool(is_active)):<8} {str(bool(has_pwd)):<8}")
    
    print("\n" + "=" * 60)
    print("КЛИЕНТЫ И МЕНЕДЖЕРЫ (users)")
    print("=" * 60)
    
    cursor.execute("""
        SELECT id, email, full_name, role, is_active, company_name,
               password_hash IS NOT NULL as has_password
        FROM users
        WHERE role != 'client' OR role = 'admin'
        ORDER BY role, id
        LIMIT 10
    """)
    
    users = cursor.fetchall()
    
    if not users:
        print("❌ Админы/менеджеры не найдены!")
    else:
        print(f"\nАдминистраторов и менеджеров: {len(users)}\n")
        print(f"{'ID':<5} {'Email':<30} {'FullName':<20} {'Role':<10} {'Active':<8} {'Company':<20} {'HasPwd':<8}")
        print("-" * 125)
        
        for user in users:
            user_id, email, full_name, role, is_active, company, has_pwd = user
            print(f"{user_id:<5} {email:<30} {(full_name or 'N/A'):<20} {role:<10} {str(bool(is_active)):<8} {(company or 'N/A'):<20} {str(bool(has_pwd)):<8}")
    
    print("\n" + "=" * 60)
    
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка при работе с БД: {e}")
