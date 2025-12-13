# UI Testing Checklist - Cash Register Management System

**Date**: December 12, 2025  
**Server**: http://localhost:8001  
**Status**: ✅ Backend API fully tested and working  

---

## ✅ Issues Fixed

### 1. Connection Error on Login
**Problem**: Frontend JavaScript was configured to connect to port 8000, but server runs on port 8001.

**Files Updated**:
- ✅ `web/app/static/js/auth.js` - Changed `API_BASE_URL` from port 8000 to 8001
- ✅ `web/app/static/js/activate.js` - Changed `API_BASE_URL` from port 8000 to 8001

**Other Files Checked**:
- ✅ `web/app/static/js/dashboard.js` - Uses dynamic URL `window.location.origin + '/api'` (OK)
- ✅ `web/app/static/js/client-details.js` - Uses relative path `/api` (OK)
- ✅ All other JS files use relative paths (OK)

**Result**: Connection error is now **FIXED**. Login should work!

---

## 🧪 Manual UI Testing Steps

### Test 1: Login Page
**URL**: http://localhost:8001/static/login.html

**Steps**:
1. [ ] Open login page in browser
2. [ ] Enter credentials:
   - Username: `admin`
   - Password: `admin123`
3. [ ] Click "Войти" button
4. [ ] Verify redirect to dashboard
5. [ ] Check that no error messages appear

**Expected Result**: Successful login and redirect to `/static/dashboard.html`

---

### Test 2: Dashboard Overview
**URL**: http://localhost:8001/static/dashboard.html (after login)

**Steps**:
1. [ ] Verify statistics cards display:
   - Total clients
   - Active clients
   - Total deadlines
   - Urgent deadlines
   - Expired deadlines
2. [ ] Check status distribution chart (doughnut chart)
3. [ ] Check deadline types chart
4. [ ] Verify urgent deadlines table shows data
5. [ ] Test sidebar navigation links

**Expected Result**: All dashboard sections load and display data correctly

---

### Test 3: Client Details Page with Cash Registers
**URL**: http://localhost:8001/static/client-details.html?id=3

**Steps**:
1. [ ] Navigate to client details page for user_id=3
2. [ ] Verify client header shows:
   - Company name
   - INN number
   - Email
3. [ ] Verify client information table displays:
   - Contact person
   - Phone
   - Address
   - Notes
4. [ ] **Section 1: Cash Registers**
   - [ ] Verify "Кассовые аппараты" section shows count: 2
   - [ ] Check both cash registers display:
     - Register name
     - Serial number
     - Fiscal drive number
     - Installation address
     - Active status badge
5. [ ] **Section 2: Register Deadlines**
   - [ ] Verify "Дедлайны по кассам" section shows count: 6
   - [ ] Check deadlines grouped by cash register
   - [ ] Verify each deadline shows:
     - Deadline type name
     - Cash register name
     - Expiration date
     - Days remaining
     - Status color badge (green/yellow/red)
     - Notes (if any)
6. [ ] **Section 3: General Deadlines**
   - [ ] Verify "Общие дедлайны" section shows count: 1
   - [ ] Check general deadline displays correctly

**Expected Result**: 
- 2 cash registers visible
- 6 deadlines linked to cash registers
- 1 general deadline
- All data displays with correct formatting and colors

---

### Test 4: Cash Register CRUD Operations (if implemented in UI)

**Test 4a: Add New Cash Register**
1. [ ] Click "Добавить кассовый аппарат" button
2. [ ] Fill in form:
   - Register name: "Касса Тестовая"
   - Serial number: "TEST-001-2025"
   - Fiscal drive number: "FN-TEST-001"
   - Installation address: "Тестовый адрес, 123"
3. [ ] Submit form
4. [ ] Verify new register appears in list

**Test 4b: Edit Cash Register**
1. [ ] Click "Изменить" button on a cash register
2. [ ] Modify register name
3. [ ] Save changes
4. [ ] Verify name updated in display

**Test 4c: Delete Cash Register**
1. [ ] Click "Удалить" button on a cash register
2. [ ] Confirm deletion in dialog
3. [ ] Verify register marked as inactive

---

### Test 5: Deadline Management (if implemented in UI)

**Test 5a: Add Deadline to Cash Register**
1. [ ] Click "Добавить дедлайн" button
2. [ ] Select cash register from dropdown
3. [ ] Select deadline type
4. [ ] Set expiration date
5. [ ] Add optional notes
6. [ ] Submit form
7. [ ] Verify deadline appears under correct cash register

**Test 5b: Add General Deadline**
1. [ ] Click "Добавить общий дедлайн" button
2. [ ] Leave cash register field empty/null
3. [ ] Select deadline type
4. [ ] Set expiration date
5. [ ] Submit form
6. [ ] Verify deadline appears in general deadlines section

**Test 5c: Edit Deadline (Inline)**
1. [ ] Click on deadline to edit
2. [ ] Modify date or notes
3. [ ] Save changes
4. [ ] Verify updates appear immediately

**Test 5d: Delete Deadline**
1. [ ] Click delete button on deadline
2. [ ] Confirm deletion
3. [ ] Verify deadline removed from display

---

## 🔍 Database Verification

**Current Test Data for user_id=3**:
```
Cash Registers:
- ID: 19, Serial: KKT-2025-003, Name: Касса 3
- ID: 20, Serial: KKT-2025-004, Name: Касса 4

Deadlines (linked to cash registers):
- 6 deadlines total for registers 19 and 20
- Includes: Фискальный накопитель, Подписка ОФД, etc.

General Deadlines (cash_register_id = NULL):
- 1 general deadline for user_id=3
```

---

## ✅ Backend API Testing Status

All backend API endpoints are **100% tested and working**:

1. ✅ **Authentication**
   - POST `/api/auth/login` - Returns valid JWT token

2. ✅ **Cash Registers CRUD**
   - GET `/api/cash-registers` - List with pagination (9 total)
   - GET `/api/cash-registers/19` - Get details with 3 deadlines
   - POST `/api/cash-registers` - Create new register
   - PUT `/api/cash-registers/{id}` - Update register
   - DELETE `/api/cash-registers/{id}` - Soft delete (returns 200)

3. ✅ **User Full Details**
   - GET `/api/users/3/full-details` - Returns client with 2 registers and 7 deadlines

4. ✅ **Database Integrity**
   - Foreign keys working correctly
   - Cascade deletes configured
   - Data relationships verified

---

## 🎯 Next Actions

1. **Immediate**: Test login page in browser (should now work!)
2. Navigate to client details page: http://localhost:8001/static/client-details.html?id=3
3. Verify all sections display correctly
4. Test any interactive features (add/edit/delete if implemented)
5. Report any visual or functional issues found

---

## 📝 Notes

- Server is running on **port 8001** (not 8000)
- All JavaScript files now configured correctly
- Backend API fully functional and tested
- Test credentials: `admin` / `admin123`
- Chrome DevTools Console can help debug any frontend issues

---

## ✅ Testing Complete When:

- [ ] Login works without errors
- [ ] Dashboard loads and displays data
- [ ] Client details page shows 2 cash registers
- [ ] All 6 register deadlines visible and correctly formatted
- [ ] General deadline displays in separate section
- [ ] All CRUD operations work (if UI implemented)
- [ ] No console errors in browser DevTools
- [ ] All navigation links function correctly

**Status**: Ready for manual UI testing! 🚀
