from web.app.database import SessionLocal
from web.app.models.user import WebUser

db = SessionLocal()
users = db.query(WebUser).all()

print("\n=== WEB USERS ===")
for u in users:
    print(f"ID: {u.id}, Username: {u.username}, Email: {u.email}, Role: {u.role}")
print(f"\nTotal: {len(users)} users")
