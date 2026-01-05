// Константы API (если ещё не объявлены)
if (typeof API_BASE_URL === 'undefined') {
    var API_BASE_URL = window.location.origin + '/api';
}

// Глобальные переменные для хранения экземпляров графиков
let statusChartInstance = null;
let typeChartInstance = null;

// Проверка авторизации при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    if (!token) {
        window.location.href = '/login.html';
        return;
    }

    // Отображение имени пользователя
    const userElement = document.getElementById('userName');
    if (userElement) {
        userElement.textContent = user.full_name || user.username || 'Пользователь';
    }
    
    // Инициализация навигации
    initNavigation();
    
    // Фильтрация меню по роли пользователя
    filterMenuByRole(user.role);
    
    // Восстановление последней активной секции или переход по hash
    const hash = window.location.hash.substring(1);
    const lastSection = hash || localStorage.getItem('lastActiveSection') || 'statistics';
    switchSection(lastSection);

    // Настройка кнопок выхода
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    const sidebarLogoutBtn = document.getElementById('sidebarLogoutBtn');
    if (sidebarLogoutBtn) {
        sidebarLogoutBtn.addEventListener('click', handleLogout);
    }
    
    // Обновление имени пользователя в сайдбаре
    const sidebarUserName = document.getElementById('sidebarUserName');
    if (sidebarUserName) {
        sidebarUserName.textContent = user.full_name || user.username || 'Пользователь';
    }
});

