"""
Custom Validators for KKT Services Expiration Management System

This module provides custom validation functions for business logic.

Validators:
- INN (Tax ID) format validation
- Russian phone number format validation
- Future date validation
- Email format validation
"""

import re
from datetime import date
from typing import Optional


def validate_inn(inn: str) -> tuple[bool, Optional[str]]:
    """
    Validate Russian INN (Tax Identification Number) format
    
    INN must be exactly 10 or 12 digits
    
    Args:
        inn: Tax identification number string
    
    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    
    Examples:
        >>> validate_inn("7701234567")
        (True, None)
        >>> validate_inn("123456789012")
        (True, None)
        >>> validate_inn("12345")
        (False, 'INN must be exactly 10 or 12 digits')
        >>> validate_inn("abc1234567")
        (False, 'INN must contain only digits')
    """
    if not inn:
        return False, "INN is required"
    
    # Remove whitespace
    inn = inn.strip()
    
    # Check if contains only digits
    if not inn.isdigit():
        return False, "INN must contain only digits"
    
    # Check length
    if len(inn) not in [10, 12]:
        return False, "INN must be exactly 10 or 12 digits"
    
    return True, None


def validate_phone(phone: str) -> tuple[bool, Optional[str]]:
    """
    Validate Russian phone number format
    
    Accepts formats:
    - +79001234567
    - 79001234567
    - +7 (900) 123-45-67
    - 8 900 123 45 67
    
    Args:
        phone: Phone number string
    
    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    
    Examples:
        >>> validate_phone("+79001234567")
        (True, None)
        >>> validate_phone("79001234567")
        (True, None)
        >>> validate_phone("+7 (900) 123-45-67")
        (True, None)
        >>> validate_phone("invalid")
        (False, 'Phone must be in Russian format: +7XXXXXXXXXX')
    """
    if not phone:
        return True, None  # Phone is optional
    
    # Remove formatting characters
    cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Replace leading 8 with 7
    if cleaned.startswith('8') and len(cleaned) == 11:
        cleaned = '7' + cleaned[1:]
    
    # Add + if missing
    if cleaned.startswith('7') and not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    
    # Check Russian phone format: +7 followed by 10 digits
    if not re.match(r'^\+7\d{10}$', cleaned):
        return False, "Phone must be in Russian format: +7XXXXXXXXXX"
    
    return True, None


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number to standard format
    
    Args:
        phone: Phone number in any accepted format
    
    Returns:
        str: Normalized phone number in format +7XXXXXXXXXX
    
    Examples:
        >>> normalize_phone("+7 (900) 123-45-67")
        '+79001234567'
        >>> normalize_phone("8 900 123 45 67")
        '+79001234567'
    """
    if not phone:
        return phone
    
    # Remove formatting
    cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Replace leading 8 with 7
    if cleaned.startswith('8') and len(cleaned) == 11:
        cleaned = '7' + cleaned[1:]
    
    # Add + if missing
    if cleaned.startswith('7') and not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    
    return cleaned


def validate_future_date(target_date: date, allow_today: bool = True) -> tuple[bool, Optional[str]]:
    """
    Validate that a date is in the future
    
    Args:
        target_date: Date to validate
        allow_today: Whether to allow today's date (default: True)
    
    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    
    Examples:
        >>> from datetime import date, timedelta
        >>> future = date.today() + timedelta(days=1)
        >>> validate_future_date(future)
        (True, None)
        >>> past = date.today() - timedelta(days=1)
        >>> validate_future_date(past)
        (False, 'Date must be in the future')
    """
    if not target_date:
        return False, "Date is required"
    
    today = date.today()
    
    if target_date < today:
        return False, "Date must be in the future"
    
    if target_date == today and not allow_today:
        return False, "Date must be after today"
    
    return True, None


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate email format
    
    Args:
        email: Email address string
    
    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    
    Examples:
        >>> validate_email("user@example.com")
        (True, None)
        >>> validate_email("admin@kkt.local")
        (True, None)
        >>> validate_email("invalid.email")
        (False, 'Invalid email format')
    """
    if not email:
        return True, None  # Email is optional in some cases
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None


def validate_status(status: str) -> tuple[bool, Optional[str]]:
    """
    Validate deadline status value
    
    Args:
        status: Status string
    
    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    
    Examples:
        >>> validate_status("active")
        (True, None)
        >>> validate_status("expired")
        (True, None)
        >>> validate_status("invalid")
        (False, "Status must be one of: active, expired, renewed")
    """
    allowed_statuses = ['active', 'expired', 'renewed']
    
    if status not in allowed_statuses:
        return False, f"Status must be one of: {', '.join(allowed_statuses)}"
    
    return True, None


