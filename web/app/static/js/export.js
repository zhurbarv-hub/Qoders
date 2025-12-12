/**
 * Экспорт данных
 */

// Константы API (если ещё не объявлены)
if (typeof API_BASE_URL === 'undefined') {
    var API_BASE_URL = window.location.origin + '/api';
}

const exportSection = document.getElementById('export-section');

/**
 * Загрузка раздела экспорта
 */
async function loadExportData() {
    renderExportPage();
}

/**
 * Отображение страницы экспорта
 */
function renderExportPage() {
    const html = `
        <div class="section-header">
            <h2>📥 Экспорт данных</h2>
        </div>
        
        <div class="mdl-grid">
            <!-- Экспорт клиентов -->
            <div class="mdl-cell mdl-cell--6-col mdl-cell--12-col-tablet">
                <div class="mdl-card mdl-shadow--2dp" style="width: 100%;">
                    <div class="mdl-card__title mdl-color--primary mdl-color-text--white">
                        <h2 class="mdl-card__title-text">👥 Клиенты</h2>
                    </div>
                    <div class="mdl-card__supporting-text">
                        <p>Экспортировать список всех клиентов с их контактными данными</p>
                        <ul>
                            <li>Название компании</li>
                            <li>ИНН</li>
                            <li>Контактное лицо</li>
                            <li>Email, телефон</li>
                            <li>Telegram ID</li>
                        </ul>
                    </div>
                    <div class="mdl-card__actions mdl-card--border">
                        <button class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" 
                                onclick="exportClients('excel')">
                            <i class="material-icons">download</i> Excel
                        </button>
                        <button class="mdl-button mdl-js-button mdl-button--raised" 
                                onclick="exportClients('csv')">
                            <i class="material-icons">download</i> CSV
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Экспорт дедлайнов -->
            <div class="mdl-cell mdl-cell--6-col mdl-cell--12-col-tablet">
                <div class="mdl-card mdl-shadow--2dp" style="width: 100%;">
                    <div class="mdl-card__title mdl-color--primary mdl-color-text--white">
                        <h2 class="mdl-card__title-text">⏰ Дедлайны</h2>
                    </div>
                    <div class="mdl-card__supporting-text">
                        <p>Экспортировать список всех дедлайнов</p>
                        <ul>
                            <li>Клиент</li>
                            <li>Тип услуги</li>
                            <li>Дата истечения</li>
                            <li>Статус</li>
                            <li>Уведомления</li>
                        </ul>
                    </div>
                    <div class="mdl-card__actions mdl-card--border">
                        <button class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" 
                                onclick="exportDeadlines('excel')">
                            <i class="material-icons">download</i> Excel
                        </button>
                        <button class="mdl-button mdl-js-button mdl-button--raised" 
                                onclick="exportDeadlines('csv')">
                            <i class="material-icons">download</i> CSV
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Экспорт типов услуг -->
            <div class="mdl-cell mdl-cell--6-col mdl-cell--12-col-tablet">
                <div class="mdl-card mdl-shadow--2dp" style="width: 100%;">
                    <div class="mdl-card__title mdl-color--primary mdl-color-text--white">
                        <h2 class="mdl-card__title-text">📋 Типы услуг</h2>
                    </div>
                    <div class="mdl-card__supporting-text">
                        <p>Экспортировать справочник типов услуг</p>
                        <ul>
                            <li>Название типа</li>
                            <li>Описание</li>
                            <li>Дней до уведомления</li>
                            <li>Статус активности</li>
                        </ul>
                    </div>
                    <div class="mdl-card__actions mdl-card--border">
                        <button class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" 
                                onclick="exportDeadlineTypes('excel')">
                            <i class="material-icons">download</i> Excel
                        </button>
                        <button class="mdl-button mdl-js-button mdl-button--raised" 
                                onclick="exportDeadlineTypes('csv')">
                            <i class="material-icons">download</i> CSV
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Полный экспорт -->
            <div class="mdl-cell mdl-cell--6-col mdl-cell--12-col-tablet">
                <div class="mdl-card mdl-shadow--2dp" style="width: 100%;">
                    <div class="mdl-card__title" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <h2 class="mdl-card__title-text">📦 Полный экспорт</h2>
                    </div>
                    <div class="mdl-card__supporting-text">
                        <p>Экспортировать все данные системы в одном архиве</p>
                        <ul>
                            <li>Все клиенты</li>
                            <li>Все дедлайны</li>
                            <li>Все типы услуг</li>
                            <li>Статистика</li>
                        </ul>
                    </div>
                    <div class="mdl-card__actions mdl-card--border">
                        <button class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" 
                                onclick="exportAll()">
                            <i class="material-icons">archive</i> Экспортировать всё
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Статус экспорта -->
        <div id="exportStatus" style="margin-top: 20px;"></div>
    `;
    
    exportSection.innerHTML = html;
    
    // Обновляем MDL компоненты
    if (typeof componentHandler !== 'undefined') {
        componentHandler.upgradeDom();
    }
}