// Загрузка данных дашборда
async function loadDashboardData() {
    console.log('📊 Загрузка данных дашборда...');
    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            console.error('❌ Нет токена авторизации');
            handleLogout();
            return;
        }

        console.log('🔑 Токен найден, запуск параллельных запросов...');
        
        // Параллельная загрузка данных (убрана загрузка deadline-types)
        const [summaryResponse, urgentResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/dashboard/stats`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }),
            fetch(`${API_BASE_URL}/deadlines/urgent?days=14`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            })
        ]);

        console.log('📊 Статусы ответов:', {
            summary: summaryResponse.status,
            urgent: urgentResponse.status
        });

        if (!summaryResponse.ok) {
            console.error('❌ Ошибка загрузки статистики:', summaryResponse.status);
            console.error('❌ URL запроса:', `${API_BASE_URL}/dashboard/stats`);
            console.error('❌ Полный URL:', summaryResponse.url);
            if (summaryResponse.status === 401) {
                console.log('🚫 Неавторизован, перенаправление на логин');
                handleLogout();
                return;
            }
            const errorText = await summaryResponse.text();
            console.error('❌ Текст ошибки:', errorText);
            showError(`Не удалось загрузить данные дашборда: ${summaryResponse.status} - ${errorText}`);
            throw new Error(`Ошибка загрузки данных: ${summaryResponse.status}`);
        }

        console.log('✅ Парсинг данных...');
        const summaryData = await summaryResponse.json();
        const urgentData = urgentResponse.ok ? await urgentResponse.json() : [];

        console.log('✅ Данные получены:', {
            summary: summaryData,
            urgentCount: urgentData.length
        });

        // Обновление карточек статистики
        console.log('📊 Обновление карточек статистики...');
        updateStatisticsCards(summaryData);

        // Отрисовка графиков - УБРАНО
        // console.log('📊 Отрисовка графиков...');
        // renderStatusChart(summaryData);
        // renderTypeChart(typesData);

        // Заполнение таблицы срочных дедлайнов
        console.log('📊 Отрисовка таблицы срочных дедлайнов...');
        renderUrgentDeadlines(urgentData);

        console.log('✅ Дашборд успешно загружен!');

    } catch (error) {
        console.error('❌ Ошибка при загрузке данных дашборда:', error);
        console.error('❌ Stack trace:', error.stack);
        console.error('❌ Тип ошибки:', error.name);
        console.error('❌ Сообщение:', error.message);
        showError(`Не удалось отобразить данные дашборда: ${error.message}`);
    }
}

// Обновление карточек статистики
function updateStatisticsCards(data) {
    console.log('[DEBUG] updateStatisticsCards вызван с данными:', data);
    
    // Всего клиентов
    const totalClientsEl = document.getElementById('totalClients');
    if (totalClientsEl) totalClientsEl.textContent = data.total_clients || 0;

    // Активных клиентов
    const activeClientsEl = document.getElementById('activeClients');
    if (activeClientsEl) activeClientsEl.textContent = data.active_clients || 0;

    // Всего касс
    const totalCashRegistersEl = document.getElementById('totalCashRegisters');
    console.log('[DEBUG] totalCashRegisters элемент:', totalCashRegistersEl);
    console.log('[DEBUG] total_cash_registers из data:', data.total_cash_registers);
    if (totalCashRegistersEl) {
        totalCashRegistersEl.textContent = data.total_cash_registers || 0;
        console.log('[DEBUG] Значение установлено:', totalCashRegistersEl.textContent);
    } else {
        console.error('[ERROR] Элемент totalCashRegisters не найден!');
    }

    // Всего сроков
    const totalDeadlinesEl = document.getElementById('totalDeadlines');
    if (totalDeadlinesEl) totalDeadlinesEl.textContent = data.total_deadlines || 0;

    // Срочных дедлайнов (красные + желтые)
    const urgentCount = (data.status_red || 0) + (data.status_yellow || 0);
    const urgentCountEl = document.getElementById('urgentCount');
    if (urgentCountEl) urgentCountEl.textContent = urgentCount;

    // Просроченных
    const expiredCountEl = document.getElementById('expiredCount');
    if (expiredCountEl) expiredCountEl.textContent = data.status_expired || 0;
}

// Отрисовка графика статусов (линейная диаграмма)
function renderStatusChart(data) {
    const ctx = document.getElementById('statusChart');
    if (!ctx) return;

    // Уничтожаем предыдущий график, если он существует
    if (statusChartInstance) {
        statusChartInstance.destroy();
        statusChartInstance = null;
    }

    const chartData = {
        labels: [
            `Норма (>${14} дн.)`,
            `Внимание (7-14 дн.)`,
            `Срочно (0-7 дн.)`,
            `Просрочено`
        ],
        datasets: [{
            label: 'Количество дедлайнов',
            data: [
                data.status_green || 0,
                data.status_yellow || 0,
                data.status_red || 0,
                data.status_expired || 0
            ],
            backgroundColor: [
                'rgba(76, 175, 80, 0.2)',   // Зеленый
                'rgba(255, 193, 7, 0.2)',   // Желтый
                'rgba(244, 67, 54, 0.2)',   // Красный
                'rgba(158, 158, 158, 0.2)'  // Серый
            ],
            borderColor: [
                'rgba(76, 175, 80, 1)',
                'rgba(255, 193, 7, 1)',
                'rgba(244, 67, 54, 1)',
                'rgba(158, 158, 158, 1)'
            ],
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: [
                'rgba(76, 175, 80, 1)',
                'rgba(255, 193, 7, 1)',
                'rgba(244, 67, 54, 1)',
                'rgba(158, 158, 158, 1)'
            ],
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 7
        }]
    };

    statusChartInstance = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        font: { size: 12 },
                        padding: 15
                    }
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Отрисовка графика по типам услуг
function renderTypeChart(typeStats) {
    const ctx = document.getElementById('typeChart');
    if (!ctx) return;

    // Уничтожаем предыдущий график, если он существует
    if (typeChartInstance) {
        typeChartInstance.destroy();
        typeChartInstance = null;
    }

    // Если данные пришли как массив типов, а не статистика,
    // просто показываем названия типов
    let labels, counts;
    
    if (Array.isArray(typeStats) && typeStats.length > 0) {
        // Если пришел массив типов (type_name, etc)
        if (typeStats[0].type_name) {
            labels = typeStats.map(stat => stat.type_name || 'Не указан');
            // Пока нет статистики, используем 0
            counts = typeStats.map(() => 0);
        } else {
            // Если пришла статистика
            labels = typeStats.map(stat => stat.deadline_type || 'Не указан');
            counts = typeStats.map(stat => stat.count || 0);
        }
    } else {
        labels = ['Нет данных'];
        counts = [0];
    }

    const data = {
        labels: labels,
        datasets: [{
            label: 'Количество сроков',
            data: counts,
            backgroundColor: [
                'rgba(102, 126, 234, 0.8)',
                'rgba(118, 75, 162, 0.8)',
                'rgba(237, 100, 166, 0.8)',
                'rgba(255, 154, 158, 0.8)',
                'rgba(250, 208, 196, 0.8)',
                'rgba(165, 177, 194, 0.8)'
            ],
            borderColor: [
                'rgba(102, 126, 234, 1)',
                'rgba(118, 75, 162, 1)',
                'rgba(237, 100, 166, 1)',
                'rgba(255, 154, 158, 1)',
                'rgba(250, 208, 196, 1)',
                'rgba(165, 177, 194, 1)'
            ],
            borderWidth: 2
        }]
    };

    typeChartInstance = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Отрисовка таблицы срочных дедлайнов (включая просроченные)
function renderUrgentDeadlines(deadlines) {
    const tableBody = document.getElementById('urgentDeadlinesTable');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    if (!deadlines || deadlines.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 20px; color: #999;">
                    Нет срочных дедлайнов
                </td>
            </tr>
        `;
        return;
    }

    deadlines.forEach(deadline => {
        const row = document.createElement('tr');
        
        // Определение статуса и цвета
        let statusText = '';
        let statusColor = '';
        const daysRemaining = deadline.days_until_expiration;

        if (daysRemaining < 0) {
            statusText = 'Просрочено';
            statusColor = '#9E9E9E';
        } else if (daysRemaining <= 7) {
            statusText = 'Срочно';
            statusColor = '#F44336';
        } else if (daysRemaining <= 14) {
            statusText = 'Внимание';
            statusColor = '#FFC107';
        } else {
            statusText = 'Норма';
            statusColor = '#4CAF50';
        }

        // Форматирование даты в российский формат ДД.ММ.ГГГГ
        const formattedDate = formatDateRU(deadline.expiration_date);
        
        // Получение имени клиента и типа дедлайна
        const clientName = deadline.client?.company_name || 'Не указан';
        const deadlineType = deadline.deadline_type?.name || deadline.deadline_type?.type_name || 'Не указан';
        
        console.log('📖 Дедлайн ID=' + deadline.id + ':', {
            client: deadline.client,
            deadline_type: deadline.deadline_type,
            clientName,
            deadlineType
        });

        row.innerHTML = `
            <td class="mdl-data-table__cell--non-numeric">${clientName}</td>
            <td class="mdl-data-table__cell--non-numeric">${deadlineType}</td>
            <td class="mdl-data-table__cell--non-numeric">${formattedDate}</td>
            <td class="mdl-data-table__cell--non-numeric" style="font-weight: bold; color: ${statusColor};">
                ${daysRemaining} дн.
            </td>
            <td class="mdl-data-table__cell--non-numeric">
                <span style="background-color: ${statusColor}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">
                    ${statusText}
                </span>
            </td>
        `;

        tableBody.appendChild(row);
    });
}

