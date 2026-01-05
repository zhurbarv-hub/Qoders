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
    
    // Загрузить настройки автобэкапа
    await loadBackupSchedule();

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
    console.log('📊 displayBackups: Получены данные:', data);
    
    const tbody = document.getElementById('backupsTableBody');
    tbody.innerHTML = '';

    // Обновить статистику
    const totalBackups = document.getElementById('totalBackups');
    const totalSize = document.getElementById('totalSize');
    const lastBackup = document.getElementById('lastBackup');
    
    console.log('📈 Элементы:', {
        totalBackups: totalBackups ? 'found' : 'NOT FOUND',
        totalSize: totalSize ? 'found' : 'NOT FOUND',
        lastBackup: lastBackup ? 'found' : 'NOT FOUND'
    });
    
    if (totalBackups) totalBackups.textContent = data.total_count || 0;
    if (totalSize) totalSize.textContent = `${data.total_size_mb || 0} МБ`;
    
    if (data.backups && data.backups.length > 0) {
        const lastBackupDate = new Date(data.backups[0].created_at);
        if (lastBackup) lastBackup.textContent = formatDateTime(lastBackupDate);
    } else {
        if (lastBackup) lastBackup.textContent = 'Нет копий';
    }

    // Заполнить таблицу
    if (!data.backups || data.backups.length === 0) {
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

    // Закрыть диалог выбора и показать прогресс
    closeRestoreDialog();
    
    const progressDialog = document.getElementById('restoreProgressDialog');
    const progressText = document.getElementById('restoreProgressText');
    const progressBar = document.getElementById('restoreProgress');
    
    progressDialog.showModal();
    
    // Инициализировать MDL прогресс-бар
    if (typeof componentHandler !== 'undefined') {
        componentHandler.upgradeElement(progressBar);
    }

    try {
        progressText.textContent = '🔒 Проверка пароля...';
        
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
            progressText.textContent = '✅ База данных успешно восстановлена!';
            
            // Подождать 2 секунды и перезагрузить
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            const error = await response.json();
            progressDialog.close();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        progressDialog.close();
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

// ========== ФУНКЦИИ АВТОМАТИЧЕСКОГО БЭКАПА ==========

// Загрузить настройки автобэкапа
async function loadBackupSchedule() {
    try {
        const response = await fetch(`${API_BASE_URL}/database/backup-schedule`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (response.status === 401) {
            logout();
            return;
        }

        if (response.ok) {
            const schedule = await response.json();
            displayBackupSchedule(schedule);
        } else {
            console.error('Ошибка загрузки расписания');
        }
    } catch (error) {
        console.error('Ошибка загрузки расписания:', error);
    }
}

// Отобразить настройки расписания
function displayBackupSchedule(schedule) {
    const enabledCheckbox = document.getElementById('autoBackupEnabled');
    enabledCheckbox.checked = schedule.enabled;
    
    // Обновить визуальное состояние MDL переключателя
    const switchParent = enabledCheckbox.parentElement;
    if (schedule.enabled) {
        switchParent.classList.add('is-checked');
    } else {
        switchParent.classList.remove('is-checked');
    }
    
    const settingsDiv = document.getElementById('autoBackupSettings');
    settingsDiv.style.display = schedule.enabled ? 'block' : 'none';
    
    const statusDiv = document.getElementById('autoBackupStatus');
    if (schedule.enabled) {
        statusDiv.innerHTML = '<span style="color: #4caf50;">✅ Автобэкап включён</span>';
    } else {
        statusDiv.innerHTML = '<span style="color: #999;">⏸️ Автобэкап отключён</span>';
    }
    
    document.getElementById('backupFrequency').value = schedule.frequency;
    
    const timeParts = schedule.time_of_day.split(':');
    document.getElementById('backupTime').value = `${timeParts[0]}:${timeParts[1]}`;
    
    if (schedule.day_of_week !== null) {
        document.getElementById('dayOfWeek').value = schedule.day_of_week;
    }
    
    if (schedule.day_of_month !== null) {
        document.getElementById('dayOfMonth').value = schedule.day_of_month;
    }
    
    document.getElementById('retentionDays').value = schedule.retention_days;
    
    updateFrequencyFields();
    
    if (schedule.last_run_at) {
        document.getElementById('lastRunTime').textContent = formatDateTime(new Date(schedule.last_run_at));
    } else {
        document.getElementById('lastRunTime').textContent = 'Не выполнялся';
    }
    
    if (schedule.next_run_at) {
        document.getElementById('nextRunTime').textContent = formatDateTime(new Date(schedule.next_run_at));
    } else {
        document.getElementById('nextRunTime').textContent = 'Не запланирован';
    }
}

// Переключение автобэкапа
async function toggleAutoBackup(enabled) {
    const settingsDiv = document.getElementById('autoBackupSettings');
    settingsDiv.style.display = enabled ? 'block' : 'none';
    await updateBackupSchedule({ enabled });
}

// Обновление видимости полей
function updateFrequencyFields() {
    const frequency = document.getElementById('backupFrequency').value;
    const dayOfWeekField = document.getElementById('dayOfWeekField');
    const dayOfMonthField = document.getElementById('dayOfMonthField');
    
    dayOfWeekField.style.display = 'none';
    dayOfMonthField.style.display = 'none';
    
    if (frequency === 'weekly') {
        dayOfWeekField.style.display = 'block';
    } else if (frequency === 'monthly') {
        dayOfMonthField.style.display = 'block';
    }
}

// Сохранить настройки расписания
async function saveBackupSchedule() {
    const frequency = document.getElementById('backupFrequency').value;
    const time = document.getElementById('backupTime').value;
    const retentionDays = parseInt(document.getElementById('retentionDays').value);
    
    const data = {
        frequency,
        time_of_day: time,
        retention_days: retentionDays
    };
    
    if (frequency === 'weekly') {
        data.day_of_week = parseInt(document.getElementById('dayOfWeek').value);
        data.day_of_month = null;
    } else if (frequency === 'monthly') {
        data.day_of_month = parseInt(document.getElementById('dayOfMonth').value);
        data.day_of_week = null;
    } else {
        data.day_of_week = null;
        data.day_of_month = null;
    }
    
    await updateBackupSchedule(data);
}

// Обновить расписание на сервере
async function updateBackupSchedule(data) {
    try {
        const response = await fetch(`${API_BASE_URL}/database/backup-schedule`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify(data)
        });

        if (response.status === 401) {
            logout();
            return;
        }

        if (response.ok) {
            const schedule = await response.json();
            displayBackupSchedule(schedule);
            alert('Настройки автобэкапа успешно сохранены!');
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка подключения к серверу');
    }
}
