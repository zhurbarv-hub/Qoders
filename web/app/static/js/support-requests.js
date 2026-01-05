/**
 * Управление обращениями клиентов
 */

// Глобальные переменные
let allRequests = [];
let currentFilter = '';

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    checkAuthentication();
    loadStatistics();
    loadRequests();
});

/**
 * Проверка аутентификации
 */
function checkAuthentication() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/static/login.html';
        return;
    }
}

/**
 * Загрузка статистики
 */
async function loadStatistics() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/support-requests/stats/summary', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/static/login.html';
                return;
            }
            throw new Error('Ошибка загрузки статистики');
        }
        
        const stats = await response.json();
        
        // Обновляем значения
        document.getElementById('stat-total').textContent = stats.total || 0;
        document.getElementById('stat-new').textContent = stats.new || 0;
        document.getElementById('stat-in-progress').textContent = stats.in_progress || 0;
        document.getElementById('stat-resolved').textContent = stats.resolved || 0;
        document.getElementById('stat-closed').textContent = stats.closed || 0;
        
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

/**
 * Загрузка списка обращений
 */
async function loadRequests() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/support-requests/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/static/login.html';
                return;
            }
            throw new Error('Ошибка загрузки обращений');
        }
        
        allRequests = await response.json();
        displayRequests(allRequests);
        
    } catch (error) {
        console.error('Ошибка загрузки обращений:', error);
        showError('Не удалось загрузить обращения');
    }
}

/**
 * Отображение обращений в таблице
 */
