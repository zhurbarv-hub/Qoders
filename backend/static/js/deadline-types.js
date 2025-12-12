// Модуль управления типами услуг

// Загрузка списка типов услуг
window.loadDeadlineTypes = async function() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadline-types`, {
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
            throw new Error('Ошибка загрузки типов услуг');
        }

        const types = await response.json();
        renderDeadlineTypesTable(types);

    } catch (error) {
        console.error('Ошибка при загрузке типов услуг:', error);
        showError('Не удалось загрузить список типов услуг');
    }
};

// Отрисовка таблицы типов услуг
function renderDeadlineTypesTable(types) {
    const tableBody = document.getElementById('deadlineTypesTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    if (types.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="mdl-data-table__cell--non-numeric" style="text-align: center; padding: 20px;">
                    Нет типов услуг
                </td>
            </tr>
        `;
        return;
    }

    types.forEach(type => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td class="mdl-data-table__cell--non-numeric">${type.id}</td>
            <td class="mdl-data-table__cell--non-numeric">${type.type_name}</td>
            <td class="mdl-data-table__cell--non-numeric">${type.description || '-'}</td>
            <td class="mdl-data-table__cell--non-numeric">${type.default_period_days || '-'}</td>
            <td class="mdl-data-table__cell--non-numeric">
                <div class="action-buttons">
                    <button class="mdl-button mdl-js-button mdl-button--icon mdl-button--colored" 
                            onclick="editDeadlineType(${type.id})" title="Редактировать">
                        <i class="material-icons">edit</i>
                    </button>
                    <button class="mdl-button mdl-js-button mdl-button--icon" 
                            style="color: #f44336;" 
                            onclick="deleteDeadlineType(${type.id})" title="Удалить">
                        <i class="material-icons">delete</i>
                    </button>
                </div>
            </td>
        `;

        tableBody.appendChild(row);
    });
}

// Добавление нового типа услуги
document.addEventListener('DOMContentLoaded', () => {
    const addBtn = document.getElementById('addDeadlineTypeBtn');
    if (addBtn) {
        addBtn.addEventListener('click', showAddDeadlineTypeDialog);
    }
});

function showAddDeadlineTypeDialog() {
    const dialogContent = `
        <dialog class="mdl-dialog" id="deadlineTypeDialog" style="width: 500px;">
            <h4 class="mdl-dialog__title">Добавить тип услуги</h4>
            <div class="mdl-dialog__content">
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label" style="width: 100%;">
                    <input class="mdl-textfield__input" type="text" id="typeName">
                    <label class="mdl-textfield__label" for="typeName">Название *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label" style="width: 100%;">
                    <textarea class="mdl-textfield__input" type="text" rows="3" id="typeDescription"></textarea>
                    <label class="mdl-textfield__label" for="typeDescription">Описание</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label" style="width: 100%;">
                    <input class="mdl-textfield__input" type="number" id="typePeriod" min="1">
                    <label class="mdl-textfield__label" for="typePeriod">Период (дней)</label>
                </div>
            </div>
            <div class="mdl-dialog__actions">
                <button type="button" class="mdl-button" onclick="closeDeadlineTypeDialog()">Отмена</button>
                <button type="button" class="mdl-button mdl-button--colored" onclick="saveDeadlineType()">Сохранить</button>
            </div>
        </dialog>
    `;

    const oldDialog = document.getElementById('deadlineTypeDialog');
    if (oldDialog) oldDialog.remove();

    document.body.insertAdjacentHTML('beforeend', dialogContent);
    
    const dialog = document.getElementById('deadlineTypeDialog');
    if (dialog.showModal) {
        dialog.showModal();
        componentHandler.upgradeDom();
    }
}

window.closeDeadlineTypeDialog = function() {
    const dialog = document.getElementById('deadlineTypeDialog');
    if (dialog) {
        dialog.close();
        dialog.remove();
    }
};

window.saveDeadlineType = async function() {
    const typeName = document.getElementById('typeName').value.trim();
    const description = document.getElementById('typeDescription').value.trim();
    const period = document.getElementById('typePeriod').value;

    if (!typeName) {
        alert('Заполните обязательное поле: Название');
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadline-types`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type_name: typeName,
                description: description || null,
                default_period_days: period ? parseInt(period) : null
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка при создании типа услуги');
        }

        closeDeadlineTypeDialog();
        loadDeadlineTypes();
        showSuccess('Тип услуги успешно добавлен');

    } catch (error) {
        console.error('Ошибка при создании типа услуги:', error);
        alert('Ошибка: ' + error.message);
    }
};

