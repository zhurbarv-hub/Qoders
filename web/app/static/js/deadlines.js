/**
 * Управление дедлайнами
 */

// Константы API (если ещё не объявлены)
if (typeof API_BASE_URL === 'undefined') {
    var API_BASE_URL = window.location.origin + '/api';
}

const deadlinesSection = document.getElementById('deadlines-section');
let allDeadlines = []; // Храним все дедлайны для фильтрации
let currentFilters = {
    client: '',
    type: '',
    daysRange: 'all',
    status: 'all'
};

/**
 * Загрузка списка дедлайнов
 */
async function loadDeadlinesData() {
    try {
        const token = localStorage.getItem('access_token');
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        
        let url = `${API_BASE_URL}/deadlines?page=1&page_size=50`;
        
        // Для клиентов показываем только их дедлайны
        if (user.role === 'client') {
            url += `&client_id=${user.id}`;
        }
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        console.log('=== ЗАГРУЗКА ДЕДЛАЙНОВ ===');
        console.log('Response status:', response.status);
        console.log('Response OK:', response.ok);

        if (!response.ok) {
            if (response.status === 401) {
                console.log('Неавторизован, выход...');
                handleLogout();
                return;
            }
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error('Ошибка загрузки дедлайнов: ' + response.status);
        }

        const data = await response.json();
        console.log('Данные получены:', data);
        console.log('Количество дедлайнов:', data.deadlines ? data.deadlines.length : 0);
        console.log('Всего дедлайнов по API:', data.total);
        
        // Сохраняем все дедлайны
        allDeadlines = data.deadlines || [];
        
        // Детальное логирование всех дедлайнов
        console.log('=== ПОЛНЫЙ СПИСОК ДЕДЛАЙНОВ ===');
        allDeadlines.forEach((d, idx) => {
            const clientName = d.client?.company_name || d.client?.name || 'НЕТ КЛИЕНТА';
            const typeName = d.deadline_type?.name || d.deadline_type?.type_name || 'НЕТ ТИПА';
            console.log(`${idx + 1}. ID=${d.id}, Клиент="${clientName}", Тип="${typeName}", Дней=${d.days_until_expiration}`);
        });
        
        renderDeadlinesTable(allDeadlines);
        renderDeadlinesPagination(data);
    } catch (error) {
        console.error('Ошибка при загрузке дедлайнов:', error);
        showDeadlinesError('Не удалось загрузить список дедлайнов');
    }
}

/**
 * Отображение таблицы дедлайнов
 */
