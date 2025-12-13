// client-details.js - Детали клиента с кассами и дедлайнами

const API_BASE = '/api';
let currentUserId = null;
let clientData = null;
let deadlineTypes = [];
let ofdProviders = [];  // Список ОФД провайдеров
let registerDialog = null;
let deadlineDialog = null;

// Получить ID клиента из URL
function getUserIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

// Загрузка данных клиента
async function loadClientDetails() {
    const userId = getUserIdFromUrl();
    if (!userId) {
        alert('ID клиента не указан');
        window.location.href = '/static/dashboard.html';
        return;
    }

    currentUserId = userId;

    try {
        const response = await fetch(`${API_BASE}/users/${userId}/full-details`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (!response.ok) {
            throw new Error(`Ошибка: ${response.status}`);
        }

        clientData = await response.json();
        console.log('Загруженные данные клиента:', clientData);
        console.log('ID клиента:', clientData.id);
        console.log('Кассы клиента:', clientData.cash_registers);
        if (clientData.cash_registers && clientData.cash_registers.length > 0) {
            console.log('Первая касса:', clientData.cash_registers[0]);
            console.log('ofd_provider_id первой кассы:', clientData.cash_registers[0].ofd_provider_id);
        }
        renderClientDetails();
    } catch (error) {
        console.error('Ошибка загрузки данных клиента:', error);
        alert('Не удалось загрузить данные клиента');
    }
}

// Отображение данных клиента
function renderClientDetails() {
    if (!clientData) return;

    // Заголовок
    document.getElementById('clientName').textContent = clientData.name || 'Без названия';
    const phoneInfo = clientData.phone ? ` | Телефон: ${clientData.phone}` : '';
    document.getElementById('clientInfo').textContent = `ИНН: ${clientData.inn || '-'} | Email: ${clientData.email || '-'}${phoneInfo}`;

    // Статус Telegram
    const telegramStatus = document.getElementById('telegramStatus');
    const telegramStatusText = document.getElementById('telegramStatusText');
    const sendToTelegramBtn = document.getElementById('sendToTelegramBtn');
    
    if (clientData.telegram_id) {
        telegramStatus.classList.remove('disconnected');
        telegramStatus.classList.add('connected');
        telegramStatusText.textContent = 'Подключен';
        
        // Показываем кнопку отправки в Telegram
        if (sendToTelegramBtn) {
            sendToTelegramBtn.style.display = 'inline-flex';
        }
    } else {
        telegramStatus.classList.remove('connected');
        telegramStatus.classList.add('disconnected');
        telegramStatusText.textContent = 'Не подключен';
    }

    // Сетка информации о клиенте
    const detailsGrid = document.getElementById('clientDetailsGrid');
    
    // Формируем карточки с информацией
    let cardsHTML = '';
    
    // Контактное лицо
    cardsHTML += `
        <div class="client-info-item editable-field" data-field="contact_person">
            <div class="client-info-icon">
                <i class="material-icons">person</i>
            </div>
            <div class="client-info-content">
                <div class="client-info-label">Контактное лицо</div>
                <div class="client-info-value ${!clientData.contact_person ? 'empty' : ''}">
                    ${clientData.contact_person || 'Не указано'}
                </div>
            </div>
        </div>
    `;
    
    // Телефон
    cardsHTML += `
        <div class="client-info-item editable-field" data-field="phone">
            <div class="client-info-icon">
                <i class="material-icons">phone</i>
            </div>
            <div class="client-info-content">
                <div class="client-info-label">Телефон</div>
                <div class="client-info-value ${!clientData.phone ? 'empty' : ''}">
                    ${clientData.phone ? `<a href="tel:${clientData.phone}">${clientData.phone}</a>` : 'Не указан'}
                </div>
            </div>
        </div>
    `;
    
    // Email
    cardsHTML += `
        <div class="client-info-item editable-field" data-field="email">
            <div class="client-info-icon">
                <i class="material-icons">email</i>
            </div>
            <div class="client-info-content">
                <div class="client-info-label">Email</div>
                <div class="client-info-value ${!clientData.email ? 'empty' : ''}">
                    ${clientData.email ? `<a href="mailto:${clientData.email}">${clientData.email}</a>` : 'Не указан'}
                </div>
            </div>
        </div>
    `;
    
    // Адрес
    cardsHTML += `
        <div class="client-info-item editable-field" data-field="address">
            <div class="client-info-icon">
                <i class="material-icons">location_on</i>
            </div>
            <div class="client-info-content">
                <div class="client-info-label">Адрес</div>
                <div class="client-info-value ${!clientData.address ? 'empty' : ''}">
                    ${clientData.address || 'Не указан'}
                </div>
            </div>
        </div>
    `;
    
    // Примечания
    cardsHTML += `
        <div class="client-info-item editable-field" data-field="notes">
            <div class="client-info-icon">
                <i class="material-icons">notes</i>
            </div>
            <div class="client-info-content">
                <div class="client-info-label">Примечания</div>
                <div class="client-info-value ${!clientData.notes ? 'empty' : ''}">
                    ${clientData.notes || 'Нет примечаний'}
                </div>
            </div>
        </div>
    `;
    
    // Telegram регистрация (только если не подключен)
    if (!clientData.telegram_id) {
        cardsHTML += `
            <div class="client-info-item telegram-item">
                <div class="client-info-icon">
                    <i class="material-icons">telegram</i>
                </div>
                <div class="client-info-content">
                    <div class="client-info-label">Telegram регистрация</div>
                    <div class="client-info-value">
                        <button class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" 
                                onclick="generateTelegramCode()" 
                                style="height: 32px; line-height: 32px; font-size: 13px; margin: 0;">
                            <i class="material-icons" style="font-size: 16px; vertical-align: middle;">vpn_key</i>
                            Сгенерировать код
                        </button>
                        <div class="telegram-code-block" id="telegramCodeBlock" style="display: none;">
                            <span class="telegram-code-display" id="telegramCodeDisplay"></span>
                            <button class="mdl-button mdl-js-button mdl-button--icon" 
                                    onclick="copyTelegramCode()" 
                                    title="Копировать код" 
                                    id="copyCodeButton">
                                <i class="material-icons" style="font-size: 18px;">content_copy</i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    detailsGrid.innerHTML = cardsHTML;
    
    // Добавление обработчиков для inline редактирования
    setTimeout(() => {
        const editableFields = document.querySelectorAll('.editable-field');
        editableFields.forEach(field => {
            field.addEventListener('click', function() {
                makeFieldEditable(field);
            });
        });
    }, 100);

    // Кассовые аппараты
    renderCashRegisters();

    // Дедлайны
    renderDeadlines();
}

// Отображение кассовых аппаратов
function renderCashRegisters() {
    const section = document.getElementById('cashRegistersSection');
    const count = document.getElementById('registersCount');
    const registers = clientData.cash_registers || [];

    count.textContent = registers.length;

    if (registers.length === 0) {
        section.innerHTML = '<p style="color: #999;">Кассовые аппараты не найдены</p>';
        return;
    }

    console.log('=== Начало рендеринга касс ===');
    console.log('Всего ОФД провайдеров загружено:', ofdProviders.length);
    console.log('Список ОФД провайдеров:', ofdProviders);
    
    let html = '';
    registers.forEach(reg => {
        // Находим название ОФД провайдера по ID
        console.log('Обработка кассы:', reg.register_name, 'OFD ID:', reg.ofd_provider_id, 'Тип:', typeof reg.ofd_provider_id);
        const ofdProvider = reg.ofd_provider_id 
            ? ofdProviders.find(p => p.id === reg.ofd_provider_id)
            : null;
        const ofdName = ofdProvider ? ofdProvider.provider_name : '-';
        console.log('ОФД провайдер найден:', ofdProvider, 'Название:', ofdName);
        
        html += `
            <div class="register-card" data-register-id="${reg.id}">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                    <h4 style="margin: 0;">
                        <i class="material-icons" style="vertical-align: middle;">point_of_sale</i>
                        ${reg.register_name}
                    </h4>
                    <div>
                        <button class="mdl-button mdl-js-button mdl-button--icon" onclick="deleteRegister(${reg.id})" title="Удалить">
                            <i class="material-icons">delete</i>
                        </button>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 200px 1fr; gap: 10px; font-size: 14px;">
                    <div style="font-weight: bold;">Серийный номер:</div>
                    <div>${reg.serial_number}</div>
                    <div style="font-weight: bold;">Номер ФН:</div>
                    <div>${reg.fiscal_drive_number}</div>
                    <div style="font-weight: bold;">Адрес установки:</div>
                    <div>${reg.installation_address || '-'}</div>
                    <div style="font-weight: bold;">Наименование ОФД:</div>
                    <div>${ofdName}</div>
                    <div style="font-weight: bold;">Дата замены ФН:</div>
                    <div>${reg.fn_replacement_date ? `<span style="color: #3f51b5;">🗓️ ${formatDateRU(reg.fn_replacement_date)}</span>` : '-'}</div>
                    <div style="font-weight: bold;">Дата продления ОФД:</div>
                    <div>${reg.ofd_renewal_date ? `<span style="color: #3f51b5;">🗓️ ${formatDateRU(reg.ofd_renewal_date)}</span>` : '-'}</div>
                    <div style="font-weight: bold;">Примечание:</div>
                    <div>${reg.notes || '-'}</div>
                    <div style="font-weight: bold;">Статус:</div>
                    <div>
                        <span class="badge ${reg.is_active ? 'badge-green' : 'badge-red'}">
                            ${reg.is_active ? 'Активна' : 'Неактивна'}
                        </span>
                    </div>
                </div>
            </div>
        `;
    });

    section.innerHTML = html;
    
    // Добавление обработчиков клика на карточки кассовых аппаратов
    setTimeout(() => {
        const registerCards = document.querySelectorAll('.register-card');
        registerCards.forEach(card => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', function(e) {
                // Проверяем, что клик не по кнопке удаления
                if (!e.target.closest('button') && !e.target.closest('.mdl-button')) {
                    const registerId = parseInt(card.getAttribute('data-register-id'));
                    editRegister(registerId);
                }
            });
        });
    }, 100);
}

// Отображение дедлайнов
function renderDeadlines() {
    renderRegisterDeadlines();
    renderGeneralDeadlines();
}

// Отображение дедлайнов по кассам
function renderRegisterDeadlines() {
    const section = document.getElementById('registerDeadlinesSection');
    const count = document.getElementById('registerDeadlinesCount');
    const deadlines = clientData.register_deadlines || [];

    count.textContent = deadlines.length;

    if (deadlines.length === 0) {
        section.innerHTML = '<p style="color: #999;">Дедлайны по кассам не найдены</p>';
        return;
    }

    let html = '';
    deadlines.forEach(dl => {
        const statusClass = `status-${dl.status_color}`;
        const badgeClass = `badge-${dl.status_color}`;
        const daysText = dl.days_until_expiration < 0 
            ? `Просрочено на ${Math.abs(dl.days_until_expiration)} дн.`
            : `Осталось ${dl.days_until_expiration} дн.`;

        html += `
            <div class="deadline-item ${statusClass}" data-deadline-id="${dl.deadline_id}" data-deadline-type="register">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="flex: 1;">
                        <strong>${dl.deadline_type_name}</strong>
                        <div style="font-size: 12px; color: #666; margin-top: 4px;">
                            <i class="material-icons" style="font-size: 14px; vertical-align: middle;">point_of_sale</i>
                            ${dl.cash_register_name}
                        </div>
                        ${dl.installation_address ? `
                        <div style="font-size: 12px; color: #888; margin-top: 2px;">
                            <i class="material-icons" style="font-size: 14px; vertical-align: middle;">place</i>
                            ${dl.installation_address}
                        </div>
                        ` : ''}
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="badge ${badgeClass}">${daysText}</span>
                        <button class="mdl-button mdl-js-button mdl-button--icon" onclick="deleteDeadline(${dl.deadline_id})" title="Удалить">
                            <i class="material-icons" style="font-size: 18px;">delete</i>
                        </button>
                    </div>
                </div>
                <div style="font-size: 13px; color: #555;">
                    <i class="material-icons" style="font-size: 14px; vertical-align: middle;">event</i>
                    ${formatDateRU(dl.expiration_date)}
                </div>
                ${dl.notes ? `<div style="font-size: 12px; color: #777; margin-top: 4px;">${dl.notes}</div>` : ''}
            </div>
        `;
    });

    section.innerHTML = html;
    
    // Добавление обработчиков клика на дедлайны по кассам
    setTimeout(() => {
        const deadlineItems = document.querySelectorAll('#registerDeadlinesSection .deadline-item');
        deadlineItems.forEach(item => {
            item.style.cursor = 'pointer';
            item.addEventListener('click', function(e) {
                // Проверяем, что клик не по кнопке удаления
                if (!e.target.closest('button') && !e.target.closest('.mdl-button')) {
                    const deadlineId = parseInt(item.getAttribute('data-deadline-id'));
                    editDeadline(deadlineId, 'register');
                }
            });
        });
    }, 100);
}

// Отображение общих дедлайнов
function renderGeneralDeadlines() {
    const section = document.getElementById('generalDeadlinesSection');
    const count = document.getElementById('generalDeadlinesCount');
    const deadlines = clientData.general_deadlines || [];

    count.textContent = deadlines.length;

    if (deadlines.length === 0) {
        section.innerHTML = '<p style="color: #999;">Общие дедлайны не найдены</p>';
        return;
    }

    let html = '';
    deadlines.forEach(dl => {
        const statusClass = `status-${dl.status_color}`;
        const badgeClass = `badge-${dl.status_color}`;
        const daysText = dl.days_until_expiration < 0 
            ? `Просрочено на ${Math.abs(dl.days_until_expiration)} дн.`
            : `Осталось ${dl.days_until_expiration} дн.`;

        html += `
            <div class="deadline-item ${statusClass}" data-deadline-id="${dl.deadline_id}" data-deadline-type="general">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong>${dl.deadline_type_name}</strong>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="badge ${badgeClass}">${daysText}</span>
                        <button class="mdl-button mdl-js-button mdl-button--icon" onclick="deleteDeadline(${dl.deadline_id})" title="Удалить">
                            <i class="material-icons" style="font-size: 18px;">delete</i>
                        </button>
                    </div>
                </div>
                <div style="font-size: 13px; color: #555;">
                    <i class="material-icons" style="font-size: 14px; vertical-align: middle;">event</i>
                    ${formatDateRU(dl.expiration_date)}
                </div>
                ${dl.notes ? `<div style="font-size: 12px; color: #777; margin-top: 4px;">${dl.notes}</div>` : ''}
            </div>
        `;
    });

    section.innerHTML = html;
    
    // Добавление обработчиков клика на общие дедлайны
    setTimeout(() => {
        const deadlineItems = document.querySelectorAll('#generalDeadlinesSection .deadline-item');
        deadlineItems.forEach(item => {
            item.style.cursor = 'pointer';
            item.addEventListener('click', function(e) {
                // Проверяем, что клик не по кнопке удаления
                if (!e.target.closest('button') && !e.target.closest('.mdl-button')) {
                    const deadlineId = parseInt(item.getAttribute('data-deadline-id'));
                    editDeadline(deadlineId, 'general');
                }
            });
        });
    }, 100);
}

// ========== ФУНКЦИИ ДЛЯ INLINE РЕДАКТИРОВАНИЯ ПОЛЕЙ КЛИЕНТА ==========

// Сделать поле редактируемым
function makeFieldEditable(fieldElement) {
    const fieldName = fieldElement.getAttribute('data-field');
    const currentValue = clientData[fieldName] || '';
    const displayValue = fieldElement.textContent;
    
    // Если это уже input, ничего не делаем
    if (fieldElement.querySelector('input') || fieldElement.querySelector('textarea')) {
        return;
    }
    
    let inputElement;
    if (fieldName === 'notes' || fieldName === 'address') {
        // Для больших полей используем textarea
        inputElement = document.createElement('textarea');
        inputElement.rows = 3;
        inputElement.style.width = '100%';
        inputElement.style.padding = '4px';
        inputElement.style.border = '1px solid #3f51b5';
        inputElement.style.borderRadius = '2px';
        inputElement.style.fontFamily = 'inherit';
        inputElement.style.fontSize = 'inherit';
    } else {
        // Для остальных полей используем input
        inputElement = document.createElement('input');
        inputElement.type = 'text';
        inputElement.style.width = '100%';
        inputElement.style.padding = '4px';
        inputElement.style.border = '1px solid #3f51b5';
        inputElement.style.borderRadius = '2px';
        inputElement.style.fontFamily = 'inherit';
        inputElement.style.fontSize = 'inherit';
    }
    
    inputElement.value = currentValue === '-' ? '' : currentValue;
    
    // Заменяем содержимое на input
    fieldElement.innerHTML = '';
    fieldElement.appendChild(inputElement);
    inputElement.focus();
    inputElement.select();
    
    // Обработчик потери фокуса
    inputElement.addEventListener('blur', async function() {
        const newValue = inputElement.value.trim();
        await saveClientField(fieldName, newValue, fieldElement);
    });
    
    // Обработчик Enter (кроме textarea)
    if (inputElement.tagName !== 'TEXTAREA') {
        inputElement.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                inputElement.blur();
            } else if (e.key === 'Escape') {
                fieldElement.textContent = displayValue;
            }
        });
    } else {
        // Для textarea только Escape
        inputElement.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                fieldElement.textContent = displayValue;
            }
        });
    }
}

// Сохранить изменение поля клиента
async function saveClientField(fieldName, newValue, fieldElement) {
    try {
        const updateData = {
            [fieldName]: newValue || null
        };
        
        const response = await fetch(`${API_BASE}/users/${currentUserId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify(updateData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сохранения');
        }
        
        // Обновляем локальные данные
        clientData[fieldName] = newValue || null;
        
        // Восстанавливаем отображение
        fieldElement.textContent = newValue || '-';
        fieldElement.style.cursor = 'pointer';
        
        // Обновляем заголовок если изменился телефон
        if (fieldName === 'phone') {
            const phoneInfo = clientData.phone ? ` | Телефон: ${clientData.phone}` : '';
            document.getElementById('clientInfo').textContent = `ИНН: ${clientData.inn || '-'} | Email: ${clientData.email || '-'}${phoneInfo}`;
        }
        
        // Показываем уведомление об успехе
        showNotification('Изменения сохранены');
    } catch (error) {
        console.error('Ошибка сохранения поля:', error);
        alert(`Ошибка: ${error.message}`);
        // Возвращаем старое значение
        fieldElement.textContent = clientData[fieldName] || '-';
        fieldElement.style.cursor = 'pointer';
    }
}

// Показать уведомление
function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = '#4CAF50';
    notification.style.color = 'white';
    notification.style.padding = '12px 24px';
    notification.style.borderRadius = '4px';
    notification.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';
    notification.style.zIndex = '10000';
    notification.style.fontSize = '14px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transition = 'opacity 0.3s';
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 2000);
}

