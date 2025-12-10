// API URL
const API_BASE_URL = 'http://localhost:8000/api';

// Форма входа
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');
    const loginBtn = document.getElementById('loginBtn');
    const spinner = document.getElementById('loadingSpinner');
    
    // Скрыть ошибки
    errorMessage.style.display = 'none';
    
    // Показать загрузку
    loginBtn.disabled = true;
    spinner.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Сохранить токен и данные пользователя
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Перенаправить на дашборд
            window.location.href = '/static/dashboard.html';
        } else {
            const error = await response.json();
            errorMessage.textContent = error.detail || 'Ошибка авторизации';
            errorMessage.style.display = 'block';
        }
    } catch (error) {
        errorMessage.textContent = 'Ошибка подключения к серверу';
        errorMessage.style.display = 'block';
        console.error('Login error:', error);
    } finally {
        loginBtn.disabled = false;
        spinner.style.display = 'none';
    }
});