// database-management.js - Управление резервными копиями БД
const API_BASE_URL = window.location.origin + '/api';

// Функции для работы с токеном
function getToken() {
    return localStorage.getItem('access_token');
}

function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/static/login.html';
}

// Проверка авторизации при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    // Проверка что пользователь авторизован
    const token = getToken();
    if (!token) {
        window.location.href = '/static/login.html';
        return;
    }

    // Проверка что пользователь - администратор
    const user = getCurrentUser();
    if (!user || user.role !== 'admin') {
        alert('Доступ запрещён. Требуются права администратора.');
        window.location.href = '/static/dashboard.html';
        return;
    }

    // Показать информацию о пользователе
    document.getElementById('userInfo').textContent = `${user.full_name} (${user.role})`;

    // Загрузить список бэкапов
    await loadBackups();

    // Инициализация диалогов
    initDialogs();
});

// Инициализация диалогов
function initDialogs() {
    // Polyfill для dialog если не поддерживается
    if (!window.dialogPolyfill) {
        const dialogs = document.querySelectorAll('dialog');
        dialogs.forEach(dialog => {
            if (!dialog.showModal) {
                dialog.showModal = function() {
                    this.style.display = 'block';
                };
                dialog.close = function() {
                    this.style.display = 'none';
                };
            }
        });
    }
}

