// Модуль экспорта данных

// Инициализация обработчиков экспорта
document.addEventListener('DOMContentLoaded', () => {
    const exportClientsBtn = document.getElementById('exportClientsBtn');
    const exportDeadlinesBtn = document.getElementById('exportDeadlinesBtn');

    if (exportClientsBtn) {
        exportClientsBtn.addEventListener('click', exportClients);
    }

    if (exportDeadlinesBtn) {
        exportDeadlinesBtn.addEventListener('click', exportDeadlines);
    }
});

// Экспорт клиентов в Excel
async function exportClients() {
    try {
        const token = localStorage.getItem('access_token');
        
        // Показываем индикатор загрузки
        showLoading('Экспорт клиентов...');
        
        const response = await fetch(`${API_BASE_URL}/export/clients`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        hideLoading();

        if (!response.ok) {
            if (response.status === 401) {
                handleLogout();
                return;
            }
            throw new Error('Ошибка при экспорте клиентов');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `clients_${getCurrentDate()}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showSuccess('Клиенты успешно экспортированы');

    } catch (error) {
        hideLoading();
        console.error('Ошибка при экспорте клиентов:', error);
        
        // Если API не поддерживает экспорт, делаем локально
        await exportClientsLocal();
    }
}

// Локальный экспорт клиентов (если нет API)
async function exportClientsLocal() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/users`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Ошибка загрузки данных');

        const users = await response.json();
        const clients = users.filter(u => u.role === 'client');

        // Конвертируем в CSV
        const csv = convertToCSV(clients, [
            { key: 'id', header: 'ID' },
            { key: 'username', header: 'Логин' },
            { key: 'full_name', header: 'ФИО' },
            { key: 'email', header: 'Email' },
            { key: 'telegram_id', header: 'Telegram ID' },
            { key: 'is_active', header: 'Активен' }
        ]);

        downloadCSV(csv, `clients_${getCurrentDate()}.csv`);
        showSuccess('Клиенты экспортированы в CSV');

    } catch (error) {
        console.error('Ошибка локального экспорта:', error);
        alert('Не удалось экспортировать клиентов');
    }
}

// Экспорт дедлайнов в Excel
async function exportDeadlines() {
    try {
        const token = localStorage.getItem('access_token');
        
        showLoading('Экспорт дедлайнов...');
        
        const response = await fetch(`${API_BASE_URL}/export/deadlines`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        hideLoading();

        if (!response.ok) {
            if (response.status === 401) {
                handleLogout();
                return;
            }
            throw new Error('Ошибка при экспорте дедлайнов');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `deadlines_${getCurrentDate()}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showSuccess('Дедлайны успешно экспортированы');

    } catch (error) {
        hideLoading();
        console.error('Ошибка при экспорте дедлайнов:', error);
        
        // Если API не поддерживает экспорт, делаем локально
        await exportDeadlinesLocal();
    }
}

// Локальный экспорт дедлайнов (если нет API)
async function exportDeadlinesLocal() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadlines`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Ошибка загрузки данных');

        const deadlines = await response.json();

        // Конвертируем в CSV
        const csv = convertToCSV(deadlines, [
            { key: 'id', header: 'ID' },
            { key: 'client_name', header: 'Клиент' },
            { key: 'deadline_type', header: 'Тип услуги' },
            { key: 'expiration_date', header: 'Дата истечения' },
            { key: 'status', header: 'Статус' },
            { key: 'notes', header: 'Примечание' },
            { key: 'days_remaining', header: 'Осталось дней' }
        ]);

        downloadCSV(csv, `deadlines_${getCurrentDate()}.csv`);
        showSuccess('Дедлайны экспортированы в CSV');

    } catch (error) {
        console.error('Ошибка локального экспорта:', error);
        alert('Не удалось экспортировать дедлайны');
    }
}

// Конвертация данных в CSV формат
function convertToCSV(data, columns) {
    if (!data || data.length === 0) {
        return '';
    }

    // Заголовки
    const headers = columns.map(col => col.header).join(',');
    
    // Строки данных
    const rows = data.map(item => {
        return columns.map(col => {
            let value = item[col.key];
            
            // Обработка специальных значений
            if (value === null || value === undefined) {
                value = '';
            } else if (typeof value === 'boolean') {
                value = value ? 'Да' : 'Нет';
            } else if (typeof value === 'string') {
                // Экранирование запятых и кавычек
                value = `"${value.replace(/"/g, '""')}"`;
            }
            
            return value;
        }).join(',');
    });

    return headers + '\n' + rows.join('\n');
}

// Скачивание CSV файла
function downloadCSV(csvContent, filename) {
    // Добавляем BOM для правильной кодировки UTF-8 в Excel
    const BOM = '\uFEFF';
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Получение текущей даты в формате YYYY-MM-DD
function getCurrentDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Показать индикатор загрузки
function showLoading(message) {
    const loadingHtml = `
        <div id="exportLoading" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 8px;
                text-align: center;
            ">
                <div class="mdl-spinner mdl-js-spinner is-active"></div>
                <p style="margin-top: 20px; font-size: 16px;">${message}</p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', loadingHtml);
    componentHandler.upgradeDom();
}

// Скрыть индикатор загрузки
function hideLoading() {
    const loading = document.getElementById('exportLoading');
    if (loading) {
        loading.remove();
    }
}

// Вспомогательные функции
function showSuccess(message) {
    const snackbar = document.getElementById('demo-snackbar');
    if (snackbar && snackbar.MaterialSnackbar) {
        snackbar.MaterialSnackbar.showSnackbar({ message });
    } else {
        alert(message);
    }
}

function showError(message) {
    const snackbar = document.getElementById('demo-snackbar');
    if (snackbar && snackbar.MaterialSnackbar) {
        snackbar.MaterialSnackbar.showSnackbar({ message });
    } else {
        alert(message);
    }
}
