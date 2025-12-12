// Константы API
const API_BASE_URL = 'http://localhost:8000/api';

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

    // Загрузка данных дашборда
    await loadDashboardData();

    // Настройка кнопки выхода
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
});

// Загрузка данных дашборда
async function loadDashboardData() {
    try {
        const token = localStorage.getItem('access_token');

        // Параллельная загрузка всех данных
        const [summaryResponse, urgentResponse, typesResponse] = await Promise.all([
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
            }),
            fetch(`${API_BASE_URL}/deadline-types`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            })
        ]);

        if (!summaryResponse.ok) {
            if (summaryResponse.status === 401) {
                handleLogout();
                return;
            }
            throw new Error('Ошибка загрузки данных');
        }

        const summaryData = await summaryResponse.json();
        const urgentData = urgentResponse.ok ? await urgentResponse.json() : [];
        const typesData = typesResponse.ok ? await typesResponse.json() : [];

        // Обновление карточек статистики
        updateStatisticsCards(summaryData);

        // Отрисовка графиков
        renderStatusChart(summaryData);
        renderTypeChart(typesData);  // Теперь с реальными данными

        // Заполнение таблицы срочных дедлайнов
        renderUrgentDeadlines(urgentData);  // Теперь с реальными данными

    } catch (error) {
        console.error('Ошибка при загрузке данных дашборда:', error);
        showError('Не удалось загрузить данные дашборда');
    }
}

// Обновление карточек статистики
function updateStatisticsCards(data) {
    // Всего клиентов
    const totalClientsEl = document.getElementById('totalClients');
    if (totalClientsEl) totalClientsEl.textContent = data.total_clients || 0;

    // Активных клиентов
    const activeClientsEl = document.getElementById('activeClients');
    if (activeClientsEl) activeClientsEl.textContent = data.active_clients || 0;

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

// Отрисовка графика статусов
function renderStatusChart(data) {
    const ctx = document.getElementById('statusChart');
    if (!ctx) return;

    const chartData = {
        labels: [
            `Норма (>${14} дн.)`,
            `Внимание (7-14 дн.)`,
            `Срочно (0-7 дн.)`,
            `Просрочено`
        ],
        datasets: [{
            data: [
                data.status_green || 0,
                data.status_yellow || 0,
                data.status_red || 0,
                data.status_expired || 0
            ],
            backgroundColor: [
                'rgba(76, 175, 80, 0.8)',   // Зеленый
                'rgba(255, 193, 7, 0.8)',   // Желтый
                'rgba(244, 67, 54, 0.8)',   // Красный
                'rgba(158, 158, 158, 0.8)'  // Серый
            ],
            borderColor: [
                'rgba(76, 175, 80, 1)',
                'rgba(255, 193, 7, 1)',
                'rgba(244, 67, 54, 1)',
                'rgba(158, 158, 158, 1)'
            ],
            borderWidth: 2
        }]
    };

    new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { size: 12 },
                        padding: 15
                    }
                },
                title: {
                    display: false
                }
            }
        }
    });
}

// Отрисовка графика по типам услуг
function renderTypeChart(typeStats) {
    const ctx = document.getElementById('typeChart');
    if (!ctx) return;

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

    new Chart(ctx, {
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

// Отрисовка таблицы срочных дедлайнов
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
        const daysRemaining = deadline.days_remaining;

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

        // Форматирование даты
        const expirationDate = new Date(deadline.expiration_date);
        const formattedDate = expirationDate.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });

        row.innerHTML = `
            <td class="mdl-data-table__cell--non-numeric">${deadline.client_name || 'Не указан'}</td>
            <td class="mdl-data-table__cell--non-numeric">${deadline.deadline_type || 'Не указан'}</td>
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

// Обработка выхода
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
}

// Отображение ошибки
function showError(message) {
    const snackbar = document.getElementById('demo-snackbar');
    if (snackbar && snackbar.MaterialSnackbar) {
        snackbar.MaterialSnackbar.showSnackbar({ message });
    } else {
        alert(message);
    }
}