// Загрузить список резервных копий
async function loadBackups() {
    try {
        const response = await fetch(`${API_BASE_URL}/database/backups`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (response.status === 401) {
            alert('Сессия истекла. Необходимо войти заново.');
            logout();
            return;
        }

        if (response.ok) {
            const data = await response.json();
            displayBackups(data);
        } else {
            const error = await response.json();
            alert(`Ошибка загрузки списка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка подключения к серверу');
    }
}

// Отобразить список бэкапов
function displayBackups(data) {
    const tbody = document.getElementById('backupsTableBody');
    tbody.innerHTML = '';

    // Обновить статистику
    document.getElementById('totalBackups').textContent = data.total_count;
    document.getElementById('totalSize').textContent = `${data.total_size_mb} МБ`;
    
    if (data.backups.length > 0) {
        const lastBackup = new Date(data.backups[0].created_at);
        document.getElementById('lastBackup').textContent = formatDateTime(lastBackup);
    } else {
        document.getElementById('lastBackup').textContent = 'Нет копий';
    }

    // Заполнить таблицу
    if (data.backups.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Нет резервных копий</td></tr>';
        return;
    }

    data.backups.forEach(backup => {
        const tr = document.createElement('tr');
        
        const createdDate = new Date(backup.created_at);
        
        tr.innerHTML = `
            <td class="mdl-data-table__cell--non-numeric">${backup.filename}</td>
            <td class="mdl-data-table__cell--non-numeric">${formatDateTime(createdDate)}</td>
            <td class="mdl-data-table__cell--non-numeric">${backup.created_by}</td>
            <td>${backup.size_mb}</td>
            <td class="mdl-data-table__cell--non-numeric">${backup.description || '-'}</td>
            <td class="mdl-data-table__cell--non-numeric">
                <button class="mdl-button mdl-js-button mdl-button--icon" onclick="downloadBackup('${backup.filename}')" title="Скачать">
                    <i class="material-icons">download</i>
                </button>
                <button class="mdl-button mdl-js-button mdl-button--icon" onclick="deleteBackup('${backup.filename}')" title="Удалить">
                    <i class="material-icons">delete</i>
                </button>
            </td>
        `;
        
        tbody.appendChild(tr);
    });

    // Обновить выпадающий список для восстановления
    updateRestoreSelect(data.backups);
}

// Обновить список для восстановления
function updateRestoreSelect(backups) {
    const select = document.getElementById('restoreBackupSelect');
    select.innerHTML = '';

    if (backups.length === 0) {
        select.innerHTML = '<option>Нет доступных резервных копий</option>';
        return;
    }

    backups.forEach(backup => {
        const option = document.createElement('option');
        option.value = backup.filename;
        option.textContent = `${backup.filename} (${formatDateTime(new Date(backup.created_at))})`;
        select.appendChild(option);
    });
}

// Форматирование даты и времени
function formatDateTime(date) {
    return date.toLocaleString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Создать резервную копию
function createBackup() {
    const dialog = document.getElementById('createBackupDialog');
    document.getElementById('backupDescription').value = '';
    dialog.showModal();
}

function closeCreateBackupDialog() {
    document.getElementById('createBackupDialog').close();
}

async function confirmCreateBackup() {
    const description = document.getElementById('backupDescription').value.trim();
    
    try {
        const response = await fetch(`${API_BASE_URL}/database/backup?description=${encodeURIComponent(description)}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (response.status === 401) {
            alert('Сессия истекла. Необходимо войти заново.');
            logout();
            return;
        }

        if (response.ok) {
            alert('Резервная копия успешно создана!');
            closeCreateBackupDialog();
            await loadBackups();
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка подключения к серверу');
    }
}

// Скачать резервную копию
function downloadBackup(filename) {
    const url = `${API_BASE_URL}/database/backup/${filename}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    
    // Добавляем токен через заголовок нельзя в обычной ссылке, 
    // поэтому используем fetch
    fetch(url, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Ошибка скачивания файла');
    });
}

// Удалить резервную копию
async function deleteBackup(filename) {
    if (!confirm(`Вы уверены, что хотите удалить резервную копию "${filename}"?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/database/backup/${filename}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (response.ok) {
            alert('Резервная копия успешно удалена');
            await loadBackups();
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка подключения к серверу');
    }
}

// Показать диалог восстановления
function showRestoreDialog() {
    const dialog = document.getElementById('restoreDialog');
    document.getElementById('restorePassword').value = '';
    dialog.showModal();
}

function closeRestoreDialog() {
    document.getElementById('restoreDialog').close();
}

async function confirmRestore() {
    const filename = document.getElementById('restoreBackupSelect').value;
    const password = document.getElementById('restorePassword').value;

    if (!filename || filename === 'Нет доступных резервных копий') {
        alert('Выберите резервную копию');
        return;
    }

    if (!password) {
        alert('Введите пароль администратора');
        return;
    }

    if (!confirm('ВНИМАНИЕ! Все текущие данные будут перезаписаны. Продолжить?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/database/restore`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: filename,
                password: password
            })
        });

        if (response.ok) {
            alert('База данных успешно восстановлена! Страница будет перезагружена.');
            closeRestoreDialog();
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка подключения к серверу');
    }
}

// Показать диалог очистки БД
function showClearDialog() {
    const dialog = document.getElementById('clearDialog');
    document.getElementById('clearConfirmation').value = '';
    document.getElementById('clearPassword').value = '';
    dialog.showModal();
}

function closeClearDialog() {
    document.getElementById('clearDialog').close();
}

async function confirmClear() {
    const confirmation = document.getElementById('clearConfirmation').value;
    const password = document.getElementById('clearPassword').value;

    if (confirmation !== 'УДАЛИТЬ ВСЕ ДАННЫЕ') {
        alert('Введите правильный текст подтверждения: "УДАЛИТЬ ВСЕ ДАННЫЕ"');
        return;
    }

    if (!password) {
        alert('Введите пароль администратора');
        return;
    }

    if (!confirm('ПОСЛЕДНЕЕ ПРЕДУПРЕЖДЕНИЕ! ВСЕ ДАННЫЕ БУДУТ БЕЗВОЗВРАТНО УДАЛЕНЫ! Продолжить?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/database/clear`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                confirmation: confirmation,
                password: password
            })
        });

        if (response.ok) {
            alert('База данных успешно очищена. Все данные удалены!');
            closeClearDialog();
            setTimeout(() => {
                window.location.href = '/static/login.html';
            }, 1000);
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка подключения к серверу');
    }
}