function renderDeadlinesTable(deadlines) {
    console.log('=== ОТОБРАЖЕНИЕ ТАБЛИЦЫ ДЕДЛАЙНОВ ===');
    console.log('Количество дедлайнов для отображения:', deadlines.length);
    console.log('Общее количество дедлайнов (allDeadlines):', allDeadlines.length);
    if (deadlines.length > 0) {
        console.log('Первый дедлайн:', deadlines[0]);
        console.log('deadline_type первого дедлайна:', deadlines[0].deadline_type);
        console.log('client первого дедлайна:', deadlines[0].client);
    }
    
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const isAdmin = ['admin', 'manager'].includes(user.role);
    
    // Создаем уникальные списки для фильтров
    const uniqueClients = [...new Set(allDeadlines.map(d => d.client?.company_name || d.client?.name).filter(Boolean))];
    const uniqueTypes = [...new Set(allDeadlines.map(d => d.deadline_type?.name || d.deadline_type?.type_name).filter(Boolean))];
    
    console.log('Уникальные клиенты:', uniqueClients);
    console.log('Уникальные типы:', uniqueTypes);
    
    const tableHTML = `
        <div class="section-header">
            <h2>⏰ Управление дедлайнами</h2>
            ${isAdmin ? `
            <button class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" 
                    onclick="showAddDeadlineModal()">
                <i class="material-icons">add</i> Добавить дедлайн
            </button>
            ` : ''}
        </div>
        
        <!-- Панель фильтров -->
        <div class="mdl-card mdl-shadow--2dp" style="width: 100%; padding: 20px; margin-bottom: 20px;">
            <h4 style="margin-top: 0;">🔍 Фильтры</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                ${isAdmin ? `
                <div>
                    <label style="display: block; margin-bottom: 5px; font-weight: 500;">Клиент:</label>
                    <select id="filterClient" class="mdl-textfield__input" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" onchange="applyFilters()">
                        <option value="">Все клиенты</option>
                        ${uniqueClients.map(client => `<option value="${client}">${client}</option>`).join('')}
                    </select>
                </div>
                ` : ''}
                
                <div>
                    <label style="display: block; margin-bottom: 5px; font-weight: 500;">Тип услуги:</label>
                    <select id="filterType" class="mdl-textfield__input" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" onchange="applyFilters()">
                        <option value="">Все типы</option>
                        ${uniqueTypes.map(type => `<option value="${type}">${type}</option>`).join('')}
                    </select>
                </div>
                
                <div>
                    <label style="display: block; margin-bottom: 5px; font-weight: 500;">Осталось дней:</label>
                    <select id="filterDays" class="mdl-textfield__input" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" onchange="applyFilters()">
                        <option value="all">Все</option>
                        <option value="expired">Просрочено (< 0)</option>
                        <option value="urgent">Срочно (0-7 дн.)</option>
                        <option value="soon">Скоро (8-30 дн.)</option>
                        <option value="normal">Активно (> 30 дн.)</option>
                    </select>
                </div>
                
                <div>
                    <label style="display: block; margin-bottom: 5px; font-weight: 500;">Статус:</label>
                    <select id="filterStatus" class="mdl-textfield__input" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" onchange="applyFilters()">
                        <option value="all">Все</option>
                        <option value="Просрочено">Просрочено</option>
                        <option value="Срочно">Срочно</option>
                        <option value="Скоро">Скоро</option>
                        <option value="Активно">Активно</option>
                    </select>
                </div>
                
                <div style="align-self: end;">
                    <button class="mdl-button mdl-js-button mdl-button--raised" onclick="resetFilters()">
                        ✖ Сбросить
                    </button>
                </div>
            </div>
        </div>
        
        <div class="mdl-card mdl-shadow--2dp" style="width: 100%;">
            <table class="mdl-data-table mdl-js-data-table" style="width: 100%;">
                <thead>
                    <tr>
                        ${isAdmin ? '<th class="mdl-data-table__cell--non-numeric">Клиент</th>' : ''}
                        <th class="mdl-data-table__cell--non-numeric">Тип услуги</th>
                        <th>Дата истечения</th>
                        <th>Осталось дней</th>
                        <th>Статус</th>
                        <th>Уведомления</th>
                        ${isAdmin ? '<th>Действия</th>' : ''}
                    </tr>
                </thead>
                <tbody>
                    ${deadlines.length > 0 ? deadlines.map((deadline, idx) => {
                        const daysLeft = deadline.days_until_expiration;
                        const status = getDeadlineStatus(daysLeft);
                        
                        // Получаем имя клиента
                        const clientName = deadline.client?.company_name || deadline.client?.name || '-';
                        
                        // Получаем тип услуги
                        const typeName = deadline.deadline_type?.name || deadline.deadline_type?.type_name || '-';
                        
                        console.log(`Отрисовка строки ${idx + 1}: ID=${deadline.id}, Клиент="${clientName}", Тип="${typeName}"`);
                        
                        return `
                            <tr>
                                ${isAdmin ? `<td class="mdl-data-table__cell--non-numeric">${clientName}</td>` : ''}
                                <td class="mdl-data-table__cell--non-numeric">${typeName}</td>
                                <td>${formatDate(deadline.expiration_date)}</td>
                                <td style="color: ${status.color}">${daysLeft}</td>
                                <td>
                                    <span style="background: ${status.bg}; color: ${status.color}; padding: 4px 8px; border-radius: 4px;">
                                        ${status.label}
                                    </span>
                                </td>
                                <td>${deadline.notification_enabled ? '✅ Включены' : '❌ Отключены'}</td>
                                ${isAdmin ? `
                                <td>
                                    <button class="mdl-button mdl-js-button mdl-button--icon" onclick="editDeadline(${deadline.id})">
                                        <i class="material-icons">edit</i>
                                    </button>
                                    <button class="mdl-button mdl-js-button mdl-button--icon" onclick="deleteDeadline(${deadline.id})">
                                        <i class="material-icons">delete</i>
                                    </button>
                                </td>
                                ` : ''}
                            </tr>
                        `;
                    }).join('') : `
                        <tr>
                            <td colspan="${isAdmin ? '7' : '5'}" style="text-align: center; padding: 20px;">
                                Дедлайны отсутствуют
                            </td>
                        </tr>
                    `}
                </tbody>
            </table>
        </div>
        <div id="deadlinesPagination" style="margin-top: 20px; text-align: center;"></div>
    `;
    
    deadlinesSection.innerHTML = tableHTML;
    
    // Обновляем MDL компоненты
    if (typeof componentHandler !== 'undefined') {
        componentHandler.upgradeDom();
    }
}