// Инициализация навигации
function initNavigation() {
    // Обработчики кликов на элементы навигации
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            const section = item.dataset.section;
            if (section) {
                // Только для элементов с data-section блокируем переход
                e.preventDefault();
                switchSection(section);
                window.location.hash = section;
            }
            // Для элементов без data-section разрешаем обычный переход по ссылке
        });
    });
    
    // Обработчик изменения hash (browser back/forward)
    window.addEventListener('hashchange', () => {
        const hash = window.location.hash.substring(1);
        if (hash) {
            switchSection(hash);
        }
    });
}

// Переключение между разделами
function switchSection(sectionId) {
    console.log('🔄 switchSection вызван для:', sectionId);
    
    // Скрыть все секции
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
        section.classList.add('hidden');
    });
    
    // Убрать активность со всех пунктов меню
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Показать выбранную секцию
    const targetSection = document.getElementById(`${sectionId}-section`);
    if (targetSection) {
        console.log('✅ Секция найдена:', `${sectionId}-section`);
        targetSection.classList.add('active');
        targetSection.classList.remove('hidden');
    } else {
        console.error('❌ Секция НЕ найдена:', `${sectionId}-section`);
    }
    
    // Активировать соответствующий пункт меню
    const navItem = document.querySelector(`[data-section="${sectionId}"]`);
    if (navItem) {
        navItem.classList.add('active');
    }
    
    // Обновить заголовок страницы
    const sectionTitles = {
        'statistics': 'Управление Дедлайнами',
        'users': 'Клиенты',
        'deadlines': 'Дедлайны',
        'deadline-types': 'Типы дедлайнов',
        'managers': 'Пользователи',
        'export': 'Экспорт данных'
    };
    document.title = `${sectionTitles[sectionId] || 'Управление Дедлайнами'} - Релабс Центр`;
    
    // Загрузить данные для секции
    loadSectionData(sectionId);
    
    // Сохранить в localStorage
    localStorage.setItem('lastActiveSection', sectionId);
}

