/**
 * Управление пользователями системы (менеджеры и администраторы)
 */

// Константы API (если ещё не объявлены)
if (typeof API_BASE_URL === 'undefined') {
    var API_BASE_URL = window.location.origin + '/api';
}

const managersSection = document.getElementById('managers-section');

/**
 * Загрузка списка пользователей
 */
async function loadManagersData() {
    try {
        const token = localStorage.getItem('access_token');
        
        // Загружаем всех пользователей с ролями admin и manager
        const response = await fetch(`${API_BASE_URL}/users?page=1&page_size=50`, {
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
            throw new Error('Ошибка загрузки пользователей');
        }

        const data = await response.json();
        
        // Фильтруем пользователей с ролями admin и manager
        const staffUsers = (data.users || []).filter(u => ['admin', 'manager'].includes(u.role));
        
        renderManagersTable(staffUsers);
        renderManagersPagination(data);
    } catch (error) {
        console.error('Ошибка при загрузке пользователей:', error);
        showManagersError('Не удалось загрузить список пользователей');
    }
}

/**
 * Отображение таблицы пользователей
 */
function renderManagersTable(users) {
    const tableHTML = `
        <div class="section-header">
            <h2>👤 Управление пользователями</h2>
            <button class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" 
                    onclick="showAddManagerModal()">
                <i class="material-icons">add</i> Добавить пользователя
            </button>
        </div>
        <div class="mdl-card mdl-shadow--2dp" style="width: 100%;">
            <table class="mdl-data-table mdl-js-data-table" style="width: 100%;">
                <thead>
                    <tr>
                        <th>ФИО</th>
                        <th>Email</th>
                        <th>Телефон</th>
                        <th>Роль</th>
                        <th>Статус</th>
                        <th>Последний вход</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.length > 0 ? users.map(user => `
                        <tr>
                            <td><strong>${user.full_name || '-'}</strong></td>
                            <td>${user.email || '-'}</td>
                            <td>${user.phone || '-'}</td>
                            <td>
                                <span style="background: ${user.role === 'admin' ? '#667eea' : '#4facfe'}; 
                                             color: white; 
                                             padding: 4px 12px; 
                                             border-radius: 4px; 
                                             font-size: 12px;">
                                    ${getRoleLabel(user.role)}
                                </span>
                            </td>
                            <td>
                                <span style="background: ${user.is_active ? '#d4edda' : '#f8d7da'}; 
                                             color: ${user.is_active ? '#155724' : '#721c24'}; 
                                             padding: 4px 8px; border-radius: 4px;">
                                    ${user.is_active ? 'Активен' : 'Неактивен'}
                                </span>
                            </td>
                            <td>${user.last_login ? formatDateTime(user.last_login) : 'Никогда'}</td>
                            <td>
                                <button class="mdl-button mdl-js-button mdl-button--icon" onclick="viewManager(${user.id})">
                                    <i class="material-icons">visibility</i>
                                </button>
                                <button class="mdl-button mdl-js-button mdl-button--icon" onclick="editManager(${user.id})">
                                    <i class="material-icons">edit</i>
                                </button>
                                <button class="mdl-button mdl-js-button mdl-button--icon" onclick="deleteManager(${user.id})">
                                    <i class="material-icons">delete</i>
                                </button>
                            </td>
                        </tr>
                    `).join('') : `
                        <tr>
                            <td colspan="7" style="text-align: center; padding: 20px;">
                                Пользователи отсутствуют
                            </td>
                        </tr>
                    `}
                </tbody>
            </table>
        </div>
        <div id="managersPagination" style="margin-top: 20px; text-align: center;"></div>
    `;
    
    managersSection.innerHTML = tableHTML;
    
    // Обновляем MDL компоненты
    if (typeof componentHandler !== 'undefined') {
        componentHandler.upgradeDom();
    }
}

/**
 * Получение метки роли
 */
function getRoleLabel(role) {
    const labels = {
        'admin': 'Администратор',
        'manager': 'Менеджер',
        'client': 'Клиент'
    };
    return labels[role] || role;
}

/**
 * Форматирование даты и времени - российский формат ДД.ММ.ГГГГ ЧЧ:ММ
 */
function formatDateTime(dateString) {
    return formatDateTimeRU(dateString);
}

/**
 * Отображение пагинации
 */
function renderManagersPagination(data) {
    const paginationDiv = document.getElementById('managersPagination');
    if (!paginationDiv) return;
    
    const staffCount = (data.users || []).filter(u => ['admin', 'manager'].includes(u.role)).length;
    
    paginationDiv.innerHTML = `
        <p>Показано ${staffCount} пользователей системы</p>
    `;
}

/**
 * Показать ошибку
 */
function showManagersError(message) {
    managersSection.innerHTML = `
        <div class="mdl-card mdl-shadow--2dp" style="width: 100%; padding: 20px;">
            <p style="color: red; text-align: center;">${message}</p>
        </div>
    `;
}

/**
 * Модальное окно добавления пользователя
 */
function showAddManagerModal() {
    const modal = createManagerModal('add');
    document.body.appendChild(modal);
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

/**
 * Просмотр пользователя
 */
function viewManager(id) {
    const token = localStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/users/${id}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(user => {
        const modal = createManagerModal('view', user);
        document.body.appendChild(modal);
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    })
    .catch(error => {
        console.error('Ошибка загрузки пользователя:', error);
        alert('Не удалось загрузить данные пользователя');
    });
}

/**
 * Редактирование пользователя
 */
function editManager(id) {
    const token = localStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/users/${id}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(user => {
        const modal = createManagerModal('edit', user);
        document.body.appendChild(modal);
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    })
    .catch(error => {
        console.error('Ошибка загрузки пользователя:', error);
        alert('Не удалось загрузить данные пользователя');
    });
}

/**
 * Удаление пользователя
 */
async function deleteManager(id) {
    if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/users/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка удаления пользователя');
        }
        
        alert('Пользователь успешно удалён');
        loadManagersData();
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка: ' + error.message);
    }
}