/**
 * Вычисление оставшихся дней
 */
function calculateDaysLeft(expiryDate) {
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

/**
 * Получение статуса дедлайна
 */
function getDeadlineStatus(daysLeft) {
    if (daysLeft < 0) {
        return { label: 'Просрочено', color: '#dc3545', bg: '#f8d7da' };
    } else if (daysLeft <= 7) {
        return { label: 'Срочно', color: '#ff6b6b', bg: '#ffe0e0' };
    } else if (daysLeft <= 30) {
        return { label: 'Скоро', color: '#ffa500', bg: '#fff3cd' };
    } else {
        return { label: 'Активно', color: '#28a745', bg: '#d4edda' };
    }
}

/**
 * Форматирование даты
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

/**
 * Отображение пагинации
 */
function renderDeadlinesPagination(data) {
    const paginationDiv = document.getElementById('deadlinesPagination');
    if (!paginationDiv) return;
    
    paginationDiv.innerHTML = `
        <p>Показано ${data.deadlines?.length || 0} из ${data.total || 0} дедлайнов</p>
    `;
}

/**
 * Показать ошибку
 */
function showDeadlinesError(message) {
    deadlinesSection.innerHTML = `
        <div class="mdl-card mdl-shadow--2dp" style="width: 100%; padding: 20px;">
            <p style="color: red; text-align: center;">${message}</p>
        </div>
    `;
}

/**
 * Модальное окно добавления дедлайна
 */
function showAddDeadlineModal() {
    const modal = createDeadlineModal('add');
    document.body.appendChild(modal);
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

/**
 * Редактирование дедлайна
 */
function editDeadline(id) {
    const token = localStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/deadlines/${id}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(deadline => {
        const modal = createDeadlineModal('edit', deadline);
        document.body.appendChild(modal);
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    })
    .catch(error => {
        console.error('Ошибка загрузки дедлайна:', error);
        alert('Не удалось загрузить данные дедлайна');
    });
}

/**
 * Удаление дедлайна
 */
async function deleteDeadline(id) {
    if (!confirm('Вы уверены, что хотите удалить этот дедлайн?')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/deadlines/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка удаления дедлайна');
        }
        
        alert('Дедлайн успешно удалён');
        loadDeadlinesData();
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка: ' + error.message);
    }
}

/**
 * Создание модального окна для дедлайна
 */
function createDeadlineModal(mode, deadline = {}) {
    const isEdit = mode === 'edit';
    const title = isEdit ? 'Редактирование дедлайна' : 'Добавить дедлайн';
    
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal-overlay';
    modalDiv.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h3>${title}</h3>
                <button class="close-btn" onclick="closeDeadlineModal(this)">
                    <i class="material-icons">close</i>
                </button>
            </div>
            <div class="modal-body">
                <form id="deadlineForm" onsubmit="submitDeadlineForm(event, '${mode}', ${deadline.id || 'null'})">
                    <div class="form-group">
                        <label for="client_id">Клиент *</label>
                        <select id="client_id" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                            <option value="">Выберите клиента</option>
                        </select>
                    </div>
                    
                    <div class="form-group" style="margin-top: 16px;">
                        <label for="deadline_type_id">Тип услуги *</label>
                        <select id="deadline_type_id" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                            <option value="">Выберите тип услуги</option>
                        </select>
                    </div>
                    
                    <div class="form-group" style="margin-top: 16px;">
                        <label for="expiration_date">Дата истечения *</label>
                        <input type="date" id="expiration_date" value="${deadline.expiration_date || ''}" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                    </div>
                    
                    <div class="form-group" style="margin-top: 16px;">
                        <label for="notify_days_before">Уведомлять за (дней) *</label>
                        <input type="number" id="notify_days_before" value="${deadline.notify_days_before || 7}" min="1" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                    </div>
                    
                    <div class="form-group" style="margin-top: 16px;">
                        <label>
                            <input type="checkbox" id="notification_enabled" ${deadline.notification_enabled !== false ? 'checked' : ''}>
                            <span>Включить уведомления</span>
                        </label>
                    </div>
                    
                    <div class="form-group" style="margin-top: 16px;">
                        <label for="notes">Заметки</label>
                        <textarea id="notes" rows="3" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">${deadline.notes || ''}</textarea>
                    </div>
                    
                    <div class="modal-footer">
                        <button type="button" class="mdl-button" onclick="closeDeadlineModal(this)">Отмена</button>
                        <button type="submit" class="mdl-button mdl-button--raised mdl-button--colored">
                            ${isEdit ? 'Сохранить' : 'Создать'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    // Загружаем списки клиентов и типов дедлайнов
    setTimeout(async () => {
        await loadClientsForSelect(deadline.client_id);
        await loadDeadlineTypesForSelect(deadline.deadline_type_id);
    }, 50);
    
    return modalDiv;
}

/**
 * Загрузка клиентов для выпадающего списка
 */
async function loadClientsForSelect(selectedId = null) {
    try {
        console.log('=== НАЧАЛО ЗАГРУЗКИ КЛИЕНТОВ ===');
        console.log('Selected ID:', selectedId);
        
        const token = localStorage.getItem('access_token');
        console.log('Token exists:', !!token);
        
        const url = `${API_BASE_URL}/users?role=client&page=1&page_size=100`;
        console.log('Request URL:', url);
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Response status:', response.status);
        console.log('Response OK:', response.ok);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Response error text:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Данные получены:', data);
        console.log('Количество клиентов:', data.users ? data.users.length : 0);
        
        const select = document.getElementById('client_id');
        if (!select) {
            console.error('❌ Select элемент client_id не найден!');
            return;
        }
        console.log('✅ Select элемент найден');
        
        // Очищаем все опции кроме первой
        while (select.options.length > 1) {
            select.remove(1);
        }
        console.log('Select очищен, осталось опций:', select.options.length);
        
        if (!data.users || data.users.length === 0) {
            console.warn('⚠️ Нет доступных клиентов');
            return;
        }
        
        data.users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.company_name || user.full_name;
            if (selectedId && user.id === selectedId) {
                option.selected = true;
            }
            select.appendChild(option);
            console.log('Добавлен клиент:', user.id, '-', option.textContent);
        });
        
        console.log(`✅ Добавлено ${data.users.length} клиентов в select`);
        console.log('Всего опций в select:', select.options.length);
        console.log('=== КОНЕЦ ЗАГРУЗКИ КЛИЕНТОВ ===');
    } catch (error) {
        console.error('❌ ОШИБКА ЗАГРУЗКИ КЛИЕНТОВ:', error);
        console.error('Error stack:', error.stack);
        alert('Не удалось загрузить список клиентов. Проверьте консоль для деталей.');
    }
}