// ========== ФУНКЦИИ ДЛЯ TELEGRAM РЕГИСТРАЦИИ ==========

// Генерация кода регистрации для Telegram
async function generateTelegramCode() {
    try {
        const response = await fetch(`${API_BASE}/users/${currentUserId}/generate-code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка генерации кода');
        }
        
        const result = await response.json();
        
        // Извлекаем код из сообщения (формат: "Код регистрации: XXXXX (действителен 24 часа)")
        const codeMatch = result.message.match(/Код регистрации: ([A-Z0-9]+)/);
        if (codeMatch && codeMatch[1]) {
            const code = codeMatch[1];
            
            // Отображаем код в новой структуре
            const codeDisplay = document.getElementById('telegramCodeDisplay');
            const codeBlock = document.getElementById('telegramCodeBlock');
            const copyButton = document.getElementById('copyCodeButton');
            
            if (codeDisplay && codeBlock && copyButton) {
                codeDisplay.textContent = code;
                codeBlock.style.display = 'flex';
                
                // Сохраняем код для копирования
                window.currentTelegramCode = code;
                
                showNotification('Код успешно сгенерирован. Отправьте его боту в Telegram. Код действителен 72 часа.');
            }
        } else {
            throw new Error('Не удалось извлечь код из ответа');
        }
    } catch (error) {
        console.error('Ошибка генерации кода:', error);
        alert(`Ошибка: ${error.message}`);
    }
}

// Копирование кода в буфер обмена
async function copyTelegramCode() {
    if (!window.currentTelegramCode) {
        alert('Код не сгенерирован');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(window.currentTelegramCode);
        showNotification('Код скопирован в буфер обмена');
    } catch (error) {
        console.error('Ошибка копирования:', error);
        // Fallback для старых браузеров
        const textArea = document.createElement('textarea');
        textArea.value = window.currentTelegramCode;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showNotification('Код скопирован в буфер обмена');
        } catch (err) {
            alert('Не удалось скопировать код');
        }
        document.body.removeChild(textArea);
    }
}

// ========== ФУНКЦИИ ДЛЯ РАБОТЫ С КАССОВЫМИ АППАРАТАМИ ==========

// Загрузить список ОФД провайдеров
async function loadOFDProviders() {
    try {
        const response = await fetch(`${API_BASE}/ofd-providers?active_only=true`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`Ошибка: ${response.status}`);
        }
        
        ofdProviders = await response.json();
        console.log('Загружено ОФД провайдеров:', ofdProviders.length);
    } catch (error) {
        console.error('Ошибка загрузки ОФД провайдеров:', error);
        ofdProviders = [];
    }
}

// Открыть диалог добавления кассы
function showAddRegisterDialog() {
    document.getElementById('registerDialogTitle').textContent = 'Добавить кассовый аппарат';
    document.getElementById('registerForm').reset();
    document.getElementById('registerId').value = '';
    
    // Заполняем список ОФД провайдеров
    const ofdSelect = document.getElementById('ofdProvider');
    ofdSelect.innerHTML = '<option value="">Не выбран</option>';
    ofdProviders.forEach(provider => {
        const option = document.createElement('option');
        option.value = provider.id;
        option.textContent = provider.provider_name;
        ofdSelect.appendChild(option);
    });
    
    registerDialog.showModal();
}

// Редактировать кассу
function editRegister(registerId) {
    const register = clientData.cash_registers.find(r => r.id === registerId);
    if (!register) {
        alert('Касса не найдена');
        return;
    }

    document.getElementById('registerDialogTitle').textContent = 'Редактировать кассовый аппарат';
    document.getElementById('registerId').value = register.id;
    document.getElementById('registerName').value = register.register_name;
    document.getElementById('serialNumber').value = register.serial_number;
    document.getElementById('fiscalDriveNumber').value = register.fiscal_drive_number;
    document.getElementById('installationAddress').value = register.installation_address || '';
    document.getElementById('registerNotes').value = register.notes || '';
    document.getElementById('fnReplacementDate').value = register.fn_replacement_date || '';
    document.getElementById('ofdRenewalDate').value = register.ofd_renewal_date || '';
    
    // Заполняем список ОФД провайдеров и устанавливаем выбранный
    const ofdSelect = document.getElementById('ofdProvider');
    ofdSelect.innerHTML = '<option value="">Не выбран</option>';
    ofdProviders.forEach(provider => {
        const option = document.createElement('option');
        option.value = provider.id;
        option.textContent = provider.provider_name;
        if (register.ofd_provider_id && provider.id === register.ofd_provider_id) {
            option.selected = true;
        }
        ofdSelect.appendChild(option);
    });
    
    // Обновляем MDL textfield
    document.querySelectorAll('#registerForm .mdl-textfield').forEach(field => {
        field.MaterialTextfield.checkDirty();
    });
    
    registerDialog.showModal();
}

// Сохранить кассу
async function saveRegister() {
    const registerId = document.getElementById('registerId').value;
    const registerName = document.getElementById('registerName').value.trim();
    const serialNumber = document.getElementById('serialNumber').value.trim();
    const fiscalDriveNumber = document.getElementById('fiscalDriveNumber').value.trim();
    const installationAddress = document.getElementById('installationAddress').value.trim();
    const ofdProviderId = document.getElementById('ofdProvider').value;  // Получаем ID провайдера
    const registerNotes = document.getElementById('registerNotes').value.trim();
    const fnReplacementDate = document.getElementById('fnReplacementDate').value || null;
    const ofdRenewalDate = document.getElementById('ofdRenewalDate').value || null;

    if (!registerName || !serialNumber || !fiscalDriveNumber) {
        alert('Заполните все обязательные поля');
        return;
    }

    const data = {
        user_id: clientData.id,  // Используем ID из загруженных данных клиента
        register_name: registerName,
        serial_number: serialNumber,
        fiscal_drive_number: fiscalDriveNumber,
        installation_address: installationAddress || '',
        ofd_provider_id: ofdProviderId ? parseInt(ofdProviderId) : null,  // Отправляем ID провайдера
        notes: registerNotes || '',
        fn_replacement_date: fnReplacementDate,
        ofd_renewal_date: ofdRenewalDate
    };

    console.log('Текущий clientData:', clientData);
    console.log('Используемый user_id:', clientData.id, 'type:', typeof clientData.id);

    try {
        console.log('Отправка данных кассы:', data);
        
        let response;
        if (registerId) {
            // Редактирование
            response = await fetch(`${API_BASE}/cash-registers/${registerId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getToken()}`
                },
                body: JSON.stringify(data)
            });
        } else {
            // Создание
            response = await fetch(`${API_BASE}/cash-registers`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getToken()}`
                },
                body: JSON.stringify(data)
            });
        }

        console.log('Статус ответа:', response.status, response.statusText);

        if (!response.ok) {
            let errorMessage = `Ошибка HTTP: ${response.status} ${response.statusText}`;
            try {
                const errorData = await response.json();
                console.log('Данные ошибки:', errorData);
                
                if (errorData.detail) {
                    // FastAPI возвращает ошибки в поле detail
                    if (typeof errorData.detail === 'string') {
                        errorMessage = errorData.detail;
                    } else if (Array.isArray(errorData.detail)) {
                        // Pydantic validation errors
                        errorMessage = errorData.detail.map(err => 
                            `${err.loc.join('.')}: ${err.msg}`
                        ).join(', ');
                    } else {
                        errorMessage = JSON.stringify(errorData.detail);
                    }
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                } else {
                    errorMessage = JSON.stringify(errorData);
                }
            } catch (parseError) {
                console.error('Не удалось распарсить ошибку:', parseError);
                // Если не удалось распарсить JSON, попробуем получить текст
                try {
                    const textError = await response.text();
                    if (textError) {
                        errorMessage = textError;
                    }
                } catch (textError) {
                    console.error('Не удалось получить текст ошибки:', textError);
                }
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('Касса успешно сохранена:', result);
        
        registerDialog.close();
        await loadClientDetails(); // Перезагрузка данных
        alert(registerId ? 'Касса успешно обновлена' : 'Касса успешно добавлена');
    } catch (error) {
        console.error('Ошибка сохранения кассы:', error);
        
        let errorMessage = 'Неизвестная ошибка';
        if (error.message) {
            errorMessage = error.message;
        } else if (typeof error === 'object') {
            try {
                errorMessage = JSON.stringify(error);
            } catch (e) {
                errorMessage = String(error);
            }
        } else {
            errorMessage = String(error);
        }
        
        alert(`Ошибка при сохранении кассы: ${errorMessage}`);
    }
}