def validate_role(role: str) -> tuple[bool, Optional[str]]:
    """
    Validate user role value
    
    Args:
        role: Role string
    
    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    
    Examples:
        >>> validate_role("admin")
        (True, None)
        >>> validate_role("manager")
        (True, None)
        >>> validate_role("superuser")
        (False, "Role must be one of: admin, manager")
    """
    allowed_roles = ['admin', 'manager']
    
    if role not in allowed_roles:
        return False, f"Role must be one of: {', '.join(allowed_roles)}"
    
    return True, None


def validate_telegram_id(telegram_id: str) -> tuple[bool, Optional[str]]:
    """
    Validate Telegram user ID format
    
    Telegram IDs are numeric strings
    
    Args:
        telegram_id: Telegram user ID string
    
    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    
    Examples:
        >>> validate_telegram_id("123456789")
        (True, None)
        >>> validate_telegram_id("abc123")
        (False, 'Telegram ID must be numeric')
    """
    if not telegram_id:
        return False, "Telegram ID is required"
    
    if not telegram_id.isdigit():
        return False, "Telegram ID must be numeric"
    
    if len(telegram_id) > 20:  # Reasonable upper limit
        return False, "Telegram ID too long"
    
    return True, None


def validate_password_strength(password: str, min_length: int = 8) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Requirements:
    - Minimum length (default 8 characters)
    - At least one letter
    - At least one digit
    
    Args:
        password: Password string
        min_length: Minimum password length (default: 8)
    
    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    
    Examples:
        >>> validate_password_strength("Password123")
        (True, None)
        >>> validate_password_strength("short")
        (False, 'Password must be at least 8 characters long')
        >>> validate_password_strength("12345678")
        (False, 'Password must contain at least one letter')
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    return True, None


# ============================================
# Testing
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ВАЛИДАТОРОВ")
    print("=" * 60)
    
    # Test INN validation
    print("\n1. Тестирование валидации ИНН:")
    test_inns = [
        ("7701234567", True),
        ("123456789012", True),
        ("12345", False),
        ("abc1234567", False),
        ("", False)
    ]
    for inn, expected in test_inns:
        is_valid, error = validate_inn(inn)
        status = "✓" if is_valid == expected else "✗"
        print(f"   {status} ИНН '{inn}': {is_valid} {'- ' + error if error else ''}")
    
    # Test phone validation
    print("\n2. Тестирование валидации телефона:")
    test_phones = [
        ("+79001234567", True),
        ("79001234567", True),
        ("+7 (900) 123-45-67", True),
        ("8 900 123 45 67", True),
        ("invalid", False)
    ]
    for phone, expected in test_phones:
        is_valid, error = validate_phone(phone)
        status = "✓" if is_valid == expected else "✗"
        normalized = normalize_phone(phone) if is_valid else ""
        print(f"   {status} Телефон '{phone}': {is_valid} {f'→ {normalized}' if normalized else ''}")
    
    # Test email validation
    print("\n3. Тестирование валидации email:")
    test_emails = [
        ("user@example.com", True),
        ("admin@kkt.local", True),
        ("invalid.email", False),
        ("", True)  # Empty is allowed (optional field)
    ]
    for email, expected in test_emails:
        is_valid, error = validate_email(email)
        status = "✓" if is_valid == expected else "✗"
        print(f"   {status} Email '{email}': {is_valid}")
    
    # Test status validation
    print("\n4. Тестирование валидации статуса:")
    test_statuses = [
        ("active", True),
        ("expired", True),
        ("renewed", True),
        ("invalid", False)
    ]
    for status, expected in test_statuses:
        is_valid, error = validate_status(status)
        check = "✓" if is_valid == expected else "✗"
        print(f"   {check} Статус '{status}': {is_valid}")
    
    # Test password strength
    print("\n5. Тестирование надёжности пароля:")
    test_passwords = [
        ("Password123", True),
        ("short", False),
        ("12345678", False),
        ("OnlyLetters", False)
    ]
    for password, expected in test_passwords:
        is_valid, error = validate_password_strength(password)
        status = "✓" if is_valid == expected else "✗"
        print(f"   {status} Пароль '{password}': {is_valid} {'- ' + error if error else ''}")
    
    print("\n" + "=" * 60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)