// Редактирование типа услуги
window.editDeadlineType = async function(typeId) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadline-types/${typeId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Ошибка загрузки данных типа услуги');

        const type = await response.json();
        showEditDeadlineTypeDialog(type);

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось загрузить данные типа услуги');
    }
};

function showEditDeadlineTypeDialog(type) {
    const dialogContent = `
        <dialog class="mdl-dialog" id="deadlineTypeDialog" style="width: 500px;">
            <h4 class="mdl-dialog__title">Редактировать тип услуги</h4>
            <div class="mdl-dialog__content">
                <input type="hidden" id="typeId" value="${type.id}">
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label is-dirty" style="width: 100%;">
                    <input class="mdl-textfield__input" type="text" id="typeName" value="${type.type_name}">
                    <label class="mdl-textfield__label" for="typeName">Название *</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label ${type.description ? 'is-dirty' : ''}" style="width: 100%;">
                    <textarea class="mdl-textfield__input" type="text" rows="3" id="typeDescription">${type.description || ''}</textarea>
                    <label class="mdl-textfield__label" for="typeDescription">Описание</label>
                </div>
                <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label ${type.default_period_days ? 'is-dirty' : ''}" style="width: 100%;">
                    <input class="mdl-textfield__input" type="number" id="typePeriod" min="1" value="${type.default_period_days || ''}">
                    <label class="mdl-textfield__label" for="typePeriod">Период (дней)</label>
                </div>
            </div>
            <div class="mdl-dialog__actions">
                <button type="button" class="mdl-button" onclick="closeDeadlineTypeDialog()">Отмена</button>
                <button type="button" class="mdl-button mdl-button--colored" onclick="updateDeadlineType()">Сохранить</button>
            </div>
        </dialog>
    `;

    const oldDialog = document.getElementById('deadlineTypeDialog');
    if (oldDialog) oldDialog.remove();

    document.body.insertAdjacentHTML('beforeend', dialogContent);
    
    const dialog = document.getElementById('deadlineTypeDialog');
    if (dialog.showModal) {
        dialog.showModal();
        componentHandler.upgradeDom();
    }
}

window.updateDeadlineType = async function() {
    const typeId = document.getElementById('typeId').value;
    const typeName = document.getElementById('typeName').value.trim();
    const description = document.getElementById('typeDescription').value.trim();
    const period = document.getElementById('typePeriod').value;

    if (!typeName) {
        alert('Заполните обязательное поле: Название');
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadline-types/${typeId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type_name: typeName,
                description: description || null,
                default_period_days: period ? parseInt(period) : null
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка при обновлении типа услуги');
        }

        closeDeadlineTypeDialog();
        loadDeadlineTypes();
        showSuccess('Тип услуги успешно обновлен');

    } catch (error) {
        console.error('Ошибка при обновлении типа услуги:', error);
        alert('Ошибка: ' + error.message);
    }
};

// Удаление типа услуги
window.deleteDeadlineType = async function(typeId) {
    if (!confirm('Вы уверены, что хотите удалить этот тип услуги? Это может повлиять на связанные дедлайны.')) {
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadline-types/${typeId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Ошибка при удалении типа услуги');

        loadDeadlineTypes();
        showSuccess('Тип услуги успешно удален');

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось удалить тип услуги');
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