// Удалить кассу
async function deleteRegister(registerId) {
    if (!confirm('Вы уверены, что хотите удалить эту кассу?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/cash-registers/${registerId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка удаления');
        }

        await loadClientDetails();
        alert('Касса успешно удалена');
    } catch (error) {
        console.error('Ошибка удаления кассы:', error);
        alert(`Ошибка: ${error.message}`);
    }
}

// ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ДЕДЛАЙНАМИ ==========

// Загрузить типы дедлайнов
async function loadDeadlineTypes() {
    try {
        const response = await fetch(`${API_BASE}/deadline-types`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка загрузки типов дедлайнов');
        }

        deadlineTypes = await response.json();
    } catch (error) {
        console.error('Ошибка загрузки типов:', error);
    }
}

// Открыть диалог добавления дедлайна
function showAddDeadlineDialog() {
    document.getElementById('deadlineDialogTitle').textContent = 'Добавить дедлайн';
    document.getElementById('deadlineForm').reset();
    document.getElementById('deadlineId').value = '';
    document.getElementById('deadlineNotifyDays').value = '7';
    document.getElementById('deadlineNotificationEnabled').checked = true;
    
    // Заполняем выбор типов дедлайнов
    const typeSelect = document.getElementById('deadlineType');
    typeSelect.innerHTML = '<option value="">Выберите тип</option>';
    deadlineTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.id;
        option.textContent = type.type_name;
        typeSelect.appendChild(option);
    });
    
    // Заполняем выбор кассовых аппаратов
    const registerSelect = document.getElementById('deadlineCashRegister');
    registerSelect.innerHTML = '<option value="">Общий дедлайн (не привязан к кассе)</option>';
    if (clientData.cash_registers) {
        clientData.cash_registers.forEach(reg => {
            if (reg.is_active) {
                const option = document.createElement('option');
                option.value = reg.id;
                option.textContent = reg.register_name;
                registerSelect.appendChild(option);
            }
        });
    }
    
    deadlineDialog.showModal();
}