// Загрузка данных для конкретной секции
function loadSectionData(sectionId) {
    console.log('🔵 loadSectionData вызван для:', sectionId);
    switch(sectionId) {
        case 'statistics':
            console.log('📊 Загрузка статистики');
            loadDashboardData();
            break;
        case 'users':
            console.log('👥 Проверка функции loadUsersData:', typeof loadUsersData);
            if (typeof loadUsersData === 'function') {
                console.log('✅ Вызов loadUsersData()');
                loadUsersData();
            } else {
                console.error('❌ loadUsersData не определена!');
            }
            break;
        case 'deadlines':
            console.log('⏰ Проверка функции loadDeadlinesData:', typeof loadDeadlinesData);
            if (typeof loadDeadlinesData === 'function') {
                console.log('✅ Вызов loadDeadlinesData()');
                loadDeadlinesData();
            } else {
                console.error('❌ loadDeadlinesData не определена!');
            }
            break;
        case 'deadline-types':
            console.log('📋 Проверка функции loadDeadlineTypesData:', typeof loadDeadlineTypesData);
            if (typeof loadDeadlineTypesData === 'function') {
                console.log('✅ Вызов loadDeadlineTypesData()');
                loadDeadlineTypesData();
            } else {
                console.error('❌ loadDeadlineTypesData не определена!');
            }
            break;
        case 'managers':
            console.log('👤 Проверка функции loadManagersData:', typeof loadManagersData);
            if (typeof loadManagersData === 'function') {
                console.log('✅ Вызов loadManagersData()');
                loadManagersData();
            } else {
                console.error('❌ loadManagersData не определена!');
            }
            break;
        case 'export':
            console.log('📥 Проверка функции loadExportData:', typeof loadExportData);
            if (typeof loadExportData === 'function') {
                console.log('✅ Вызов loadExportData()');
                loadExportData();
            } else {
                console.error('❌ loadExportData не определена!');
            }
            break;
    }
}

// Фильтрация меню по роли пользователя
function filterMenuByRole(role) {
    // Общая обработка всех элементов с data-role
    document.querySelectorAll('[data-role]').forEach(item => {
        const allowedRoles = item.dataset.role.split(',').map(r => r.trim());
        if (!allowedRoles.includes(role)) {
            item.style.display = 'none';
        }
    });
    
    // Для клиентов показываем только их данные
    if (role === 'client') {
        // Раздел "Клиенты" переименовываем в "Мои данные"
        const usersNavItem = document.querySelector('[data-section="users"]');
        if (usersNavItem) {
            const span = usersNavItem.querySelector('span');
            if (span) span.textContent = 'Мои данные';
        }
    }
}

// Обработка выхода
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('lastActiveSection');
    window.location.href = '/login.html';
}

// Отображение ошибки
function showError(message) {
    console.error('❌ ОШИБКА:', message);
    
    // Попытка использовать snackbar
    const snackbar = document.getElementById('demo-snackbar');
    if (snackbar && snackbar.MaterialSnackbar) {
        snackbar.MaterialSnackbar.showSnackbar({ 
            message: message,
            timeout: 5000 
        });
    } else {
        // Fallback на alert если snackbar недоступен
        console.warn('⚠️ Snackbar недоступен, используется alert');
        alert(message);
    }
}

// Функции навигации для кликабельных карточек статистики
function navigateToClients() {
    // Сбрасываем фильтр неактивных клиентов
    if (typeof showInactiveUsers !== 'undefined') {
        showInactiveUsers = false;
    }
    switchSection('users');
    window.location.hash = 'users';
}

function navigateToAllDeadlines() {
    switchSection('deadlines');
    window.location.hash = 'deadlines';
    // Сбросим все фильтры для отображения всех дедлайнов
    setTimeout(() => {
        if (typeof resetFilters === 'function') {
            resetFilters();
        }
    }, 100);
}

function navigateToUrgentDeadlines() {
    switchSection('deadlines');
    window.location.hash = 'deadlines';
    // Установим фильтр для срочных дедлайнов (0-7 дней)
    setTimeout(() => {
        // Дождемся загрузки данных и отрисовки фильтров
        const checkAndApply = () => {
            const filterDays = document.getElementById('filterDays');
            if (filterDays) {
                filterDays.value = 'urgent';
                if (typeof applyFilters === 'function') {
                    applyFilters();
                }
            } else {
                // Если элемент еще не появился, повторим через 50мс
                setTimeout(checkAndApply, 50);
            }
        };
        checkAndApply();
    }, 100);
}

function navigateToExpiredDeadlines() {
    switchSection('deadlines');
    window.location.hash = 'deadlines';
    // Установим фильтр для просроченных дедлайнов
    setTimeout(() => {
        // Дождемся загрузки данных и отрисовки фильтров
        const checkAndApply = () => {
            const filterDays = document.getElementById('filterDays');
            if (filterDays) {
                filterDays.value = 'expired';
                if (typeof applyFilters === 'function') {
                    applyFilters();
                }
            } else {
                // Если элемент еще не появился, повторим через 50мс
                setTimeout(checkAndApply, 50);
            }
        };
        checkAndApply();
    }, 100);
}
