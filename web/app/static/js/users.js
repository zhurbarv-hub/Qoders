// Константы API (если ещё не объявлены)
if (typeof API_BASE_URL === 'undefined') {
    var API_BASE_URL = window.location.origin + '/api';
}

const usersSection = document.getElementById('users-section');

// Глобальная переменная для хранения состояния фильтра
let showInactiveUsers = false;

// Загрузка данных клиентов
async function loadUsersData() {
    try {
        const token = localStorage.getItem('access_token');
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        
        // Формируем параметр фильтра по активности
        const isActiveParam = showInactiveUsers ? '' : '&is_active=true';
        
        const response = await fetch(`${API_BASE_URL}/users?role=client&page=1&page_size=50${isActiveParam}`, {
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

        const data = await response.json();
        renderUsersTable(data.users || []);
        renderUsersPagination(data);
        
    } catch (error) {
        console.error('Ошибка при загрузке клиентов:', error);
        showUsersError('Не удалось загрузить список клиентов');
    }
}

// Переключение отображения неактивных пользователей
function toggleShowInactive() {
    showInactiveUsers = !showInactiveUsers;
    loadUsersData();
}

// Отрисовка таблицы клиентов
function renderUsersTable(users) {
    const usersSection = document.getElementById('users-section');
    if (!usersSection) return;
    
    const tableHTML = `
        <div class="section-header">
            <h2>👥 Управление клиентами</h2>
            <button class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" onclick="showAddUserModal()">
                <i class="material-icons">add</i> Добавить клиента
            </button>
        </div>
        
        <div style="padding: 10px 0; margin-bottom: 10px;">
            <label class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect" for="show-inactive-checkbox">
                <input type="checkbox" id="show-inactive-checkbox" class="mdl-checkbox__input" 
                       ${showInactiveUsers ? 'checked' : ''} onchange="toggleShowInactive()">
                <span class="mdl-checkbox__label">Показать неактивных клиентов</span>
            </label>
        </div>
        
        <div class="mdl-card mdl-shadow--2dp" style="width: 100%;">
            <div class="mdl-card__supporting-text" style="padding: 0; overflow-x: auto;">
                <table class="mdl-data-table mdl-js-data-table" style="width: 100%;">
                    <thead>
                        <tr>
                            <th class="mdl-data-table__cell--non-numeric">Компания</th>
                            <th class="mdl-data-table__cell--non-numeric">ИНН</th>
                            <th class="mdl-data-table__cell--non-numeric">Контактное лицо</th>
                            <th class="mdl-data-table__cell--non-numeric">Email</th>
                            <th class="mdl-data-table__cell--non-numeric">Телефон</th>
                            <th class="mdl-data-table__cell--non-numeric">Telegram</th>
                            <th class="mdl-data-table__cell--non-numeric">Статус</th>
                            <th class="mdl-data-table__cell--non-numeric">Действия</th>
                        </tr>
                    </thead>
                    <tbody id="users-table-body">
                        ${users.length === 0 ? `
                            <tr>
                                <td colspan="8" style="text-align: center; padding: 20px;">
                                    Клиенты не найдены
                                </td>
                            </tr>
                        ` : users.map(user => `
                            <tr>
                                <td class="mdl-data-table__cell--non-numeric">${user.company_name || '-'}</td>
                                <td class="mdl-data-table__cell--non-numeric">${user.inn || '-'}</td>
                                <td class="mdl-data-table__cell--non-numeric">${user.full_name || '-'}</td>
                                <td class="mdl-data-table__cell--non-numeric">${user.email || '-'}</td>
                                <td class="mdl-data-table__cell--non-numeric">${user.phone || '-'}</td>
                                <td class="mdl-data-table__cell--non-numeric">
                                    ${user.telegram_id ? '✅ Подключен' : '❌ Не подключен'}
                                </td>
                                <td class="mdl-data-table__cell--non-numeric">
                                    <span style="color: ${user.is_active ? '#4CAF50' : '#999'};">
                                        ${user.is_active ? 'Активен' : 'Неактивен'}
                                    </span>
                                </td>
                                <td class="mdl-data-table__cell--non-numeric">
                                    ${user.is_active ? `
                                        <button class="mdl-button mdl-js-button mdl-button--icon" 
                                                onclick="toggleUserStatus(${user.id}, '${(user.company_name || user.full_name || '').replace(/'/g, "\\'")}')"
                                                title="Деактивировать" style="color: #ff9800;">
                                            <i class="material-icons">block</i>
                                        </button>
                                    ` : `
                                        <button class="mdl-button mdl-js-button mdl-button--icon" 
                                                onclick="toggleUserStatus(${user.id}, '${(user.company_name || user.full_name || '').replace(/'/g, "\\'")}')"
                                                title="Активировать" style="color: #4CAF50;">
                                            <i class="material-icons">check_circle</i>
                                        </button>
                                    `}
                                    <button class="mdl-button mdl-js-button mdl-button--icon" onclick="deleteUser(${user.id}, '${(user.company_name || user.full_name || '').replace(/'/g, "\\'")}')"
                                            title="Удалить" style="color: #f44336;" ${!user.is_active ? 'disabled' : ''}>
                                        <i class="material-icons">delete</i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
        <div id="users-pagination"></div>
    `;
    
    usersSection.innerHTML = tableHTML;
    
    // Добавление обработчиков клика на строки таблицы
    setTimeout(() => {
        const tableRows = document.querySelectorAll('#users-table-body tr');
        tableRows.forEach((row, index) => {
            if (users[index]) {
                row.style.cursor = 'pointer';
                row.addEventListener('click', function(e) {
                    // Проверяем, что клик не по кнопке действия
                    if (!e.target.closest('button') && !e.target.closest('.mdl-button')) {
                        viewUserDetails(users[index].id);
                    }
                });
            }
        });
    }, 100);
    
    // Инициализация MDL компонентов
    if (typeof componentHandler !== 'undefined') {
        componentHandler.upgradeDom();
    }
}

// Отрисовка пагинации
function renderUsersPagination(data) {
    const paginationDiv = document.getElementById('users-pagination');
    if (!paginationDiv || !data.total_pages) return;
    
    paginationDiv.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <p>Страница ${data.page} из ${data.total_pages} (Всего: ${data.total})</p>
        </div>
    `;
}

// Функции для работы с клиентами
function viewUserDetails(userId) {
    // Переход на страницу деталей клиента с кассами и дедлайнами
    window.location.href = `/static/client-details.html?id=${userId}`;
}

function showAddUserModal() {
    const modal = createUserModal('add');
    document.body.appendChild(modal);
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

function viewUser(userId) {
    // Загрузка данных клиента
    const token = localStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/users/${userId}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(user => {
        const modal = createUserModal('view', user);
        document.body.appendChild(modal);
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    })
    .catch(error => {
        console.error('Ошибка загрузки клиента:', error);
        alert('Не удалось загрузить данные клиента');
    });
}

function editUser(userId) {
    const token = localStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/users/${userId}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(user => {
        const modal = createUserModal('edit', user);
        document.body.appendChild(modal);
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    })
    .catch(error => {
        console.error('Ошибка загрузки клиента:', error);
        alert('Не удалось загрузить данные клиента');
    });
}

// Создание модального окна для клиента
function createUserModal(mode, user = {}) {
    const isView = mode === 'view';
    const isEdit = mode === 'edit';
    const isAdd = mode === 'add';
    const title = isView ? 'Просмотр клиента' : isEdit ? 'Редактирование клиента' : 'Добавить клиента';
    
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal-overlay';
    modalDiv.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h3>${title}</h3>
                <button class="close-btn" onclick="closeUserModal(this)">
                    <i class="material-icons">close</i>
                </button>
            </div>
            <div class="modal-body">
                <form id="userForm" onsubmit="submitUserForm(event, '${mode}', ${user.id || 'null'})">
                    <div class="form-row">
                        <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                            <input class="mdl-textfield__input" type="text" id="company_name" 
                                   value="${user.company_name || ''}" ${isView ? 'disabled' : 'required'}>
                            <label class="mdl-textfield__label" for="company_name">Название компании *</label>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                            <input class="mdl-textfield__input" type="text" id="inn" pattern="[0-9]{10,12}"
                                   value="${user.inn || ''}" ${isView ? 'disabled' : 'required'}>
                            <label class="mdl-textfield__label" for="inn">ИНН (10 или 12 цифр) *</label>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                            <input class="mdl-textfield__input" type="text" id="full_name"
                                   value="${user.full_name || ''}" ${isView ? 'disabled' : ''}>
                            <label class="mdl-textfield__label" for="full_name">Контактное лицо</label>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                            <input class="mdl-textfield__input" type="email" id="email"
                                   value="${user.email || ''}" ${isView ? 'disabled' : 'required'}>
                            <label class="mdl-textfield__label" for="email">Email *</label>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                            <input class="mdl-textfield__input" type="tel" id="phone"
                                   value="${user.phone || ''}" ${isView ? 'disabled' : ''}>
                            <label class="mdl-textfield__label" for="phone">Телефон</label>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                            <textarea class="mdl-textfield__input" id="address" rows="2" ${isView ? 'disabled' : ''}>${user.address || ''}</textarea>
                            <label class="mdl-textfield__label" for="address">Адрес</label>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label">
                            <textarea class="mdl-textfield__input" id="notes" rows="3" ${isView ? 'disabled' : ''}>${user.notes || ''}</textarea>
                            <label class="mdl-textfield__label" for="notes">Примечания</label>
                        </div>
                    </div>
                    ${user.telegram_id ? `
                    <div class="form-row">
                        <p><strong>Telegram:</strong> ${user.telegram_username || user.telegram_id} (подключен)</p>
                    </div>
                    ` : ''}
                    <div class="modal-footer">
                        <button type="button" class="mdl-button" onclick="closeUserModal(this)">Закрыть</button>
                        ${!isView ? `<button type="submit" class="mdl-button mdl-button--raised mdl-button--colored">${isEdit ? 'Сохранить' : 'Создать'}</button>` : ''}
                    </div>
                </form>
            </div>
        </div>
    `;
    
    // Инициализация MDL компонентов
    setTimeout(() => {
        if (typeof componentHandler !== 'undefined') {
            componentHandler.upgradeElements(modalDiv.querySelectorAll('.mdl-textfield, .mdl-checkbox'));
        }
    }, 50);
    
    return modalDiv;
}

// Закрытие модального окна
function closeUserModal(btn) {
    const overlay = btn.closest('.modal-overlay');
    overlay.remove();
}

// Отправка формы клиента
async function submitUserForm(event, mode, userId) {
    event.preventDefault();
    
    const formData = {
        company_name: document.getElementById('company_name').value,
        inn: document.getElementById('inn').value,
        full_name: document.getElementById('full_name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        address: document.getElementById('address').value,
        notes: document.getElementById('notes').value,
        role: 'client',
        is_active: true
    };
    
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
        
        alert(mode === 'edit' ? 'Клиент успешно обновлен' : 'Клиент успешно создан');
        closeUserModal(event.target);
        loadUsersData(); // Перезагрузка списка
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка: ' + error.message);
    }
}

// Активировать/деактивировать пользователя
async function toggleUserStatus(userId, userName) {
    const confirmMessage = `Вы действительно хотите изменить статус клиента "${userName}"?`;
    
    if (!confirm(confirmMessage)) {
        return;
    }
    
    try {
        const token = localStorage.getItem('access_token');
        
        const response = await fetch(`${API_BASE_URL}/users/${userId}/toggle-status`, {
            method: 'PATCH',
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
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка изменения статуса');
        }
        
        const result = await response.json();
        alert(result.message || 'Статус успешно изменён');
        
        // Перезагружаем список клиентов
        loadUsersData();
        
    } catch (error) {
        console.error('Ошибка изменения статуса:', error);
        alert('Ошибка: ' + error.message);
    }
}

// Удаление клиента
async function deleteUser(userId, userName) {
    // Подтверждение удаления
    const confirmMessage = `Вы действительно хотите удалить клиента "${userName}"?\n\nВнимание: это деактивирует учетную запись клиента.`;
    
    if (!confirm(confirmMessage)) {
        console.log('Удаление отменено пользователем');
        return;
    }
    
    try {
        const token = localStorage.getItem('access_token');
        
        console.log(`Удаление клиента ID: ${userId}, Имя: ${userName}`);
        
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Response status:', response.status);
        console.log('Response OK:', response.ok);
        
        if (!response.ok) {
            if (response.status === 401) {
                handleLogout();
                return;
            }
            
            // Попытка получить детали ошибки
            const contentType = response.headers.get('content-type');
            let errorMessage = 'Ошибка удаления клиента';
            
            if (contentType && contentType.includes('application/json')) {
                try {
                    const error = await response.json();
                    console.log('Error response:', error);
                    errorMessage = error.detail || JSON.stringify(error);
                } catch (jsonError) {
                    console.error('Ошибка парсинга JSON:', jsonError);
                    const text = await response.text();
                    console.log('Response text:', text);
                    errorMessage = `Ошибка ${response.status}: ${text.substring(0, 200)}`;
                }
            } else {
                const text = await response.text();
                console.log('Response text (not JSON):', text);
                errorMessage = `Ошибка сервера ${response.status}: ${text.substring(0, 200)}`;
            }
            
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        console.log('Успешно удалено:', result);
        
        alert(result.message || 'Клиент успешно деактивирован');
        
        // Перезагружаем список клиентов
        loadUsersData();
        
    } catch (error) {
        console.error('❌ ОШИБКА УДАЛЕНИЯ:', error);
        console.error('Error stack:', error.stack);
        alert('Ошибка: ' + error.message);
    }
}

function showUsersError(message) {
    const usersSection = document.getElementById('users-section');
    if (usersSection) {
        usersSection.innerHTML = `
            <div class="section-header">
                <h2>👥 Управление клиентами</h2>
            </div>
            <div class="mdl-card mdl-shadow--2dp" style="width: 100%; padding: 20px;">
                <p style="color: #f44336; text-align: center;">${message}</p>
            </div>
        `;
    }
}
