// Модуль управления дедлайнами

// Загрузка списка дедлайнов
window.loadDeadlinesManage = async function() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadlines`, {
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
            throw new Error('Ошибка загрузки дедлайнов');
        }

        const deadlines = await response.json();
        renderDeadlinesManageTable(deadlines);

    } catch (error) {
        console.error('Ошибка при загрузке дедлайнов:', error);
        showError('Не удалось загрузить список дедлайнов');
    }
};

// Отрисовка таблицы дедлайнов
function renderDeadlinesManageTable(deadlines) {
    const tableBody = document.getElementById('deadlinesManageTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    if (deadlines.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="mdl-data-table__cell--non-numeric" style="text-align: center; padding: 20px;">
                    Нет дедлайнов
                </td>
            </tr>
        `;
        return;
    }

    deadlines.forEach(deadline => {
        const row = document.createElement('tr');
        
        // Форматирование даты
        const expirationDate = new Date(deadline.expiration_date);
        const formattedDate = expirationDate.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });

        // Определение статуса
        let statusText = '';
        let statusColor = '';
        
        switch(deadline.status) {
            case 'active':
                statusText = 'Активен';
                statusColor = '#4CAF50';
                break;
            case 'completed':
                statusText = 'Завершен';
                statusColor = '#2196F3';
                break;
            case 'expired':
                statusText = 'Просрочен';
                statusColor = '#9E9E9E';
                break;
            default:
                statusText = deadline.status;
                statusColor = '#757575';
        }

        row.innerHTML = `
            <td class="mdl-data-table__cell--non-numeric">${deadline.id}</td>
            <td class="mdl-data-table__cell--non-numeric">${deadline.client_name || 'Не указан'}</td>
            <td class="mdl-data-table__cell--non-numeric">${deadline.deadline_type || 'Не указан'}</td>
            <td class="mdl-data-table__cell--non-numeric">${formattedDate}</td>
            <td class="mdl-data-table__cell--non-numeric">
                <span style="background-color: ${statusColor}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">
                    ${statusText}
                </span>
            </td>
            <td class="mdl-data-table__cell--non-numeric">${deadline.notes || '-'}</td>
            <td class="mdl-data-table__cell--non-numeric">
                <div class="action-buttons">
                    <button class="mdl-button mdl-js-button mdl-button--icon mdl-button--colored" 
                            onclick="editDeadline(${deadline.id})" title="Редактировать">
                        <i class="material-icons">edit</i>
                    </button>
                    <button class="mdl-button mdl-js-button mdl-button--icon" 
                            style="color: #f44336;" 
                            onclick="deleteDeadline(${deadline.id})" title="Удалить">
                        <i class="material-icons">delete</i>
                    </button>
                </div>
            </td>
        `;

        tableBody.appendChild(row);
    });
}

// Добавление нового дедлайна
document.addEventListener('DOMContentLoaded', () => {
    const addBtn = document.getElementById('addDeadlineBtn');
    if (addBtn) {
        addBtn.addEventListener('click', showAddDeadlineDialog);
    }
});

