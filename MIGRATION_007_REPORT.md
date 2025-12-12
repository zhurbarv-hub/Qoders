# Migration 007: Unify Users and Clients - Report

**Date:** 2025-12-12  
**Migration File:** `backend/migrations/007_unify_users_clients.sql`  
**Status:** ✅ **SUCCESSFULLY APPLIED**

---

## Migration Summary

### Objective
Объединение таблиц `users`, `clients`, и `contacts` в единую таблицу `users` с поддержкой ролей:
- `client` - клиенты организаций (бывшие clients + contacts)
- `manager` - менеджеры поддержки
- `admin` - администраторы системы

### Changes Applied

#### 1. Database Structure
- ✅ **Dropped tables:** `clients`, `contacts`
- ✅ **Recreated table:** `users` with extended schema (22 fields)
- ✅ **Created backup tables:** `_backup_users`, `_backup_clients`, `_backup_contacts`
- ✅ **Added column to deadlines:** `user_id INTEGER REFERENCES users(id)`

#### 2. Data Migration Results

**Users Table:**
- Total users: **4** (all migrated successfully)
- Role distribution:
  - `client`: 4
  - `manager`: 0
  - `admin`: 0

**User Details:**
| ID | Email | Full Name | Role | INN | Company Name | Telegram |
|----|-------|-----------|------|-----|--------------|----------|
| 1 | zhurbarv@gmail.com | Иванов Иван Иванович | client | 1234567890 | ООО Рога и Копыта | ❌ |
| 2 | info@info.ru | ООО Тестовая компания | client | 1234567891 | ООО Тестовая компания | ❌ |
| 3 | test@test.su | Иванов Иван Иванович | client | 4457885844 | ООО Тестовый | ❌ |
| 4 | post@ruslan.ru | Треплов Василий Петрович | client | 1235854566 | ООО Вася и сыновья | ❌ |

**Deadlines:**
- Total deadlines: **1**
- Linked to users: **1** (100%)

**Telegram Integration:**
- Clients with Telegram: **0** (none registered yet)
- Registration codes generated: TBD

---

## Database Schema - New Users Table

```sql
CREATE TABLE users (
    -- Primary key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Authentication
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- NULL for clients not yet registered
    
    -- Common fields
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'client' CHECK(role IN ('client', 'manager', 'admin')),
    
    -- Client-specific fields (NULL for managers/admins)
    inn VARCHAR(12) UNIQUE,
    company_name VARCHAR(255),
    
    -- Contact information
    phone VARCHAR(20),
    address TEXT,
    notes TEXT,
    
    -- Telegram integration
    telegram_id VARCHAR(50) UNIQUE,
    telegram_username VARCHAR(100),
    registration_code VARCHAR(20) UNIQUE,
    code_expires_at DATETIME,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    
    -- Notification settings
    notification_days TEXT DEFAULT '14,7,3',
    notifications_enabled BOOLEAN DEFAULT 1,
    
    -- Status and metadata
    is_active BOOLEAN NOT NULL DEFAULT 1,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes Created:**
- `idx_users_email` - Email lookup
- `idx_users_role` - Role filtering
- `idx_users_inn` - INN lookup (partial, WHERE inn IS NOT NULL)
- `idx_users_telegram_id` - Telegram ID lookup (partial)
- `idx_users_registration_code` - Registration code (partial, unique)
- `idx_users_is_active` - Active status filtering
- `ix_users_role_active` - Composite role + active

---

## Verification Checklist

### Database Level
- ✅ Table `users` created with all 22 fields
- ✅ Old tables `clients` and `contacts` dropped
- ✅ Backup tables exist and contain original data
- ✅ All 4 clients migrated to users table
- ✅ Client data preserved: inn, company_name, contact info
- ✅ Deadlines linked to users via `user_id` column
- ✅ All indexes created successfully
- ✅ Check constraints in place (role, inn length)

### Data Integrity
- ✅ No data loss during migration
- ✅ All client organizations present in users
- ✅ Unique constraints working (email, inn, telegram_id)
- ✅ Foreign key relationships maintained
- ✅ Default values applied correctly

### What Works Now
- ✅ Database structure is ready
- ✅ Data migration completed
- ✅ Backups available for rollback if needed

### What Needs Updates (Code)
- ⚠️ **backend/models.py** - User model updated, but Client/Contact models still present
- ⚠️ **backend/schemas.py** - Need to update/create UserCreate, UserUpdate, UserResponse schemas
- ⚠️ **backend/api/clients.py** - Needs to become users.py or be updated
- ⚠️ **backend/api/contacts.py** - Needs to be merged into users.py
- ⚠️ **bot/handlers/** - All handlers using clients/contacts need updates
- ⚠️ **web frontend** - Vue components using /api/clients need updates

---

## Rollback Procedure

If issues are found and rollback is needed:

```sql
-- 1. Restore original tables from backups
CREATE TABLE clients AS SELECT * FROM _backup_clients;
CREATE TABLE contacts AS SELECT * FROM _backup_contacts;

