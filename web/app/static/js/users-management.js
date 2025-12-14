// API базовый URL
const API_BASE = '/api';

// Текущая страница и параметры фильтрации
let currentPage = 1;
let currentFilters = {
    search: '',
    role: '',
    is_active: ''
};

// Данные текущего пользователя (из JWT)
let currentUser = null;

// ========== УТИЛИТЫ ==========

function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

function removeToken() {
    localStorage.removeItem('access_token');
}

function isAuthenticated() {
    return getToken() !== null;
}

// Декодирование JWT токена
function decodeToken(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('Ошибка декодирования токена:', error);
        return null;
    }
}

// Получение данных текущего пользователя
function getCurrentUser() {
    const token = getToken();
    if (!token) return null;
    return decodeToken(token);
}

// ========== ИНИЦИАЛИЗАЦИЯ ==========

document.addEventListener('DOMContentLoaded', function() {
    // Проверка авторизации
    if (!isAuthenticated()) {
        window.location.href = '/static/login.html';
        return;
    }
    
    // Получение данных текущего пользователя
    currentUser = getCurrentUser();
    
    if (!currentUser) {
        window.location.href = '/static/login.html';
        return;
    }
    
    // Проверка прав доступа (только admin и manager)
    if (currentUser.role !== 'admin' && currentUser.role !== 'manager') {
        alert('У вас нет прав для доступа к этой странице');
        window.location.href = '/static/dashboard.html';
        return;
    }
    
    // Отображение имени пользователя
    document.getElementById('sidebarUserName').textContent = currentUser.full_name || currentUser.email;
    
    // Обработчики событий
    document.getElementById('sidebarLogoutBtn').addEventListener('click', logout);
    document.getElementById('addUserBtn').addEventListener('click', showAddUserDialog);
    document.getElementById('applyFiltersBtn').addEventListener('click', applyFilters);
    document.getElementById('prevPageBtn').addEventListener('click', () => changePage(currentPage - 1));
    document.getElementById('nextPageBtn').addEventListener('click', () => changePage(currentPage + 1));
    
    // Поиск по нажатию Enter
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            applyFilters();
        }
    });
    
    // Загрузка пользователей
    loadUsers();
});

// ========== ЗАГРУЗКА ПОЛЬЗОВАТЕЛЕЙ ==========