/**
 * Загрузка типов дедлайнов для выпадающего списка
 */
async function loadDeadlineTypesForSelect(selectedId = null) {
    try {
        console.log('Загрузка типов дедлайнов для select...');
        const token = localStorage.getItem('access_token');
        
        // Загружаем только активные типы (без include_inactive)
        const response = await fetch(`${API_BASE_URL}/deadline-types`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const types = await response.json();
        console.log('Типы дедлайнов загружены:', types);
        
        const select = document.getElementById('deadline_type_id');
        if (!select) {
            console.error('Select элемент deadline_type_id не найден!');
            return;
        }
        
        // Очищаем все опции кроме первой
        while (select.options.length > 1) {
            select.remove(1);
        }
        
        if (!types || types.length === 0) {
            console.warn('Нет доступных типов дедлайнов');
            return;
        }
        
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type.id;
            
            // Используем type_name из API, объединяем с description если есть
            const displayName = type.description 
                ? `${type.type_name} (${type.description})` 
                : type.type_name;
            
            option.textContent = displayName;
            
            if (selectedId && type.id === selectedId) {
                option.selected = true;
            }
            select.appendChild(option);
        });
        
        console.log(`Добавлено ${types.length} типов в select`);
    } catch (error) {
        console.error('Ошибка загрузки типов дедлайнов:', error);
        alert('Не удалось загрузить список типов услуг');
    }
}

/**
 * Отправка формы дедлайна
 */
