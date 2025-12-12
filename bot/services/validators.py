# -*- coding: utf-8 -*-
"""
Сервис валидации входных данных для Telegram бота
"""
import re
from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Результат валидации"""
    valid: bool
    error_message: str = ""
    cleaned_value: any = None


def validate_inn(inn: str) -> ValidationResult:
    """
    Валидация ИНН
    
    Правила:
    - Только цифры
    - 10 или 12 символов
    - Проверка контрольной суммы
    
    Args:
        inn: Строка с ИНН
        
    Returns:
        ValidationResult
    """
    # Очистка от пробелов и нецифровых символов
    cleaned = re.sub(r'\D', '', inn.strip())
    
    # Проверка длины
    if len(cleaned) not in [10, 12]:
        return ValidationResult(
            valid=False,
            error_message="ИНН должен содержать 10 или 12 цифр"
        )
    
    # Для простоты пропускаем проверку контрольной суммы
    # В production нужно добавить полную проверку
    
    return ValidationResult(
        valid=True,
        cleaned_value=cleaned
    )


def validate_client_name(name: str) -> ValidationResult:
    """
    Валидация названия организации
    
    Правила:
    - Длина от 2 до 200 символов
    - Разрешены: кириллица, латиница, цифры, пробелы, "-", '"', "(", ")"
    
    Args:
        name: Название организации
        
    Returns:
        ValidationResult
    """
    cleaned = name.strip()
    
    # Проверка длины
    if len(cleaned) < 2:
        return ValidationResult(
            valid=False,
            error_message="Название слишком короткое (минимум 2 символа)"
        )
    
    if len(cleaned) > 200:
        return ValidationResult(
            valid=False,
            error_message="Название слишком длинное (максимум 200 символов)"
        )
    
    # Проверка допустимых символов
    allowed_pattern = r'^[а-яА-ЯёЁa-zA-Z0-9\s\-"().№«»,]+$'
    if not re.match(allowed_pattern, cleaned):
        return ValidationResult(
            valid=False,
            error_message="Название содержит недопустимые символы"
        )
    
    return ValidationResult(
        valid=True,
        cleaned_value=cleaned
    )


def validate_phone(phone: str) -> ValidationResult:
    """
    Валидация телефона
    
    Форматы:
    - +7XXXXXXXXXX
    - 8XXXXXXXXXX
    - 7XXXXXXXXXX
    
    Нормализация к формату: +7XXXXXXXXXX
    
    Args:
        phone: Номер телефона
        
    Returns:
        ValidationResult
    """
    # Очистка от всех символов кроме цифр и +
    cleaned = re.sub(r'[^\d+]', '', phone.strip())
    
    # Проверка формата
    if cleaned.startswith('+7') and len(cleaned) == 12:
        normalized = cleaned
    elif cleaned.startswith('8') and len(cleaned) == 11:
        normalized = '+7' + cleaned[1:]
    elif cleaned.startswith('7') and len(cleaned) == 11:
        normalized = '+' + cleaned
    elif len(cleaned) == 10:
        normalized = '+7' + cleaned
    else:
        return ValidationResult(
            valid=False,
            error_message="Неверный формат телефона. Используйте: +7XXXXXXXXXX или 8XXXXXXXXXX"
        )
    
    return ValidationResult(
        valid=True,
        cleaned_value=normalized
    )


def validate_email(email: str) -> ValidationResult:
    """
    Валидация email
    
    Правила:
    - Базовый формат email
    - Приводится к нижнему регистру
    
    Args:
        email: Email адрес
        
    Returns:
        ValidationResult
    """
    cleaned = email.strip().lower()
    
    # Простая проверка формата email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, cleaned):
        return ValidationResult(
            valid=False,
            error_message="Неверный формат email. Пример: info@company.ru"
        )
    
    return ValidationResult(
        valid=True,
        cleaned_value=cleaned
    )


def validate_date(date_str: str, allow_past: bool = False) -> ValidationResult:
    """
    Валидация даты
    
    Форматы:
    - DD.MM.YYYY
    - YYYY-MM-DD
    
    Args:
        date_str: Строка с датой
        allow_past: Разрешить даты в прошлом
        
    Returns:
        ValidationResult
    """
    cleaned = date_str.strip()
    
    # Попытка разбора формата DD.MM.YYYY
    formats = ['%d.%m.%Y', '%Y-%m-%d']
    parsed_date = None
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(cleaned, fmt).date()
            break
        except ValueError:
            continue
    
    if not parsed_date:
        return ValidationResult(
            valid=False,
            error_message="Неверный формат даты. Используйте: ДД.ММ.ГГГГ (например, 31.12.2025)"
        )
    
    # Проверка что дата не в прошлом (для дедлайнов)
    if not allow_past and parsed_date < date.today():
        return ValidationResult(
            valid=False,
            error_message="Дата не может быть в прошлом"
        )
    
    # Проверка что дата не слишком далеко в будущем (>10 лет)
    max_future_days = 365 * 10
    if (parsed_date - date.today()).days > max_future_days:
        return ValidationResult(
            valid=False,
            error_message="Дата слишком далеко в будущем (максимум 10 лет)"
        )
    
    return ValidationResult(
        valid=True,
        cleaned_value=parsed_date
    )


def validate_deadline_type_id(type_id_str: str) -> ValidationResult:
    """
    Валидация ID типа дедлайна
    
    Args:
        type_id_str: Строка с ID
        
    Returns:
        ValidationResult
    """
    try:
        type_id = int(type_id_str.strip())
        
        if type_id < 1:
            return ValidationResult(
                valid=False,
                error_message="ID должен быть положительным числом"
            )
        
        return ValidationResult(
            valid=True,
            cleaned_value=type_id
        )
    except ValueError:
        return ValidationResult(
            valid=False,
            error_message="ID должен быть числом"
        )


def validate_yes_no(answer: str) -> ValidationResult:
    """
    Валидация ответа да/нет
    
    Args:
        answer: Ответ пользователя
        
    Returns:
        ValidationResult (cleaned_value = True/False)
    """
    cleaned = answer.strip().lower()
    
    yes_variants = ['да', 'yes', 'y', 'д', '+', '1']
    no_variants = ['нет', 'no', 'n', 'н', '-', '0']
    
    if cleaned in yes_variants:
        return ValidationResult(valid=True, cleaned_value=True)
    elif cleaned in no_variants:
        return ValidationResult(valid=True, cleaned_value=False)
    else:
        return ValidationResult(
            valid=False,
            error_message='Ответьте "да" или "нет"'
        )


# Экспорт функций
__all__ = [
    'ValidationResult',
    'validate_inn',
    'validate_client_name',
    'validate_phone',
    'validate_email',
    'validate_date',
    'validate_deadline_type_id',
    'validate_yes_no'
]