async function showAddDeadlineDialog() {
    // Загружаем списки клиентов и типов
    const [clients, types] = await Promise.all([
        loadClientsForSelect(),
        loadTypesForSelect()
    ]);

    const clientsOptions = clients.map(c => `<option value="${c.id}">${c.full_name}</option>`).join('');
    const typesOptions = types.map(t => `<option value="${t.id}">${t.type_name}</option>`).join('');

    const dialogContent = `
        <dialog class="mdl-dialog" id="deadlineDialog" style="width: 500px;">
            <h4 class="mdl-dialog__title">Добавить дедлайн</h4>
            <div class="mdl-dialog__content">
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label" style="width: 100%;">
                    <select class="mdl-textfield__input" id="deadlineClient" required>
                        <option value="">Выберите клиента</option>
                        ${clientsOptions}
                    </select>
                    <label class="mdl-textfield__label" for="deadlineClient">Клиент *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label" style="width: 100%;">
                    <select class="mdl-textfield__input" id="deadlineType" required>
                        <option value="">Выберите тип услуги</option>
                        ${typesOptions}
                    </select>
                    <label class="mdl-textfield__label" for="deadlineType">Тип услуги *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label" style="width: 100%;">
                    <input class="mdl-textfield__input" type="date" id="deadlineExpiration" required>
                    <label class="mdl-textfield__label" for="deadlineExpiration">Дата истечения *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label" style="width: 100%;">
                    <textarea class="mdl-textfield__input" type="text" rows="3" id="deadlineNotes"></textarea>
                    <label class="mdl-textfield__label" for="deadlineNotes">Примечание</label>
                </div>
            </div>
            <div class="mdl-dialog__actions">
                <button type="button" class="mdl-button" onclick="closeDeadlineDialog()">Отмена</button>
                <button type="button" class="mdl-button mdl-button--colored" onclick="saveDeadline()">Сохранить</button>
            </div>
        </dialog>
    `;

    const oldDialog = document.getElementById('deadlineDialog');
    if (oldDialog) oldDialog.remove();

    document.body.insertAdjacentHTML('beforeend', dialogContent);
    
    const dialog = document.getElementById('deadlineDialog');
    if (dialog.showModal) {
        dialog.showModal();
        componentHandler.upgradeDom();
    }
}

async function loadClientsForSelect() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/users`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const users = await response.json();
            return users.filter(u => u.role === 'client' && u.is_active);
        }
    } catch (error) {
        console.error('Ошибка загрузки клиентов:', error);
    }
    return [];
}

async function loadTypesForSelect() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadline-types`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('Ошибка загрузки типов:', error);
    }
    return [];
}

window.closeDeadlineDialog = function() {
    const dialog = document.getElementById('deadlineDialog');
    if (dialog) {
        dialog.close();
        dialog.remove();
    }
};

