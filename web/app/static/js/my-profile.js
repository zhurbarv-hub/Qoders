// API базовый URL
const API_BASE = '/api';

// Данные текущего пользователя
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
    
    // Загрузка профиля
    loadProfile();
    
    // Обработчики событий
    document.getElementById('sidebarLogoutBtn').addEventListener('click', logout);
    document.getElementById('editProfileBtn').addEventListener('click', showEditProfileDialog);
    document.getElementById('changePasswordBtn').addEventListener('click', showChangePasswordDialog);
    
    // Обработчики форм
    document.getElementById('editProfileForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await saveProfile();
    });
    
    document.getElementById('changePasswordForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await changePassword();
    });
});

// ========== ЗАГРУЗКА ПРОФИЛЯ ==========

async function loadProfile() {
    try {
        const userId = parseInt(currentUser.sub);
        
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки профиля');
        }
        
        const user = await response.json();
        renderProfile(user);
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка загрузки данных профиля');
    }
}

// ========== ОТОБРАЖЕНИЕ ПРОФИЛЯ ==========

function renderProfile(user) {
    // Отображение имени пользователя
    document.getElementById('sidebarUserName').textContent = user.full_name || user.email;
    
    // Заголовок
    document.getElementById('profileName').textContent = user.company_name || user.full_name;
    document.getElementById('profileRole').textContent = getRoleLabel(user.role);
    
    // Основная информация
    document.getElementById('fullName').textContent = user.full_name || '—';
    document.getElementById('email').textContent = user.email || '—';
    document.getElementById('phone').textContent = user.phone || '—';
    document.getElementById('userRole').textContent = getRoleLabel(user.role);
    
    // Дополнительная информация для клиентов
    if (user.role === 'client') {
        document.getElementById('clientInfo').style.display = 'block';
        document.getElementById('companyName').textContent = user.company_name || '—';
        document.getElementById('inn').textContent = user.inn || '—';
    } else {
        document.getElementById('clientInfo').style.display = 'none';
    }
    
    // Telegram интеграция
    if (user.telegram_id) {
        document.getElementById('telegramStatus').innerHTML = '<span style="color: #28a745;">✓ Подключен</span>';
        document.getElementById('telegramUsername').textContent = user.telegram_username ? `@${user.telegram_username}` : '—';
        document.getElementById('telegramName').textContent = `${user.first_name || ''} ${user.last_name || ''}`.trim() || '—';
    } else {
        document.getElementById('telegramStatus').innerHTML = '<span style="color: #dc3545;">✗ Не подключен</span>';
        document.getElementById('telegramUsername').textContent = '—';
        document.getElementById('telegramName').textContent = '—';
    }
    
    // Сохранение данных для редактирования
    window.profileData = user;
}

function getRoleLabel(role) {
    const labels = {
        'admin': 'Администратор',
        'manager': 'Менеджер',
        'client': 'Клиент'
    };
    return labels[role] || role;
}

// ========== РЕДАКТИРОВАНИЕ ПРОФИЛЯ ==========

function showEditProfileDialog() {
    const user = window.profileData;
    
    if (!user) {
        alert('Данные профиля не загружены');
        return;
    }
    
    // Заполнение формы
    document.getElementById('editFullName').value = user.full_name || '';
    document.getElementById('editEmail').value = user.email || '';
    document.getElementById('editPhone').value = user.phone || '';
    
    // Показать модальное окно
    document.getElementById('editProfileModalOverlay').style.display = 'flex';
}

function closeEditProfileModal() {
    document.getElementById('editProfileModalOverlay').style.display = 'none';
    document.getElementById('editProfileForm').reset();
}

async function saveProfile() {
    const userId = parseInt(currentUser.sub);
    
    const userData = {
        full_name: document.getElementById('editFullName').value.trim(),
        email: document.getElementById('editEmail').value.trim(),
        phone: document.getElementById('editPhone').value.trim() || null
    };
    
    if (!userData.full_name) {
        alert('Укажите полное имя');
        return;
    }
    
    if (!userData.email) {
        alert('Укажите email');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify(userData)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Ошибка сохранения профиля');
        }
        
        // Закрытие модального окна
        closeEditProfileModal();
        
        // Обновление профиля
        await loadProfile();
        
        // Уведомление об успехе
        alert('Профиль успешно обновлен');
    } catch (error) {
        console.error('Ошибка:', error);
        alert(error.message || 'Ошибка сохранения профиля');
    }
}

// ========== СМЕНА ПАРОЛЯ ==========

function showChangePasswordDialog() {
    // Очистка формы
    document.getElementById('changePasswordForm').reset();
    
    // Показать модальное окно
    document.getElementById('changePasswordModalOverlay').style.display = 'flex';
}

function closeChangePasswordModal() {
    document.getElementById('changePasswordModalOverlay').style.display = 'none';
    document.getElementById('changePasswordForm').reset();
}

async function changePassword() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPasswordOwn').value;
    const confirmPassword = document.getElementById('confirmPasswordOwn').value;
    
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
        // Сначала проверяем текущий пароль через логин
        const loginResponse = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: currentUser.email,
                password: currentPassword
            })
        });
        
        if (!loginResponse.ok) {
            throw new Error('Неверный текущий пароль');
        }
        
        // Если текущий пароль верный, меняем на новый
        const userId = parseInt(currentUser.sub);
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
        closeChangePasswordModal();
        
        // Уведомление об успехе
        alert('Пароль успешно изменен');
    } catch (error) {
        console.error('Ошибка:', error);
        alert(error.message || 'Ошибка смены пароля');
    }
}

// ========== ВЫХОД ==========

function logout() {
    removeToken();
    window.location.href = '/static/login.html';
}