// Открыть диалог добавления дедлайна по кассам (с предвыбранной кассой)
function showAddRegisterDeadlineDialog() {
    document.getElementById('deadlineDialogTitle').textContent = 'Добавить дедлайн по кассам';
    document.getElementById('deadlineForm').reset();
    document.getElementById('deadlineId').value = '';
    document.getElementById('deadlineNotifyDays').value = '7';
    document.getElementById('deadlineNotificationEnabled').checked = true;
    
    // Заполняем выбор типов дедлайнов
    const typeSelect = document.getElementById('deadlineType');
    typeSelect.innerHTML = '<option value="">Выберите тип</option>';
    deadlineTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.id;
        option.textContent = type.type_name;
        typeSelect.appendChild(option);
    });
    
    // Заполняем выбор кассовых аппаратов (обязательно выбрать кассу)
    const registerSelect = document.getElementById('deadlineCashRegister');
    registerSelect.innerHTML = '<option value="">Выберите кассу *</option>';
    if (clientData.cash_registers) {
        clientData.cash_registers.forEach(reg => {
            if (reg.is_active) {
                const option = document.createElement('option');
                option.value = reg.id;
                option.textContent = reg.register_name;
                registerSelect.appendChild(option);
            }
        });
    }
    
    deadlineDialog.showModal();
}

