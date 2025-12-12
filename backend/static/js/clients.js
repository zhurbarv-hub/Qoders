// Модуль управления клиентами

// Загрузка списка клиентов
window.loadClients = async function() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/users`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                handleLogout();
                return;
            }
            throw new Error('Ошибка загрузки клиентов');
        }

        const clients = await response.json();
        renderClientsTable(clients);

    } catch (error) {
        console.error('Ошибка при загрузке клиентов:', error);
        showError('Не удалось загрузить список клиентов');
    }
};

// Отрисовка таблицы клиентов
function renderClientsTable(clients) {
    const tableBody = document.getElementById('clientsTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    // Фильтруем только клиентов (role = 'client')
    const clientsOnly = clients.filter(u => u.role === 'client');

    if (clientsOnly.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="mdl-data-table__cell--non-numeric" style="text-align: center; padding: 20px;">
                    Нет клиентов
                </td>
            </tr>
        `;
        return;
    }

    clientsOnly.forEach(client => {
        const row = document.createElement('tr');
        
        const statusText = client.is_active ? 'Активен' : 'Неактивен';
        const statusColor = client.is_active ? '#4CAF50' : '#9E9E9E';

        row.innerHTML = `
            <td class="mdl-data-table__cell--non-numeric">${client.id}</td>
            <td class="mdl-data-table__cell--non-numeric">${client.full_name || 'Не указано'}</td>
            <td class="mdl-data-table__cell--non-numeric">${client.email || 'Не указан'}</td>
            <td class="mdl-data-table__cell--non-numeric">${client.telegram_id || 'Не привязан'}</td>
            <td class="mdl-data-table__cell--non-numeric">
                <span style="background-color: ${statusColor}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">
                    ${statusText}
                </span>
            </td>
            <td class="mdl-data-table__cell--non-numeric">
                <div class="action-buttons">
                    <button class="mdl-button mdl-js-button mdl-button--icon mdl-button--colored" 
                            onclick="editClient(${client.id})" title="Редактировать">
                        <i class="material-icons">edit</i>
                    </button>
                    <button class="mdl-button mdl-js-button mdl-button--icon" 
                            onclick="toggleClientStatus(${client.id}, ${client.is_active})" 
                            title="${client.is_active ? 'Деактивировать' : 'Активировать'}">
                        <i class="material-icons">${client.is_active ? 'block' : 'check_circle'}</i>
                    </button>
                    <button class="mdl-button mdl-js-button mdl-button--icon" 
                            style="color: #f44336;" 
                            onclick="deleteClient(${client.id})" title="Удалить">
                        <i class="material-icons">delete</i>
                    </button>
                </div>
            </td>
        `;

        tableBody.appendChild(row);
    });
}

// Добавление нового клиента
document.addEventListener('DOMContentLoaded', () => {
    const addBtn = document.getElementById('addClientBtn');
    if (addBtn) {
        addBtn.addEventListener('click', showAddClientDialog);
    }
});

function showAddClientDialog() {
    const dialogContent = `
        <dialog class="mdl-dialog" id="clientDialog">
            <h4 class="mdl-dialog__title">Добавить клиента</h4>
            <div class="mdl-dialog__content">
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                    <input class="mdl-textfield__input" type="text" id="clientUsername">
                    <label class="mdl-textfield__label" for="clientUsername">Логин *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                    <input class="mdl-textfield__input" type="text" id="clientFullName">
                    <label class="mdl-textfield__label" for="clientFullName">ФИО *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                    <input class="mdl-textfield__input" type="email" id="clientEmail">
                    <label class="mdl-textfield__label" for="clientEmail">Email</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                    <input class="mdl-textfield__input" type="password" id="clientPassword">
                    <label class="mdl-textfield__label" for="clientPassword">Пароль *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                    <input class="mdl-textfield__input" type="text" id="clientTelegram">
                    <label class="mdl-textfield__label" for="clientTelegram">Telegram ID</label>
                </div>
            </div>
            <div class="mdl-dialog__actions">
                <button type="button" class="mdl-button" onclick="closeClientDialog()">Отмена</button>
                <button type="button" class="mdl-button mdl-button--colored" onclick="saveClient()">Сохранить</button>
            </div>
        </dialog>
    `;

    // Удаляем старый диалог если есть
    const oldDialog = document.getElementById('clientDialog');
    if (oldDialog) oldDialog.remove();

    // Добавляем новый
    document.body.insertAdjacentHTML('beforeend', dialogContent);
    
    const dialog = document.getElementById('clientDialog');
    if (dialog.showModal) {
        dialog.showModal();
        // Инициализация MDL компонентов
        componentHandler.upgradeDom();
    }
}

window.closeClientDialog = function() {
    const dialog = document.getElementById('clientDialog');
    if (dialog) {
        dialog.close();
        dialog.remove();
    }
};