/**
 * Экспорт клиентов
 */
async function exportClients(format) {
    showExportStatus('Подготовка экспорта клиентов...', 'info');
    
    try {
        const token = localStorage.getItem('access_token');
        
        const response = await fetch(`${API_BASE_URL}/export/clients?format=${format}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка экспорта клиентов');
        }
        
        // Получаем файл и сохраняем
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `clients_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showExportStatus('✅ Клиенты успешно экспортированы', 'success');
    } catch (error) {
        console.error('Ошибка при экспорте клиентов:', error);
        showExportStatus('❌ Ошибка при экспорте клиентов', 'error');
    }
}

/**
 * Экспорт дедлайнов
 */
async function exportDeadlines(format) {
    showExportStatus('Подготовка экспорта дедлайнов...', 'info');
    
    try {
        const token = localStorage.getItem('access_token');
        
        const response = await fetch(`${API_BASE_URL}/export/deadlines?format=${format}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка экспорта дедлайнов');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `deadlines_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showExportStatus('✅ Дедлайны успешно экспортированы', 'success');
    } catch (error) {
        console.error('Ошибка при экспорте дедлайнов:', error);
        showExportStatus('❌ Ошибка при экспорте дедлайнов', 'error');
    }
}

/**
 * Экспорт типов услуг
 */
async function exportDeadlineTypes(format) {
    showExportStatus('Подготовка экспорта типов услуг...', 'info');
    
    try {
        const token = localStorage.getItem('access_token');
        
        const response = await fetch(`${API_BASE_URL}/export/deadline-types?format=${format}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка экспорта типов услуг');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `deadline_types_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showExportStatus('✅ Типы услуг успешно экспортированы', 'success');
    } catch (error) {
        console.error('Ошибка при экспорте типов услуг:', error);
        showExportStatus('❌ Ошибка при экспорте типов услуг', 'error');
    }
}

/**
 * Полный экспорт
 */
async function exportAll() {
    showExportStatus('Подготовка полного экспорта данных...', 'info');
    
    try {
        const token = localStorage.getItem('access_token');
        
        const response = await fetch(`${API_BASE_URL}/export/all`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка полного экспорта');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `kkt_full_export_${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showExportStatus('✅ Данные успешно экспортированы', 'success');
    } catch (error) {
        console.error('Ошибка при полном экспорте:', error);
        showExportStatus('❌ Ошибка при экспорте данных', 'error');
    }
}

/**
 * Показать статус экспорта
 */
function showExportStatus(message, type) {
    const statusDiv = document.getElementById('exportStatus');
    if (!statusDiv) return;
    
    const colors = {
        'info': '#2196F3',
        'success': '#4CAF50',
        'error': '#F44336'
    };
    
    statusDiv.innerHTML = `
        <div class="mdl-card mdl-shadow--2dp" style="width: 100%; padding: 15px; background: ${colors[type]}; color: white;">
            <p style="margin: 0; font-size: 16px;">${message}</p>
        </div>
    `;
    
    // Автоматически скрыть сообщение через 5 секунд
    if (type !== 'info') {
        setTimeout(() => {
            statusDiv.innerHTML = '';
        }, 5000);
    }
}