window.saveDeadline = async function() {
    const clientId = document.getElementById('deadlineClient').value;
    const typeId = document.getElementById('deadlineType').value;
    const expirationDate = document.getElementById('deadlineExpiration').value;
    const notes = document.getElementById('deadlineNotes').value.trim();

    if (!clientId || !typeId || !expirationDate) {
        alert('Заполните обязательные поля: Клиент, Тип услуги, Дата истечения');
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadlines`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: parseInt(clientId),
                deadline_type_id: parseInt(typeId),
                expiration_date: expirationDate,
                notes: notes || null,
                status: 'active'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка при создании дедлайна');
        }

        closeDeadlineDialog();
        loadDeadlinesManage();
        showSuccess('Дедлайн успешно добавлен');

    } catch (error) {
        console.error('Ошибка при создании дедлайна:', error);
        alert('Ошибка: ' + error.message);
    }
};

// Редактирование дедлайна
window.editDeadline = async function(deadlineId) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadlines/${deadlineId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Ошибка загрузки данных дедлайна');

        const deadline = await response.json();
        await showEditDeadlineDialog(deadline);

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось загрузить данные дедлайна');
    }
};

async function showEditDeadlineDialog(deadline) {
    const [clients, types] = await Promise.all([
        loadClientsForSelect(),
        loadTypesForSelect()
    ]);

    const clientsOptions = clients.map(c => 
        `<option value="${c.id}" ${c.id === deadline.user_id ? 'selected' : ''}>${c.full_name}</option>`
    ).join('');
    
    const typesOptions = types.map(t => 
        `<option value="${t.id}" ${t.id === deadline.deadline_type_id ? 'selected' : ''}>${t.type_name}</option>`
    ).join('');

    const statusOptions = `
        <option value="active" ${deadline.status === 'active' ? 'selected' : ''}>Активен</option>
        <option value="completed" ${deadline.status === 'completed' ? 'selected' : ''}>Завершен</option>
        <option value="expired" ${deadline.status === 'expired' ? 'selected' : ''}>Просрочен</option>
    `;

    const dialogContent = `
        <dialog class="mdl-dialog" id="deadlineDialog" style="width: 500px;">
            <h4 class="mdl-dialog__title">Редактировать дедлайн</h4>
            <div class="mdl-dialog__content">
                <input type="hidden" id="deadlineId" value="${deadline.id}">
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label is-dirty" style="width: 100%;">
                    <select class="mdl-textfield__input" id="deadlineClient" required>
                        ${clientsOptions}
                    </select>
                    <label class="mdl-textfield__label" for="deadlineClient">Клиент *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label is-dirty" style="width: 100%;">
                    <select class="mdl-textfield__input" id="deadlineType" required>
                        ${typesOptions}
                    </select>
                    <label class="mdl-textfield__label" for="deadlineType">Тип услуги *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label is-dirty" style="width: 100%;">
                    <input class="mdl-textfield__input" type="date" id="deadlineExpiration" value="${deadline.expiration_date}" required>
                    <label class="mdl-textfield__label" for="deadlineExpiration">Дата истечения *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label is-dirty" style="width: 100%;">
                    <select class="mdl-textfield__input" id="deadlineStatus" required>
                        ${statusOptions}
                    </select>
                    <label class="mdl-textfield__label" for="deadlineStatus">Статус *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label ${deadline.notes ? 'is-dirty' : ''}" style="width: 100%;">
                    <textarea class="mdl-textfield__input" type="text" rows="3" id="deadlineNotes">${deadline.notes || ''}</textarea>
                    <label class="mdl-textfield__label" for="deadlineNotes">Примечание</label>
                </div>
            </div>
            <div class="mdl-dialog__actions">
                <button type="button" class="mdl-button" onclick="closeDeadlineDialog()">Отмена</button>
                <button type="button" class="mdl-button mdl-button--colored" onclick="updateDeadline()">Сохранить</button>
            </div>
        </dialog>
    `;

    const oldDialog = document.getElementById('deadlineDialog');
    if (oldDialog) oldDialog.remove();

    document.body.insertAdjacentHTML('beforeend', dialogContent);
    
    const dialog = document.getElementById('deadlineDialog');
    if (dialog.showModal) {
        dialog.showModal();
        componentHandler.upgradeDom();
    }
}

window.updateDeadline = async function() {
    const deadlineId = document.getElementById('deadlineId').value;
    const clientId = document.getElementById('deadlineClient').value;
    const typeId = document.getElementById('deadlineType').value;
    const expirationDate = document.getElementById('deadlineExpiration').value;
    const status = document.getElementById('deadlineStatus').value;
    const notes = document.getElementById('deadlineNotes').value.trim();

    if (!clientId || !typeId || !expirationDate) {
        alert('Заполните обязательные поля');
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadlines/${deadlineId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: parseInt(clientId),
                deadline_type_id: parseInt(typeId),
                expiration_date: expirationDate,
                status: status,
                notes: notes || null
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка при обновлении дедлайна');
        }

        closeDeadlineDialog();
        loadDeadlinesManage();
        showSuccess('Дедлайн успешно обновлен');

    } catch (error) {
        console.error('Ошибка при обновлении дедлайна:', error);
        alert('Ошибка: ' + error.message);
    }
};

// Удаление дедлайна
window.deleteDeadline = async function(deadlineId) {
    if (!confirm('Вы уверены, что хотите удалить этот дедлайн?')) {
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadlines/${deadlineId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Ошибка при удалении дедлайна');

        loadDeadlinesManage();
        showSuccess('Дедлайн успешно удален');

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось удалить дедлайн');
    }
};

function showSuccess(message) {
    const snackbar = document.getElementById('demo-snackbar');
    if (snackbar && snackbar.MaterialSnackbar) {
        snackbar.MaterialSnackbar.showSnackbar({ message });
    } else {
        alert(message);
    }
}
