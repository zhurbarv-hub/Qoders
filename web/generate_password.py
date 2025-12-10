# -*- coding: utf-8 -*-
"""
Генерация хеша пароля для веб-пользователей
"""
import bcrypt

def generate_password_hash(password: str) -> str:
    """Генерация хеша пароля"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

if __name__ == "__main__":
    # Генерируем хеш для пароля admin123
    password = "admin123"
    hash_value = generate_password_hash(password)
    
    print("=" * 60)
    print("ГЕНЕРАЦИЯ ХЕША ПАРОЛЯ")
    print("=" * 60)
    print(f"\n🔑 Пароль: {password}")
    print(f"🔐 Хеш: {hash_value}")
    print("\n✅ Используйте этот хеш для обновления пользователя")
    print("=" * 60)