window.saveClient = async function() {
    const username = document.getElementById('clientUsername').value.trim();
    const fullName = document.getElementById('clientFullName').value.trim();
    const email = document.getElementById('clientEmail').value.trim();
    const password = document.getElementById('clientPassword').value;
    const telegramId = document.getElementById('clientTelegram').value.trim();

    if (!username || !fullName || !password) {
        alert('Заполните обязательные поля: Логин, ФИО, Пароль');
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password,
                full_name: fullName,
                email: email || null,
                telegram_id: telegramId || null,
                role: 'client',
                is_active: true
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка при создании клиента');
        }

        closeClientDialog();
        loadClients();
        showSuccess('Клиент успешно добавлен');

    } catch (error) {
        console.error('Ошибка при создании клиента:', error);
        alert('Ошибка: ' + error.message);
    }
};

// Редактирование клиента
window.editClient = async function(clientId) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/users/${clientId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Ошибка загрузки данных клиента');

        const client = await response.json();
        showEditClientDialog(client);

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось загрузить данные клиента');
    }
};

function showEditClientDialog(client) {
    const dialogContent = `
        <dialog class="mdl-dialog" id="clientDialog">
            <h4 class="mdl-dialog__title">Редактировать клиента</h4>
            <div class="mdl-dialog__content">
                <input type="hidden" id="clientId" value="${client.id}">
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label is-dirty">
                    <input class="mdl-textfield__input" type="text" id="clientUsername" value="${client.username}">
                    <label class="mdl-textfield__label" for="clientUsername">Логин *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label ${client.full_name ? 'is-dirty' : ''}">
                    <input class="mdl-textfield__input" type="text" id="clientFullName" value="${client.full_name || ''}">
                    <label class="mdl-textfield__label" for="clientFullName">ФИО *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label ${client.email ? 'is-dirty' : ''}">
                    <input class="mdl-textfield__input" type="email" id="clientEmail" value="${client.email || ''}">
                    <label class="mdl-textfield__label" for="clientEmail">Email</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                    <input class="mdl-textfield__input" type="password" id="clientPassword" placeholder="Оставьте пустым чтобы не менять">
                    <label class="mdl-textfield__label" for="clientPassword">Новый пароль</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label ${client.telegram_id ? 'is-dirty' : ''}">
                    <input class="mdl-textfield__input" type="text" id="clientTelegram" value="${client.telegram_id || ''}">
                    <label class="mdl-textfield__label" for="clientTelegram">Telegram ID</label>
                </div>
            </div>
            <div class="mdl-dialog__actions">
                <button type="button" class="mdl-button" onclick="closeClientDialog()">Отмена</button>
                <button type="button" class="mdl-button mdl-button--colored" onclick="updateClient()">Сохранить</button>
            </div>
        </dialog>
    `;

    const oldDialog = document.getElementById('clientDialog');
    if (oldDialog) oldDialog.remove();

    document.body.insertAdjacentHTML('beforeend', dialogContent);
    
    const dialog = document.getElementById('clientDialog');
    if (dialog.showModal) {
        dialog.showModal();
        componentHandler.upgradeDom();
    }
}

window.updateClient = async function() {
    const clientId = document.getElementById('clientId').value;
    const username = document.getElementById('clientUsername').value.trim();
    const fullName = document.getElementById('clientFullName').value.trim();
    const email = document.getElementById('clientEmail').value.trim();
    const password = document.getElementById('clientPassword').value;
    const telegramId = document.getElementById('clientTelegram').value.trim();

    if (!username || !fullName) {
        alert('Заполните обязательные поля: Логин, ФИО');
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const body = {
            username: username,
            full_name: fullName,
            email: email || null,
            telegram_id: telegramId || null
        };

        // Добавляем пароль только если он указан
        if (password) {
            body.password = password;
        }

        const response = await fetch(`${API_BASE_URL}/users/${clientId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка при обновлении клиента');
        }

        closeClientDialog();
        loadClients();
        showSuccess('Клиент успешно обновлен');

    } catch (error) {
        console.error('Ошибка при обновлении клиента:', error);
        alert('Ошибка: ' + error.message);
    }
};

// Переключение статуса клиента
window.toggleClientStatus = async function(clientId, currentStatus) {
    const action = currentStatus ? 'деактивировать' : 'активировать';
    if (!confirm(`Вы уверены, что хотите ${action} этого клиента?`)) {
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/users/${clientId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                is_active: !currentStatus
            })
        });

        if (!response.ok) throw new Error('Ошибка при изменении статуса');

        loadClients();
        showSuccess(`Клиент успешно ${currentStatus ? 'деактивирован' : 'активирован'}`);

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось изменить статус клиента');
    }
};

// Удаление клиента
window.deleteClient = async function(clientId) {
    if (!confirm('Вы уверены, что хотите удалить этого клиента? Это действие необратимо.')) {
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/users/${clientId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Ошибка при удалении клиента');

        loadClients();
        showSuccess('Клиент успешно удален');

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось удалить клиента');
    }
};

// Вспомогательная функция для отображения успешного сообщения
function showSuccess(message) {
    const snackbar = document.getElementById('demo-snackbar');
    if (snackbar && snackbar.MaterialSnackbar) {
        snackbar.MaterialSnackbar.showSnackbar({ message });
    } else {
        alert(message);
    }
}