async function loadUsers() {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px; color: #999;">Загрузка...</td></tr>';
    
    try {
        const params = new URLSearchParams({
            page: currentPage,
            page_size: 20
        });
        
        if (currentFilters.search) {
            params.append('search', currentFilters.search);
        }
        if (currentFilters.role) {
            params.append('role', currentFilters.role);
        }
        if (currentFilters.is_active !== '') {
            params.append('is_active', currentFilters.is_active);
        }
        
        const response = await fetch(`${API_BASE}/users?${params}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки пользователей');
        }
        
        const data = await response.json();
        renderUsers(data.users);
        updatePagination(data.page, data.total_pages, data.total);
    } catch (error) {
        console.error('Ошибка:', error);
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px; color: #dc3545;">Ошибка загрузки данных</td></tr>';
    }
}

// ========== ОТОБРАЖЕНИЕ ПОЛЬЗОВАТЕЛЕЙ ==========

function renderUsers(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px; color: #999;">Пользователи не найдены</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => {
        const displayName = user.company_name || user.full_name;
        const roleLabel = getRoleLabel(user.role);
        const statusBadge = getStatusBadge(user.is_active);
        const telegramBadge = user.telegram_id ? 
            `<span style="color: #28a745;">✓ @${user.telegram_username || 'Подключен'}</span>` : 
            '<span style="color: #999;">Не подключен</span>';
        
        return `
            <tr onclick="openUserDetails(${user.id})" style="cursor: pointer;">
                <td>
                    <div style="font-weight: 500;">${displayName}</div>
                    ${user.inn ? `<div style="font-size: 12px; color: #666;">ИНН: ${user.inn}</div>` : ''}
                </td>
                <td>${user.email}</td>
                <td>${roleLabel}</td>
                <td>${user.phone || '—'}</td>
                <td>${telegramBadge}</td>
                <td>${statusBadge}</td>
                <td onclick="event.stopPropagation()">
                    <button class="action-button secondary" onclick="editUser(${user.id})" title="Редактировать">
                        <i class="material-icons" style="font-size: 18px;">edit</i>
                    </button>
                    ${currentUser.role === 'admin' ? `
                        <button class="action-button secondary" onclick="changeUserPassword(${user.id})" title="Сменить пароль">
                            <i class="material-icons" style="font-size: 18px;">vpn_key</i>
                        </button>
                    ` : ''}
                </td>
            </tr>
        `;
    }).join('');
}

function getRoleLabel(role) {
    const labels = {
        'admin': '<span class="role-badge admin">Администратор</span>',
        'manager': '<span class="role-badge manager">Менеджер</span>',
        'client': '<span class="role-badge client">Клиент</span>'
    };
    return labels[role] || role;
}

function getStatusBadge(isActive) {
    if (isActive) {
        return '<span class="status-badge active"><i class="material-icons" style="font-size: 14px;">check_circle</i> Активен</span>';
    } else {
        return '<span class="status-badge inactive"><i class="material-icons" style="font-size: 14px;">cancel</i> Неактивен</span>';
    }
}

// ========== ПАГИНАЦИЯ ==========

function updatePagination(page, totalPages, total) {
    document.getElementById('pageInfo').textContent = `Страница ${page} из ${totalPages} (всего: ${total})`;
    document.getElementById('prevPageBtn').disabled = page <= 1;
    document.getElementById('nextPageBtn').disabled = page >= totalPages;
}

function changePage(page) {
    currentPage = page;
    loadUsers();
}

// ========== ФИЛЬТРАЦИЯ ==========

function applyFilters() {
    currentFilters.search = document.getElementById('searchInput').value.trim();
    currentFilters.role = document.getElementById('roleFilter').value;
    currentFilters.is_active = document.getElementById('statusFilter').value;
    currentPage = 1;
    loadUsers();
}

// ========== ВЫХОД ==========

function logout() {
    removeToken();
    window.location.href = '/static/login.html';
}

// ========== МОДАЛЬНЫЕ ОКНА: УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ==========

function showAddUserDialog() {
    // Очистка формы
    document.getElementById('userForm').reset();
    document.getElementById('userId').value = '';
    
    // Настройка заголовка и кнопки
    document.getElementById('userModalTitle').innerHTML = '<i class="material-icons" style="vertical-align: middle; margin-right: 8px; font-size: 24px;">person_add</i> Добавить пользователя';
    document.getElementById('saveButtonText').textContent = 'Создать';
    
    // Скрытие поля статус при создании
    document.getElementById('statusField').style.display = 'none';
    
    // Установка роли по умолчанию
    document.getElementById('userRole').value = 'client';
    handleRoleChange();
    
    // Логин редактируемый только при создании
    const usernameInput = document.getElementById('userUsername');
    usernameInput.removeAttribute('readonly');
    usernameInput.style.backgroundColor = '';
    usernameInput.style.cursor = '';
    
    // Показать модальное окно
    document.getElementById('userModalOverlay').style.display = 'flex';
}

async function editUser(userId) {
    try {
        // Загрузка данных пользователя
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки данных пользователя');
        }
        
        const user = await response.json();
        
        // Заполнение формы
        document.getElementById('userId').value = user.id;
        document.getElementById('userRole').value = user.role;
        document.getElementById('userUsername').value = user.username || '';
        document.getElementById('userFullName').value = user.full_name || '';
        document.getElementById('userEmail').value = user.email || '';
        document.getElementById('userPhone').value = user.phone || '';
        document.getElementById('userIsActive').value = user.is_active ? 'true' : 'false';
        document.getElementById('userCompanyName').value = user.company_name || '';
        document.getElementById('userInn').value = user.inn || '';
        document.getElementById('userAddress').value = user.address || '';
        document.getElementById('userNotes').value = user.notes || '';
        
        // Настройка заголовка и кнопки
        document.getElementById('userModalTitle').innerHTML = '<i class="material-icons" style="vertical-align: middle; margin-right: 8px; font-size: 24px;">edit</i> Редактировать пользователя';
        document.getElementById('saveButtonText').textContent = 'Сохранить';
        
        // Показать поле статус при редактировании
        document.getElementById('statusField').style.display = 'block';
        
        // Логин нельзя редактировать при изменении
        const usernameInput = document.getElementById('userUsername');
        usernameInput.setAttribute('readonly', 'readonly');
        usernameInput.style.backgroundColor = '#f5f5f5';
        usernameInput.style.cursor = 'not-allowed';
        
        // Показать/скрыть поля в зависимости от роли
        handleRoleChange();
        
        // Показать модальное окно
        document.getElementById('userModalOverlay').style.display = 'flex';
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка загрузки данных пользователя');
    }
}

function handleRoleChange() {
    const role = document.getElementById('userRole').value;
    const clientFields = document.getElementById('clientFields');
    const companyNameInput = document.getElementById('userCompanyName');
    const innInput = document.getElementById('userInn');
    
    if (role === 'client') {
        clientFields.style.display = 'block';
        companyNameInput.setAttribute('required', 'required');
        innInput.setAttribute('required', 'required');
    } else {
        clientFields.style.display = 'none';
        companyNameInput.removeAttribute('required');
        innInput.removeAttribute('required');
    }
}

function closeUserModal() {
    document.getElementById('userModalOverlay').style.display = 'none';
    document.getElementById('userForm').reset();
}

// Обработчик отправки формы пользователя
document.addEventListener('DOMContentLoaded', function() {
    // ... существующий код ...
    
    // Добавляем обработчик формы пользователя
    const userForm = document.getElementById('userForm');
    if (userForm) {
        userForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await saveUser();
        });
    }
});

async function saveUser() {
    const userId = document.getElementById('userId').value;
    const role = document.getElementById('userRole').value;
    
    // Подготовка данных
    const userData = {
        role: role,
        full_name: document.getElementById('userFullName').value.trim(),
        email: document.getElementById('userEmail').value.trim(),
        phone: document.getElementById('userPhone').value.trim() || null,
        address: document.getElementById('userAddress').value.trim() || null,
        notes: document.getElementById('userNotes').value.trim() || null
    };
    
    // Добавление username только при создании (не при редактировании)
    if (!userId) {
        userData.username = document.getElementById('userUsername').value.trim();
        if (!userData.username) {
            alert('Укажите логин');
            return;
        }
    }
    
    // Добавление полей для клиентов
    if (role === 'client') {
        userData.company_name = document.getElementById('userCompanyName').value.trim();
        userData.inn = document.getElementById('userInn').value.trim();
        
        if (!userData.company_name) {
            alert('Укажите название компании для клиента');
            return;
        }
        if (!userData.inn) {
            alert('Укажите ИНН для клиента');
            return;
        }
    } else {
        // Для admin и manager явно указываем null
        userData.company_name = null;
        userData.inn = null;
    }
    
    // Добавление статуса при редактировании
    if (userId) {
        userData.is_active = document.getElementById('userIsActive').value === 'true';
    } else {
        // При создании пользователя отправляем приглашение
        userData.send_invitation = true;
    }
    
    try {
        const url = userId ? `${API_BASE}/users/${userId}` : `${API_BASE}/users`;
        const method = userId ? 'PUT' : 'POST';
        
        console.log('Отправка данных:', userData);
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify(userData)
        });
        
        const result = await response.json();
        console.log('Ответ сервера:', result);
        
        if (!response.ok) {
            // Проверяем наличие деталей валидации
            if (result.detail && Array.isArray(result.detail)) {
                const errors = result.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join('\n');
                throw new Error(`Ошибка валидации:\n${errors}`);
            }
            throw new Error(result.detail || 'Ошибка сохранения пользователя');
        }
        
        // Закрытие модального окна
        closeUserModal();
        
        // Обновление списка пользователей
        await loadUsers();
        
        // Уведомление об успехе
        alert(result.message || 'Пользователь успешно сохранен');
    } catch (error) {
        console.error('Полная ошибка:', error);
        alert(error.message || 'Ошибка сохранения пользователя');
    }
}

// ========== МОДАЛЬНОЕ ОКНО: СМЕНА ПАРОЛЯ ==========

let currentPasswordUserId = null;

async function changeUserPassword(userId) {
    try {
        // Загрузка данных пользователя
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки данных пользователя');
        }
        
        const user = await response.json();
        
        // Сохраняем ID пользователя
        currentPasswordUserId = userId;
        document.getElementById('passwordUserId').value = userId;
        document.getElementById('passwordUserName').textContent = user.full_name || user.email;
        
        // Очистка формы
        document.getElementById('passwordForm').reset();
        
        // Показать модальное окно
        document.getElementById('passwordModalOverlay').style.display = 'flex';
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка загрузки данных пользователя');
    }
}

function closePasswordModal() {
    document.getElementById('passwordModalOverlay').style.display = 'none';
    document.getElementById('passwordForm').reset();
    currentPasswordUserId = null;
}

// Обработчик отправки формы смены пароля
document.addEventListener('DOMContentLoaded', function() {
    // ... существующий код ...
    
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await saveNewPassword();
        });
    }
});

async function saveNewPassword() {
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const userId = currentPasswordUserId;
    
    // Валидация
    if (newPassword.length < 6) {
        alert('Пароль должен содержать минимум 6 символов');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        alert('Пароли не совпадают');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({
                password: newPassword
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Ошибка смены пароля');
        }
        
        // Закрытие модального окна
        closePasswordModal();
        
        // Уведомление об успехе
        alert('Пароль успешно изменен');
    } catch (error) {
        console.error('Ошибка:', error);
        alert(error.message || 'Ошибка смены пароля');
    }
}

function openUserDetails(userId) {
    window.location.href = `/static/user-profile.html?id=${userId}`;
}