/**
 * Создание модального окна для пользователя
 */
function createManagerModal(mode, user = {}) {
    const isView = mode === 'view';
    const isEdit = mode === 'edit';
    const isAdd = mode === 'add';
    const title = isView ? 'Просмотр пользователя' : isEdit ? 'Редактирование пользователя' : 'Добавить пользователя';
    
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal-overlay';
    modalDiv.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h3>${title}</h3>
                <button class="close-btn" onclick="closeManagerModal(this)">
                    <i class="material-icons">close</i>
                </button>
            </div>
            <div class="modal-body">
                <form id="managerForm" onsubmit="submitManagerForm(event, '${mode}', ${user.id || 'null'})">
                    <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                        <input class="mdl-textfield__input" type="text" id="full_name" value="${user.full_name || ''}" ${isView ? 'disabled' : 'required'}>
                        <label class="mdl-textfield__label" for="full_name">ФИО *</label>
                    </div>
                    
                    <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                        <input class="mdl-textfield__input" type="email" id="email" value="${user.email || ''}" ${isView ? 'disabled' : 'required'}>
                        <label class="mdl-textfield__label" for="email">Email *</label>
                    </div>
                    
                    <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                        <input class="mdl-textfield__input" type="tel" id="phone" value="${user.phone || ''}" ${isView ? 'disabled' : ''}>
                        <label class="mdl-textfield__label" for="phone">Телефон</label>
                    </div>
                    
                    ${!isView ? `
                    <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                        <input class="mdl-textfield__input" type="password" id="password" ${isAdd ? 'required' : ''}>
                        <label class="mdl-textfield__label" for="password">Пароль ${isAdd ? '*' : '(оставьте пустым, чтобы не менять)'}</label>
                    </div>
                    ` : ''}
                    
                    <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                        <select class="mdl-textfield__input" id="role" ${isView ? 'disabled' : 'required'}>
                            <option value="manager" ${user.role === 'manager' ? 'selected' : ''}>Менеджер</option>
                            <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Администратор</option>
                        </select>
                        <label class="mdl-textfield__label" for="role">Роль *</label>
                    </div>
                    
                    <label class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect" for="is_active">
                        <input type="checkbox" id="is_active" class="mdl-checkbox__input" ${user.is_active !== false ? 'checked' : ''} ${isView ? 'disabled' : ''}>
                        <span class="mdl-checkbox__label">Активен</span>
                    </label>
                    
                    ${user.last_login ? `
                    <div class="info-row">
                        <i class="material-icons">schedule</i>
                        <span>Последний вход: ${formatDateTime(user.last_login)}</span>
                    </div>
                    ` : ''}
                    
                    ${user.telegram_id ? `
                    <div class="info-row">
                        <i class="material-icons">telegram</i>
                        <span>Telegram ID: ${user.telegram_id}</span>
                    </div>
                    ` : ''}
                    
                    <div class="modal-footer">
                        <button type="button" class="mdl-button" onclick="closeManagerModal(this)">Закрыть</button>
                        ${!isView ? `<button type="submit" class="mdl-button mdl-button--raised mdl-button--colored">${isEdit ? 'Сохранить' : 'Создать'}</button>` : ''}
                    </div>
                </form>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        if (typeof componentHandler !== 'undefined') {
            componentHandler.upgradeElements(modalDiv.querySelectorAll('.mdl-textfield, .mdl-checkbox'));
        }
    }, 50);
    
    return modalDiv;
}

/**
 * Отправка формы пользователя
 */
async function submitManagerForm(event, mode, userId) {
    event.preventDefault();
    
    const formData = {
        full_name: document.getElementById('full_name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        role: document.getElementById('role').value,
        is_active: document.getElementById('is_active').checked
    };
    
    // Добавляем пароль только если он указан
    const passwordField = document.getElementById('password');
    if (passwordField && passwordField.value) {
        formData.password = passwordField.value;
    }
    
    const token = localStorage.getItem('access_token');
    const url = mode === 'edit' ? `${API_BASE_URL}/users/${userId}` : `${API_BASE_URL}/users`;
    const method = mode === 'edit' ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сохранения');
        }
        
        alert(mode === 'edit' ? 'Пользователь успешно обновлён' : 'Пользователь успешно создан');
        closeManagerModal(event.target);
        loadManagersData();
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка: ' + error.message);
    }
}

/**
 * Закрытие модального окна пользователя
 */
function closeManagerModal(element) {
    const overlay = element.closest('.modal-overlay');
    if (overlay) {
        overlay.querySelector('.modal').classList.remove('show');
        setTimeout(() => overlay.remove(), 300);
    }
}