// Редактировать дедлайн
function editDeadline(deadlineId, deadlineType) {
    let deadline = null;
    
    // Найти дедлайн в соответствующем массиве
    if (deadlineType === 'register') {
        deadline = clientData.register_deadlines.find(d => d.deadline_id === deadlineId);
    } else {
        deadline = clientData.general_deadlines.find(d => d.deadline_id === deadlineId);
    }
    
    if (!deadline) {
        alert('Дедлайн не найден');
        return;
    }
    
    document.getElementById('deadlineDialogTitle').textContent = 'Редактировать дедлайн';
    document.getElementById('deadlineId').value = deadlineId;
    
    // Заполняем выбор типов дедлайнов
    const typeSelect = document.getElementById('deadlineType');
    typeSelect.innerHTML = '<option value="">Выберите тип</option>';
    deadlineTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.id;
        option.textContent = type.type_name;
        if (type.type_name === deadline.deadline_type_name) {
            option.selected = true;
        }
        typeSelect.appendChild(option);
    });
    
    // Заполняем выбор кассовых аппаратов
    const registerSelect = document.getElementById('deadlineCashRegister');
    registerSelect.innerHTML = '<option value="">Общий дедлайн (не привязан к кассе)</option>';
    if (clientData.cash_registers) {
        clientData.cash_registers.forEach(reg => {
            if (reg.is_active) {
                const option = document.createElement('option');
                option.value = reg.id;
                option.textContent = reg.register_name;
                if (deadline.cash_register_id && reg.id === deadline.cash_register_id) {
                    option.selected = true;
                }
                registerSelect.appendChild(option);
            }
        });
    }
    
    // Заполняем дату и примечания
    document.getElementById('deadlineExpiration').value = deadline.expiration_date;
    document.getElementById('deadlineNotifyDays').value = deadline.notify_days_before || 7;
    document.getElementById('deadlineNotificationEnabled').checked = deadline.notification_enabled !== false;
    document.getElementById('deadlineNotes').value = deadline.notes || '';
    
    // Обновляем MDL textfield
    document.querySelectorAll('#deadlineForm .mdl-textfield').forEach(field => {
        if (field.MaterialTextfield) {
            field.MaterialTextfield.checkDirty();
        }
    });
    
    deadlineDialog.showModal();
}

