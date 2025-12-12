# -*- coding: utf-8 -*-
"""
Email сервис для отправки приглашений и уведомлений
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

from ..config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email через SMTP"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_from_name = settings.smtp_from_name
        self.smtp_from_email = settings.smtp_from_email
        self.smtp_use_tls = settings.smtp_use_tls
        self.web_base_url = settings.web_base_url
    
    def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """
        Отправка email через SMTP
        
        Args:
            to_email: Email получателя
            subject: Тема письма
            html_body: HTML содержимое письма
            
        Returns:
            bool: True если отправка успешна, False в случае ошибки
        """
        try:
            # Создание сообщения
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
            msg['To'] = to_email
            
            # HTML часть
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Подключение к SMTP серверу
            if self.smtp_use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            
            # Аутентификация
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            
            # Отправка
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Email успешно отправлен на {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки email на {to_email}: {str(e)}")
            return False
    
    def send_invitation_email(
        self,
        to_email: str,
        full_name: str,
        company_name: str,
        activation_token: str,
        registration_code: Optional[str] = None,
        code_expires_at: Optional[datetime] = None
    ) -> bool:
        """
        Отправка приглашения новому клиенту
        
        Args:
            to_email: Email клиента
            full_name: ФИО клиента
            company_name: Название компании
            activation_token: Токен для активации аккаунта
            registration_code: Код регистрации в Telegram боте
            code_expires_at: Срок действия кода регистрации
            
        Returns:
            bool: True если отправка успешна
        """
        activation_link = f"{self.web_base_url}/static/activate.html?token={activation_token}"
        
        # Формирование HTML письма
        html_body = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .button {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .info-box {{
            background: white;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
        }}
        .telegram-section {{
            background: #E3F2FD;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 0;
        }}
        .code {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            letter-spacing: 2px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Добро пожаловать в KKT System!</h1>
    </div>
    
    <div class="content">
        <p>Здравствуйте, <strong>{full_name}</strong>!</p>
        
        <p>Вы были зарегистрированы в системе управления сроками истечения услуг ККТ.</p>
        
        <div class="info-box">
            <p><strong>📋 Компания:</strong> {company_name}</p>
            <p><strong>📧 Ваш Email:</strong> {to_email}</p>
        </div>
        
        <h3>🔐 Активация аккаунта</h3>
        <p>Для завершения регистрации и установки пароля перейдите по ссылке:</p>
        
        <p style="text-align: center;">
            <a href="{activation_link}" class="button">Установить пароль</a>
        </p>
        
        <p style="font-size: 12px; color: #666;">
            Или скопируйте ссылку в браузер:<br>
            <code style="background: #eee; padding: 5px; display: block; margin-top: 5px;">{activation_link}</code>
        </p>
        
        <p><strong>⏰ Ссылка действительна в течение 48 часов.</strong></p>
"""
        
        # Добавление информации о Telegram боте, если есть код регистрации
        if registration_code and code_expires_at:
            expires_str = code_expires_at.strftime('%d.%m.%Y %H:%M')
            html_body += f"""
        <div class="telegram-section">
            <h3>📱 Telegram бот для уведомлений</h3>
            <p>Также вы можете зарегистрироваться в Telegram боте для получения уведомлений о дедлайнах:</p>
            
            <p><strong>Код регистрации:</strong></p>
            <p class="code">{registration_code}</p>
            
            <p style="font-size: 12px; color: #666;">
                Срок действия кода: до {expires_str}
            </p>
            
            <p>
                <strong>Как зарегистрироваться:</strong><br>
                1. Найдите бот @your_kkt_bot в Telegram<br>
                2. Отправьте команду: <code>/register {registration_code}</code>
            </p>
        </div>
"""
        
        html_body += """
        <p>После активации аккаунта вы получите доступ к веб-интерфейсу для управления своими дедлайнами.</p>
        
        <div class="footer">
            <p>С уважением,<br>Команда KKT System</p>
            <p style="font-size: 10px; color: #999;">
                Это автоматическое письмо. Пожалуйста, не отвечайте на него.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        subject = "Приглашение в систему управления дедлайнами KKT"
        return self._send_email(to_email, subject, html_body)
    
    def send_password_reset_email(
        self,
        to_email: str,
        full_name: str,
        reset_token: str
    ) -> bool:
        """
        Отправка письма для сброса пароля
        
        Args:
            to_email: Email пользователя
            full_name: ФИО пользователя
            reset_token: Токен для сброса пароля
            
        Returns:
            bool: True если отправка успешна
        """
        reset_link = f"{self.web_base_url}/static/activate.html?token={reset_token}"
        
        html_body = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .button {{
            display: inline-block;
            background: #f5576c;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Сброс пароля</h1>
    </div>
    
    <div class="content">
        <p>Здравствуйте, <strong>{full_name}</strong>!</p>
        
        <p>Вы запросили сброс пароля для вашего аккаунта в KKT System.</p>
        
        <p>Для установки нового пароля перейдите по ссылке:</p>
        
        <p style="text-align: center;">
            <a href="{reset_link}" class="button">Установить новый пароль</a>
        </p>
        
        <p style="font-size: 12px; color: #666;">
            Или скопируйте ссылку в браузер:<br>
            <code style="background: #eee; padding: 5px; display: block; margin-top: 5px;">{reset_link}</code>
        </p>
        
        <div class="warning">
            <p><strong>⏰ Ссылка действительна в течение 48 часов.</strong></p>
            <p style="font-size: 14px;">
                Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.
            </p>
        </div>
        
        <div class="footer">
            <p>С уважением,<br>Команда KKT System</p>
            <p style="font-size: 10px; color: #999;">
                Это автоматическое письмо. Пожалуйста, не отвечайте на него.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        subject = "Сброс пароля - KKT System"
        return self._send_email(to_email, subject, html_body)


# Глобальный экземпляр сервиса
email_service = EmailService()