async function submitDeadlineForm(event, mode, deadlineId) {
    event.preventDefault();
    
    const formData = {
        client_id: parseInt(document.getElementById('client_id').value),
        deadline_type_id: parseInt(document.getElementById('deadline_type_id').value),
        expiration_date: document.getElementById('expiration_date').value,
        notify_days_before: parseInt(document.getElementById('notify_days_before').value),
        notification_enabled: document.getElementById('notification_enabled').checked,
        notes: document.getElementById('notes').value
    };
    
    console.log('Отправка формы дедлайна:', mode, formData);
    
    const token = localStorage.getItem('access_token');
    const url = mode === 'edit' ? `${API_BASE_URL}/deadlines/${deadlineId}` : `${API_BASE_URL}/deadlines`;
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
        
        console.log('Response status:', response.status);
        console.log('Response OK:', response.ok);
        
        if (!response.ok) {
            // Пытаемся распарсить JSON ответ
            const contentType = response.headers.get('content-type');
            console.log('Response Content-Type:', contentType);
            
            let errorMessage = 'Ошибка сохранения';
            
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
                // Если не JSON, получаем текст
                const text = await response.text();
                console.log('Response text (not JSON):', text);
                errorMessage = `Ошибка сервера ${response.status}: ${text.substring(0, 200)}`;
            }
            
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        console.log('Успешно сохранено:', result);
        
        alert(mode === 'edit' ? 'Дедлайн успешно обновлён' : 'Дедлайн успешно создан');
        closeDeadlineModal(event.target);
        loadDeadlinesData();
    } catch (error) {
        console.error('❌ ОШИБКА:', error);
        console.error('Error stack:', error.stack);
        alert('Ошибка: ' + error.message);
    }
}

/**
 * Закрытие модального окна дедлайна
 */
function closeDeadlineModal(element) {
    const overlay = element.closest('.modal-overlay');
    if (overlay) {
        overlay.querySelector('.modal').classList.remove('show');
        setTimeout(() => overlay.remove(), 300);
    }
}

/**
 * Применение фильтров
 */
function applyFilters() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const isAdmin = ['admin', 'manager'].includes(user.role);
    
    // Считываем значения фильтров
    const filterClient = isAdmin ? (document.getElementById('filterClient')?.value || '') : '';
    const filterType = document.getElementById('filterType')?.value || '';
    const filterDays = document.getElementById('filterDays')?.value || 'all';
    const filterStatus = document.getElementById('filterStatus')?.value || 'all';
    
    console.log('Применение фильтров:', { filterClient, filterType, filterDays, filterStatus });
    
    // Сохраняем текущие фильтры
    currentFilters = {
        client: filterClient,
        type: filterType,
        daysRange: filterDays,
        status: filterStatus
    };
    
    // Фильтруем дедлайны
    let filtered = allDeadlines.filter(deadline => {
        const clientName = deadline.client?.company_name || deadline.client?.name || '-';
        const typeName = deadline.deadline_type?.name || deadline.deadline_type?.type_name || '-';
        const daysLeft = deadline.days_until_expiration;
        const status = getDeadlineStatus(daysLeft);
        
        // Фильтр по клиенту
        if (filterClient && clientName !== filterClient) {
            return false;
        }
        
        // Фильтр по типу услуги
        if (filterType && typeName !== filterType) {
            return false;
        }
        
        // Фильтр по оставшимся дням
        if (filterDays !== 'all') {
            if (filterDays === 'expired' && daysLeft >= 0) return false;
            if (filterDays === 'urgent' && (daysLeft < 0 || daysLeft > 7)) return false;
            if (filterDays === 'soon' && (daysLeft < 8 || daysLeft > 30)) return false;
            if (filterDays === 'normal' && daysLeft <= 30) return false;
        }
        
        // Фильтр по статусу
        if (filterStatus !== 'all' && status.label !== filterStatus) {
            return false;
        }
        
        return true;
    });
    
    console.log(`Отфильтровано: ${filtered.length} из ${allDeadlines.length} дедлайнов`);
    
    // Перерисовываем таблицу
    renderDeadlinesTable(filtered);
}

/**
 * Сброс фильтров
 */
function resetFilters() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const isAdmin = ['admin', 'manager'].includes(user.role);
    
    // Сбрасываем значения фильтров
    if (isAdmin && document.getElementById('filterClient')) {
        document.getElementById('filterClient').value = '';
    }
    if (document.getElementById('filterType')) {
        document.getElementById('filterType').value = '';
    }
    if (document.getElementById('filterDays')) {
        document.getElementById('filterDays').value = 'all';
    }
    if (document.getElementById('filterStatus')) {
        document.getElementById('filterStatus').value = 'all';
    }
    
    // Сбрасываем текущие фильтры
    currentFilters = {
        client: '',
        type: '',
        daysRange: 'all',
        status: 'all'
    };
    
    console.log('Фильтры сброшены');
    
    // Показываем все дедлайны
    renderDeadlinesTable(allDeadlines);
}