// Сохранить дедлайн
async function saveDeadline() {
    const deadlineId = document.getElementById('deadlineId').value;
    const deadlineTypeId = document.getElementById('deadlineType').value;
    const cashRegisterId = document.getElementById('deadlineCashRegister').value;
    const expirationDate = document.getElementById('deadlineExpiration').value;
    const notifyDays = document.getElementById('deadlineNotifyDays').value;
    const notificationEnabled = document.getElementById('deadlineNotificationEnabled').checked;
    const notes = document.getElementById('deadlineNotes').value.trim();

    if (!deadlineTypeId || !expirationDate || !notifyDays) {
        alert('Заполните все обязательные поля');
        return;
    }

    const data = {
        client_id: clientData.id,  // Используем ID из загруженных данных клиента
        deadline_type_id: parseInt(deadlineTypeId),
        cash_register_id: cashRegisterId ? parseInt(cashRegisterId) : null,
        expiration_date: expirationDate,
        notify_days_before: parseInt(notifyDays),
        notification_enabled: notificationEnabled,
        notes: notes || '',  // Пустая строка вместо null
        status: 'active'
    };

    try {
        let response;
        if (deadlineId) {
            // Редактирование
            response = await fetch(`${API_BASE}/deadlines/${deadlineId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getToken()}`
                },
                body: JSON.stringify(data)
            });
        } else {
            // Создание
            response = await fetch(`${API_BASE}/deadlines`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getToken()}`
                },
                body: JSON.stringify(data)
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сохранения');
        }

        deadlineDialog.close();
        await loadClientDetails();
        alert(deadlineId ? 'Дедлайн успешно обновлен' : 'Дедлайн успешно добавлен');
    } catch (error) {
        console.error('Ошибка сохранения дедлайна:', error);
        alert(`Ошибка: ${error.message}`);
    }
}

// Удалить дедлайн
async function deleteDeadline(deadlineId) {
    if (!confirm('Вы уверены, что хотите удалить этот дедлайн?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/deadlines/${deadlineId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка удаления');
        }

        await loadClientDetails();
        alert('Дедлайн успешно удален');
    } catch (error) {
        console.error('Ошибка удаления дедлайна:', error);
        alert(`Ошибка: ${error.message}`);
    }
}

// Отправить дедлайны в Telegram
async function sendDeadlinesToTelegram() {
    if (!currentUserId) {
        alert('Не удалось определить ID клиента');
        return;
    }
    
    // Проверяем, подключен ли Telegram
    if (!clientData.telegram_id) {
        alert('Клиент не подключен к Telegram');
        return;
    }
    
    // Подтверждение отправки
    const clientName = clientData.company_name || clientData.full_name || 'клиенту';
    const totalDeadlines = (clientData.register_deadlines?.length || 0) + (clientData.general_deadlines?.length || 0);
    
    if (totalDeadlines === 0) {
        alert('У клиента нет активных дедлайнов для отправки');
        return;
    }
    
    if (!confirm(`Отправить ${totalDeadlines} дедлайн(ов) клиенту ${clientName} в Telegram?`)) {
        return;
    }
    
    // Отключаем кнопку и показываем индикатор загрузки
    const btn = document.getElementById('sendToTelegramBtn');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="material-icons" style="font-size: 16px; vertical-align: middle; margin-right: 6px;">hourglass_empty</i>Отправка...';
    
    try {
        const response = await fetch(`${API_BASE}/users/${currentUserId}/send-deadlines-telegram`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка отправки');
        }
        
        const result = await response.json();
        
        // Успех
        showNotification(result.message || 'Дедлайны успешно отправлены в Telegram!');
        
        // Возвращаем кнопку в исходное состояние с галочкой
        btn.innerHTML = '<i class="material-icons" style="font-size: 16px; vertical-align: middle; margin-right: 6px;">check</i>Отправлено';
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 2000);
        
    } catch (error) {
        console.error('Ошибка отправки дедлайнов:', error);
        alert(`Ошибка: ${error.message}`);
        
        // Возвращаем кнопку в исходное состояние
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Обработчики кнопок
document.addEventListener('DOMContentLoaded', function() {
    // Проверка авторизации
    if (!getToken()) {
        window.location.href = '/static/login.html';
        return;
    }

    // Установка имени пользователя
    const currentUser = getCurrentUser();
    if (currentUser) {
        document.getElementById('sidebarUserName').textContent = currentUser.username || currentUser.email;
    }

    // Кнопка выхода
    document.getElementById('sidebarLogoutBtn').addEventListener('click', function() {
        logout();
        window.location.href = '/static/login.html';
    });

    // Инициализация диалогов
    registerDialog = document.getElementById('registerDialog');
    deadlineDialog = document.getElementById('deadlineDialog');

    // Кнопки добавления
    document.getElementById('addRegisterBtn').addEventListener('click', showAddRegisterDialog);
    document.getElementById('addDeadlineBtn').addEventListener('click', showAddDeadlineDialog);
    document.getElementById('addRegisterDeadlineBtn').addEventListener('click', showAddRegisterDeadlineDialog);

    // Кнопки сохранения в диалогах
    document.getElementById('saveRegisterBtn').addEventListener('click', saveRegister);
    document.getElementById('saveDeadlineBtn').addEventListener('click', saveDeadline);

    // Кнопки закрытия диалогов
    document.getElementById('closeRegisterDialog').addEventListener('click', function() {
        registerDialog.close();
    });
    document.getElementById('closeDeadlineDialog').addEventListener('click', function() {
        deadlineDialog.close();
    });
    
    // Кнопка отправки в Telegram
    const sendToTelegramBtn = document.getElementById('sendToTelegramBtn');
    if (sendToTelegramBtn) {
        sendToTelegramBtn.addEventListener('click', sendDeadlinesToTelegram);
    }

    // Загрузка данных
    Promise.all([
        loadDeadlineTypes(),
        loadOFDProviders()
    ]).then(() => {
        loadClientDetails();
    });
});