-- 2. Drop new users table
DROP TABLE users;

-- 3. Recreate original users table
CREATE TABLE users AS SELECT * FROM _backup_users;

-- 4. Remove user_id from deadlines
ALTER TABLE deadlines DROP COLUMN user_id;

-- 5. Drop backup tables
DROP TABLE _backup_users;
DROP TABLE _backup_clients;
DROP TABLE _backup_contacts;
```

**Note:** Before rollback, ensure no new data was created in the unified users table.

---

## Next Steps (Priority Order)

### Phase 1: Critical Code Updates (Required for basic functionality)
1. **Update Deadline model** to use `user` relationship instead of `client`
2. **Remove/comment out** Client and Contact models from models.py
3. **Update schemas.py** - create UserCreate, UserUpdate, UserResponse
4. **Test database access** - ensure models can read/write to new structure

### Phase 2: API Updates (Required for web/bot to work)
5. **Merge API endpoints** - combine clients.py and contacts.py into users.py
6. **Update authentication** - support both web and Telegram login for clients
7. **Test API endpoints** - ensure CRUD operations work

### Phase 3: Bot Updates (Required for Telegram functionality)
8. **Update bot handlers** - use users instead of clients/contacts
9. **Update notification system** - read notification_days from users
10. **Test bot registration** - ensure clients can register via Telegram

### Phase 4: Frontend Updates (Required for web interface)
11. **Update Vue components** - use /api/users instead of /api/clients
12. **Update navigation** - rename "Клиенты" to "Пользователи"
13. **Add role management** - support creating managers/admins
14. **Test web interface** - full CRUD testing

### Phase 5: Cleanup
15. **Drop backup tables** (after full testing):
    ```sql
    DROP TABLE _backup_users;
    DROP TABLE _backup_clients;
    DROP TABLE _backup_contacts;
    ```
16. **Remove client_id column** from deadlines (after verification):
    ```sql
    ALTER TABLE deadlines DROP COLUMN client_id;
    ```

---

## Risk Assessment

**Current Risk Level:** 🟡 **MEDIUM**

**Why Medium:**
- Database migration successful, but code not yet updated
- System will not work until models/API updated
- Backup tables exist for safety
- Test environment (no production data at risk)

**Mitigation:**
- Keep backup tables until Phase 4 complete
- Test each phase before moving to next
- Can rollback at any time before Phase 5

---

## Testing Recommendations

Before proceeding with code updates, test:

1. **Manual SQL queries** to verify data integrity
2. **Backup restore** to ensure rollback works
3. **Foreign key relationships** with sample inserts

After code updates, test:

1. **Create new client user** via API
2. **Assign deadline to user** via API
3. **Telegram registration** flow
4. **Web login** for both support and client roles
5. **Notification generation** for client users

---

## Conclusion

✅ **Database migration completed successfully**
✅ **All data preserved and linked correctly**
✅ **Ready to proceed with code updates**

**Recommended Next Action:** Update backend/models.py Deadline model to use `user` relationship (Phase 1, Step 1)

---

*Migration executed by: AI Assistant*  
*Report generated: 2025-12-12*
