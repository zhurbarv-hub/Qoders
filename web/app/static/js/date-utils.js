/**
 * Утилиты для работы с датами в российском формате
 * Все даты отображаются в формате ДД.ММ.ГГГГ
 */

/**
 * Форматирование даты в российский формат ДД.ММ.ГГГГ
 * @param {string|Date} dateInput - Дата в формате ISO (YYYY-MM-DD) или объект Date
 * @returns {string} Дата в формате ДД.ММ.ГГГГ
 */
function formatDateRU(dateInput) {
    if (!dateInput) return '-';
    
    try {
        const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;
        
        // Проверка на валидность даты
        if (isNaN(date.getTime())) {
            return '-';
        }
        
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        
        return `${day}.${month}.${year}`;
    } catch (error) {
        console.error('Ошибка форматирования даты:', error);
        return '-';
    }
}

/**
 * Форматирование даты и времени в российский формат ДД.ММ.ГГГГ ЧЧ:ММ
 * @param {string|Date} dateInput - Дата/время
 * @returns {string} Дата и время в формате ДД.ММ.ГГГГ ЧЧ:ММ
 */
function formatDateTimeRU(dateInput) {
    if (!dateInput) return '-';
    
    try {
        const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;
        
        // Проверка на валидность даты
        if (isNaN(date.getTime())) {
            return '-';
        }
        
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        return `${day}.${month}.${year} ${hours}:${minutes}`;
    } catch (error) {
        console.error('Ошибка форматирования даты и времени:', error);
        return '-';
    }
}

/**
 * Конвертация даты из формата ДД.ММ.ГГГГ в ISO формат YYYY-MM-DD
 * @param {string} dateStr - Дата в формате ДД.ММ.ГГГГ
 * @returns {string} Дата в формате YYYY-MM-DD для отправки на сервер
 */
function parseRUDateToISO(dateStr) {
    if (!dateStr || dateStr === '-') return null;
    
    try {
        const parts = dateStr.split('.');
        if (parts.length !== 3) return null;
        
        const day = parts[0].padStart(2, '0');
        const month = parts[1].padStart(2, '0');
        const year = parts[2];
        
        return `${year}-${month}-${day}`;
    } catch (error) {
        console.error('Ошибка парсинга российской даты:', error);
        return null;
    }
}

/**
 * Форматирование даты для input[type="date"]
 * Input элементы требуют формат YYYY-MM-DD
 * @param {string|Date} dateInput - Дата
 * @returns {string} Дата в формате YYYY-MM-DD
 */
function formatDateForInput(dateInput) {
    if (!dateInput) return '';
    
    try {
        const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;
        
        // Проверка на валидность даты
        if (isNaN(date.getTime())) {
            return '';
        }
        
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        
        return `${year}-${month}-${day}`;
    } catch (error) {
        console.error('Ошибка форматирования даты для input:', error);
        return '';
    }
}

/**
 * Получение текущей даты в российском формате
 * @returns {string} Текущая дата в формате ДД.ММ.ГГГГ
 */
function getCurrentDateRU() {
    return formatDateRU(new Date());
}

/**
 * Получение текущей даты и времени в российском формате
 * @returns {string} Текущая дата и время в формате ДД.ММ.ГГГГ ЧЧ:ММ
 */
function getCurrentDateTimeRU() {
    return formatDateTimeRU(new Date());
}

/**
 * Форматирование даты для имени файла (ГГГГMMДД)
 * @param {Date} date - Дата (по умолчанию текущая)
 * @returns {string} Дата в формате ГГГГMMДД
 */
function formatDateForFilename(date = new Date()) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    return `${year}${month}${day}`;
}

// Экспорт функций для использования в других модулях
if (typeof window !== 'undefined') {
    window.formatDateRU = formatDateRU;
    window.formatDateTimeRU = formatDateTimeRU;
    window.parseRUDateToISO = parseRUDateToISO;
    window.formatDateForInput = formatDateForInput;
    window.getCurrentDateRU = getCurrentDateRU;
    window.getCurrentDateTimeRU = getCurrentDateTimeRU;
    window.formatDateForFilename = formatDateForFilename;
}