function displayRequests(requests) {
    const tbody = document.getElementById('requestsTableBody');
    
    if (!requests || requests.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 40px;">
                    Обращений не найдено
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = requests.map(request => {
        const date = new Date(request.created_at);
        const dateStr = date.toLocaleDateString('ru-RU') + ' ' + date.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'});
        
        const statusBadge = getStatusBadge(request.status);
        const clientName = request.client_company || request.client_name || 'Неизвестен';
        
        return `
            <tr>
                <td class="mdl-data-table__cell--non-numeric">${request.id}</td>
                <td class="mdl-data-table__cell--non-numeric">${dateStr}</td>
                <td class="mdl-data-table__cell--non-numeric">${clientName}</td>
                <td class="mdl-data-table__cell--non-numeric" style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">${request.subject}</td>
                <td class="mdl-data-table__cell--non-numeric">${statusBadge}</td>
                <td class="mdl-data-table__cell--non-numeric">
                    <div class="action-buttons">
                        <button class="mdl-button mdl-js-button mdl-button--icon" title="Подробнее" onclick="showDetails(${request.id})">
                            <i class="material-icons">visibility</i>
                        </button>
                        <button class="mdl-button mdl-js-button mdl-button--icon" title="Изменить статус" onclick="showStatusChange(${request.id})">
                            <i class="material-icons">edit</i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Получить HTML бейдж для статуса
 */
function getStatusBadge(status) {
    const statusLabels = {
        'new': 'Новое',
        'in_progress': 'В работе',
        'resolved': 'Решено',
        'closed': 'Закрыто'
    };
    
    const label = statusLabels[status] || status;
    return `<span class="status-badge status-${status}">${label}</span>`;
}

/**
 * Фильтрация по статусу
 */
function filterByStatus() {
    const filter = document.getElementById('statusFilter').value;
    currentFilter = filter;
    
    if (!filter) {
        displayRequests(allRequests);
        return;
    }
    
    const filtered = allRequests.filter(r => r.status === filter);
    displayRequests(filtered);
}

/**
 * Показать детали обращения
 */
async function showDetails(requestId) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/support-requests/${requestId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки деталей');
        }
        
        const request = await response.json();
        displayRequestDetails(request);
        
    } catch (error) {
        console.error('Ошибка загрузки деталей:', error);
        showError('Не удалось загрузить детали обращения');
    }
}

/**
 * Отображение деталей обращения в модальном окне
 */
function displayRequestDetails(request) {
    document.getElementById('modal-request-id').textContent = request.id;
    
    const createdDate = new Date(request.created_at);
    const updatedDate = new Date(request.updated_at);
    const resolvedDate = request.resolved_at ? new Date(request.resolved_at) : null;
    
    const clientName = request.client_company || request.client_name || 'Неизвестен';
    const statusBadge = getStatusBadge(request.status);
    
    document.getElementById('modalBody').innerHTML = `
        <div class="info-row">
            <div class="info-label">Клиент:</div>
            <div class="info-value"><strong>${clientName}</strong></div>
            ${request.client_inn ? `<div class="info-value" style="color: #666;">ИНН: ${request.client_inn}</div>` : ''}
        </div>
        
        <div class="info-row">
            <div class="info-label">Тема обращения:</div>
            <div class="info-value"><strong>${request.subject}</strong></div>
        </div>
        
        <div class="info-row">
            <div class="info-label">Текст обращения:</div>
            <div class="info-value" style="white-space: pre-wrap; background: #f5f5f5; padding: 12px; border-radius: 4px;">${request.message}</div>
        </div>
        
        <div class="info-row">
            <div class="info-label">Контактный телефон:</div>
            <div class="info-value"><strong>${request.contact_phone}</strong></div>
        </div>
        
        <div class="info-row">
            <div class="info-label">Статус:</div>
            <div class="info-value">${statusBadge}</div>
        </div>
        
        <div class="info-row">
            <div class="info-label">Создано:</div>
            <div class="info-value">${createdDate.toLocaleString('ru-RU')}</div>
        </div>
        
        <div class="info-row">
            <div class="info-label">Последнее обновление:</div>
            <div class="info-value">${updatedDate.toLocaleString('ru-RU')}</div>
        </div>
        
        ${resolvedDate ? `
        <div class="info-row">
            <div class="info-label">Решено:</div>
            <div class="info-value">${resolvedDate.toLocaleString('ru-RU')}</div>
        </div>
        ` : ''}
        
        ${request.resolution_notes ? `
        <div class="info-row">
            <div class="info-label">Заметки о решении:</div>
            <div class="info-value" style="white-space: pre-wrap; background: #e8f5e9; padding: 12px; border-radius: 4px;">${request.resolution_notes}</div>
        </div>
        ` : ''}
    `;
    
    // Показываем модальное окно
    const modal = document.getElementById('detailsModal');
    modal.style.display = 'flex';
}

/**
 * Закрыть модальное окно деталей
 */
function closeDetailsModal() {
    document.getElementById('detailsModal').style.display = 'none';
}

/**
 * Показать диалог изменения статуса
 */
async function showStatusChange(requestId) {
    const newStatus = prompt('Введите новый статус:\n\n- new (новое)\n- in_progress (в работе)\n- resolved (решено)\n- closed (закрыто)', 'in_progress');
    
    if (!newStatus) return;
    
    const validStatuses = ['new', 'in_progress', 'resolved', 'closed'];
    if (!validStatuses.includes(newStatus)) {
        alert('Недопустимый статус');
        return;
    }
    
    const notes = prompt('Добавьте заметки о решении (необязательно):', '');
    
    await updateRequestStatus(requestId, newStatus, notes);
}

/**
 * Обновить статус обращения
 */
async function updateRequestStatus(requestId, status, notes) {
    try {
        const token = localStorage.getItem('access_token');
        
        const body = {
            status: status
        };
        
        if (notes) {
            body.resolution_notes = notes;
        }
        
        const response = await fetch(`/api/support-requests/${requestId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        
        if (!response.ok) {
            throw new Error('Ошибка обновления статуса');
        }
        
        showSuccess('Статус обращения обновлён');
        await refreshRequests();
        
    } catch (error) {
        console.error('Ошибка обновления статуса:', error);
        showError('Не удалось обновить статус обращения');
    }
}

/**
 * Обновить список обращений
 */
async function refreshRequests() {
    await loadStatistics();
    await loadRequests();
}

/**
 * Показать сообщение об ошибке
 */
function showError(message) {
    alert('❌ ' + message);
}

/**
 * Показать сообщение об успехе
 */
function showSuccess(message) {
    alert('✅ ' + message);
}

// Закрытие модального окна по клику вне его
document.addEventListener('click', function(event) {
    const modal = document.getElementById('detailsModal');
    if (event.target === modal) {
        closeDetailsModal();
    }
});
