// Константы API
const API_BASE_URL = 'http://localhost:8001/api';

// Получение токена из URL
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

// Элементы страницы
const validationBlock = document.getElementById('validationBlock');
const passwordBlock = document.getElementById('passwordBlock');
const successBlock = document.getElementById('successBlock');
const errorBlock = document.getElementById('errorBlock');
const errorText = document.getElementById('errorText');
const welcomeMessage = document.getElementById('welcomeMessage');
const activateForm = document.getElementById('activateForm');
const errorMessage = document.getElementById('errorMessage');
const submitBtn = document.getElementById('submitBtn');

// Проверка наличия токена
if (!token) {
    showError('Токен активации отсутствует в ссылке.');
} else {
    validateToken();
}

// Валидация токена на сервере
async function validateToken() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/validate-activation-token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token })
        });

        const data = await response.json();

        if (response.ok) {
            // Токен валиден, показываем форму установки пароля
            validationBlock.style.display = 'none';
            passwordBlock.style.display = 'block';
            
            if (data.user) {
                welcomeMessage.textContent = `Добро пожаловать, ${data.user.full_name}! Установите пароль для входа в систему.`;
            }
        } else {
            // Ошибка валидации
            showError(data.detail || 'Ссылка активации недействительна или истекла.');
        }
    } catch (error) {
        console.error('Ошибка валидации токена:', error);
        showError('Произошла ошибка при проверке токена. Попробуйте позже.');
    }
}

// Обработка отправки формы
activateForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const password = document.getElementById('password').value;
    const passwordConfirm = document.getElementById('passwordConfirm').value;
    
    // Валидация
    if (password.length < 6) {
        showFormError('Пароль должен содержать минимум 6 символов');
        return;
    }
    
    if (password !== passwordConfirm) {
        showFormError('Пароли не совпадают');
        return;
    }
    
    // Отключаем кнопку
    submitBtn.disabled = true;
    submitBtn.textContent = 'Активация...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/set-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: token,
                password: password,
                password_confirm: passwordConfirm
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Успешная активация
            passwordBlock.style.display = 'none';
            successBlock.style.display = 'block';
            
            // Перенаправление через 3 секунды
            setTimeout(() => {
                window.location.href = '/login.html';
            }, 3000);
        } else {
            // Ошибка активации
            submitBtn.disabled = false;
            submitBtn.textContent = 'Активировать аккаунт';
            showFormError(data.detail || 'Не удалось активировать аккаунт');
        }
    } catch (error) {
        console.error('Ошибка активации:', error);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Активировать аккаунт';
        showFormError('Произошла ошибка при активации. Попробуйте позже.');
    }
});

// Показать ошибку в форме
function showFormError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    
    // Скрыть через 5 секунд
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

// Показать блок ошибки
function showError(message) {
    validationBlock.style.display = 'none';
    passwordBlock.style.display = 'none';
    errorBlock.style.display = 'block';
    errorText.textContent = message;
}
