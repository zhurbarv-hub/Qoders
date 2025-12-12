# -*- coding: utf-8 -*-
"""
Обработчик диалогов для CRUD операций
Объединённый обработчик для управления клиентами и дедлайнами
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from datetime import datetime

from bot.services.validators import (
    validate_inn, validate_client_name, validate_phone, 
    validate_email, validate_yes_no, validate_date, 
    validate_deadline_type_id
)
from bot.services.conversation import (
    get_conversation, end_conversation
)
from bot.services import checker

logger = logging.getLogger(__name__)
router = Router(name='crud_conversations')

@router.message(F.text & ~F.text.startswith('/'))
async def handle_crud_conversation_step(
    message: Message,
    user_role: str = 'unknown',
    **kwargs
):
    """Обработка шагов активного CRUD диалога"""
    user = message.from_user
    conv = get_conversation(user.id)
    
    if not conv:
        return  # Нет активного диалога - пропускаем
    
    logger.info(f"🔄 Обработка диалога: {conv.command}, шаг {conv.step}")
    
    # Маршрутизация по типу диалога
    if conv.command in ['add_client', 'edit_client', 'delete_client']:
        await handle_client_conversation(message, conv, user_role)
    elif conv.command in ['add_deadline', 'edit_deadline', 'delete_deadline']:
        await handle_deadline_conversation(message, conv, user_role)
    else:
        logger.warning(f"Неизвестный тип диалога: {conv.command}")
        return
        
        

async def handle_client_conversation(message: Message, conv, user_role: str):
    """Обработка диалогов управления клиентами"""
    user = message.from_user
    text = message.text.strip()
    api_client = checker._api_client
    
    # === ДИАЛОГ: Добавление клиента ===
    if conv.command == 'add_client':
        if conv.step == 1:
            # Шаг 1: Название
            validation = validate_client_name(text)
            if not validation.valid:
                await message.answer(f"❌ {validation.error_message}\nПопробуйте снова:", parse_mode='HTML')
                return
            
            conv.set_data('name', validation.cleaned_value)
            conv.next_step()
            await message.answer(
                f"✅ Название: {validation.cleaned_value}\n\n"
                f"<b>Шаг 2/7:</b> Введите ИНН (10 или 12 цифр):",
                parse_mode='HTML'
            )
        
        elif conv.step == 2:
            # Шаг 2: ИНН
            validation = validate_inn(text)
            if not validation.valid:
                await message.answer(f"❌ {validation.error_message}\nПопробуйте снова:", parse_mode='HTML')
                return
            
            # Проверка уникальности через API
            try:
                response = await api_client.get("/api/clients", params={"search": validation.cleaned_value})
                if response.get('clients'):
                    await message.answer(
                        f"❌ Клиент с ИНН {validation.cleaned_value} уже существует!\n"
                        f"Используйте /editclient для редактирования.",
                        parse_mode='HTML'
                    )
                    end_conversation(user.id)
                    return
            except:
                pass
            
            conv.set_data('inn', validation.cleaned_value)
            conv.next_step()
            await message.answer(
                f"✅ ИНН: {validation.cleaned_value}\n\n"
                f"<b>Шаг 3/7:</b> Введите ФИО контактного лица (или /skip):",
                parse_mode='HTML'
            )
        
        elif conv.step == 3:
            # Шаг 3: Контактное лицо (опционально)
            if text.lower() == '/skip':
                conv.set_data('contact_person', None)
            else:
                contact_person = text.strip()
                if len(contact_person) < 1 or len(contact_person) > 255:
                    await message.answer("❌ ФИО должно быть от 1 до 255 символов\nПопробуйте снова или /skip:", parse_mode='HTML')
                    return
                conv.set_data('contact_person', contact_person)
            
            conv.next_step()
            await message.answer(
                f"✅ Контактное лицо: {conv.get_data('contact_person') or 'не указано'}\n\n"
                f"<b>Шаг 4/7:</b> Введите телефон (или /skip):",
                parse_mode='HTML'
            )
        
        elif conv.step == 4:
            # Шаг 4: Телефон (опционально)
            if text.lower() == '/skip':
                conv.set_data('phone', None)
            else:
                validation = validate_phone(text)
                if not validation.valid:
                    await message.answer(f"❌ {validation.error_message}\nПопробуйте снова или /skip:", parse_mode='HTML')
                    return
                conv.set_data('phone', validation.cleaned_value)
            
            conv.next_step()
            await message.answer(
                f"✅ Телефон: {conv.get_data('phone') or 'не указан'}\n\n"
                f"<b>Шаг 5/7:</b> Введите email (или /skip):",
                parse_mode='HTML'
            )
        
        elif conv.step == 5:
            # Шаг 5: Email (опционально)
            if text.lower() == '/skip':
                conv.set_data('email', None)
            else:
                validation = validate_email(text)
                if not validation.valid:
                    await message.answer(f"❌ {validation.error_message}\nПопробуйте снова или /skip:", parse_mode='HTML')
                    return
                conv.set_data('email', validation.cleaned_value)
            
            conv.next_step()
            await message.answer(
                f"✅ Email: {conv.get_data('email') or 'не указан'}\n\n"
                f"<b>Шаг 6/7:</b> Введите адрес (или /skip):",
                parse_mode='HTML'
            )
        
        elif conv.step == 6:
            # Шаг 6: Адрес (опционально)
            if text.lower() == '/skip':
                conv.set_data('address', None)
            else:
                address = text.strip()
                if len(address) > 500:
                    await message.answer("❌ Адрес слишком длинный (максимум 500 символов)\nПопробуйте снова или /skip:", parse_mode='HTML')
                    return
                conv.set_data('address', address)
            
            conv.next_step()
            await message.answer(
                f"✅ Адрес: {conv.get_data('address') or 'не указан'}\n\n"
                f"<b>Шаг 7/7:</b> Введите примечание (или /skip):",
                parse_mode='HTML'
            )
        
        elif conv.step == 7:
            # Шаг 7: Примечание (опционально)
            if text.lower() == '/skip':
                conv.set_data('notes', None)
            else:
                notes = text.strip()
                if len(notes) > 1000:
                    await message.answer("❌ Примечание слишком длинное (максимум 1000 символов)\nПопробуйте снова или /skip:", parse_mode='HTML')
                    return
                conv.set_data('notes', notes)
            
            conv.next_step()
            
            # Показываем сводку
            await message.answer(
                f"📋 <b>Проверьте данные:</b>\n\n"
                f"🏢 Название: {conv.get_data('name')}\n"
                f"🆔 ИНН: {conv.get_data('inn')}\n"
                f"👤 Контактное лицо: {conv.get_data('contact_person') or 'не указано'}\n"
                f"📞 Телефон: {conv.get_data('phone') or 'не указан'}\n"
                f"📧 Email: {conv.get_data('email') or 'не указан'}\n"
                f"📍 Адрес: {conv.get_data('address') or 'не указан'}\n"
                f"📝 Примечание: {conv.get_data('notes') or 'нет'}\n\n"
                f"Всё верно? Отправьте \"да\" для создания или /cancel для отмены",
                parse_mode='HTML'
            )
        
        elif conv.step == 8:
            # Шаг 8: Подтверждение
            validation = validate_yes_no(text)
            if not validation.valid:
                await message.answer(validation.error_message, parse_mode='HTML')
                return
            
            if not validation.cleaned_value:
                await message.answer("❌ Создание отменено", parse_mode='HTML')
                end_conversation(user.id)
                return
            
            # Создание через API
            try:
                client_data = {
                    "name": conv.get_data('name'),
                    "inn": conv.get_data('inn'),
                    "contact_person": conv.get_data('contact_person'),
                    "phone": conv.get_data('phone'),
                    "email": conv.get_data('email'),
                    "address": conv.get_data('address'),
                    "notes": conv.get_data('notes'),
                    "is_active": True
                }
                
                new_client = await api_client.post("/api/clients", data=client_data)
                
                await message.answer(
                    f"✅ <b>Клиент успешно создан!</b>\n\n"
                    f"🆔 ID: {new_client['id']}\n"
                    f"🏢 Название: {new_client['name']}\n"
                    f"📄 ИНН: {new_client['inn']}",
                    parse_mode='HTML'
                )
                
                end_conversation(user.id)
                logger.info(f"Клиент создан: ID={new_client['id']}, ИНН={new_client['inn']}")
                
            except Exception as e:
                logger.error(f"Ошибка создания клиента: {e}")
                await message.answer(
                    f"❌ Ошибка создания клиента: {str(e)}\n"
                    f"Попробуйте снова позже.",
                    parse_mode='HTML'
                )
                end_conversation(user.id)    
                end_conversation(user.id)    
    # === ДИАЛОГ: Редактирование клиента ===
    elif conv.command == 'edit_client':
        client_id = conv.get_data('client_id')
        
        if conv.step == 1:
            # Выбор поля для редактирования
            if text in ['1', '2', '3', '4']:
                field_map = {'1': 'name', '2': 'email', '3': 'phone', '4': 'is_active'}
                field = field_map[text]
                conv.set_data('edit_field', field)
                conv.next_step()
                
                prompts = {
                    'name': 'Введите новое название:',
                    'email': 'Введите новый email:',
                    'phone': 'Введите новый телефон:',
                    'is_active': 'Активировать клиента? (да/нет):'
                }
                
                await message.answer(prompts[field], parse_mode='HTML')
            else:
                await message.answer("❌ Выберите 1, 2, 3 или 4", parse_mode='HTML')
        
        elif conv.step == 2:
            # Ввод нового значения
            field = conv.get_data('edit_field')
            
            validators = {
                'name': validate_client_name,
                'email': validate_email,
                'phone': validate_phone,
                'is_active': validate_yes_no
            }
            
            validation = validators[field](text)
            if not validation.valid:
                await message.answer(f"❌ {validation.error_message}\nПопробуйте снова:", parse_mode='HTML')
                return
            
            conv.set_data('new_value', validation.cleaned_value)
            conv.next_step()
            
            await message.answer(
                f"Подтвердить изменение? (да/нет)",
                parse_mode='HTML'
            )
        
        elif conv.step == 3:
            # Подтверждение
            validation = validate_yes_no(text)
            if not validation.valid or not validation.cleaned_value:
                await message.answer("❌ Изменение отменено", parse_mode='HTML')
                end_conversation(user.id)
                return
            
            # Обновление через API
            try:
                field = conv.get_data('edit_field')
                new_value = conv.get_data('new_value')
                
                update_data = {field: new_value}
                updated_client = await api_client.put(f"/api/clients/{client_id}", data=update_data)
                
                await message.answer(
                    f"✅ <b>Клиент обновлён!</b>\n\n"
                    f"Поле: {field}\n"
                    f"Новое значение: {new_value}",
                    parse_mode='HTML'
                )
                
                end_conversation(user.id)
                
            except Exception as e:
                logger.error(f"Ошибка обновления клиента: {e}")
                await message.answer(f"❌ Ошибка: {str(e)}", parse_mode='HTML')
                end_conversation(user.id)
    
    # === ДИАЛОГ: Удаление клиента ===
    elif conv.command == 'delete_client':
        client_id = conv.get_data('client_id')
        inn = conv.get_data('inn')
        expected = f"УДАЛИТЬ {inn}"
        
        if text == expected:
            try:
                # Удаление (деактивация) через API
                await api_client.delete(f"/api/clients/{client_id}")
                
                await message.answer(
                    f"✅ <b>Клиент деактивирован</b>\n\n"
                    f"Дедлайны остались в системе.\n"
                    f"Используйте /editclient для активации.",
                    parse_mode='HTML'
                )
                
                end_conversation(user.id)
                logger.info(f"Клиент удалён: ID={client_id}")
                
            except Exception as e:
                logger.error(f"Ошибка удаления клиента: {e}")
                await message.answer(f"❌ Ошибка: {str(e)}", parse_mode='HTML')
                end_conversation(user.id)
        else:
            await message.answer(
                f"❌ Неверная фраза подтверждения\n"
                f"Ожидалось: <code>{expected}</code>",
                parse_mode='HTML'
            )
            
            

async def handle_deadline_conversation(message: Message, conv, user_role: str):
    """Обработка диалогов управления дедлайнами"""
    user = message.from_user
    text = message.text.strip()
    api_client = checker._api_client
    
    # === ДИАЛОГ: Добавление дедлайна ===
    if conv.command == 'add_deadline':
        if conv.step == 1:
            # Шаг 1: Поиск клиента по ИНН
            validation = validate_inn(text)
            if not validation.valid:
                await message.answer(f"❌ {validation.error_message}\nПопробуйте снова:", parse_mode='HTML')
                return
            
            # Поиск клиента через API
            try:
                response = await api_client.get("/api/clients", params={"search": validation.cleaned_value})
                logger.info(f"🔍 API response type: {type(response)}, content: {response}")
                clients = response if isinstance(response, list) else response.get('clients', []) if isinstance(response, dict) else []
                logger.info(f"🔍 Найдено клиентов: {len(clients)}")
                
                if not clients:
                    await message.answer(
                        f"❌ Клиент с ИНН {validation.cleaned_value} не найден\n"
                        f"Используйте /addclient для добавления нового клиента",
                        parse_mode='HTML'
                    )
                    end_conversation(user.id)
                    return
                
                client = clients[0]
                
                # Проверка что клиент активен
                if not client.get('is_active'):
                    await message.answer(
                        f"❌ Клиент {client['name']} деактивирован\n"
                        f"Активируйте клиента через /editclient",
                        parse_mode='HTML'
                    )
                    end_conversation(user.id)
                    return
                
                conv.set_data('client_id', client['id'])
                conv.set_data('client', client)
                conv.next_step()
                
                # Получаем список типов дедлайнов
                # Получаем список типов дедлайнов
                types_response = await api_client.get("/api/deadline-types")
                logger.info(f"🔍 Deadline types response type: {type(types_response)}, content: {types_response}")
                types = types_response if isinstance(types_response, list) else types_response.get('deadline_types', []) if isinstance(types_response, dict) else []
                logger.info(f"🔍 Найдено типов дедлайнов: {len(types)}")
                
                if not types:
                    await message.answer("❌ Нет доступных типов дедлайнов", parse_mode='HTML')
                    end_conversation(user.id)
                    return
                
                conv.set_data('types', types)
                
                # Показываем список типов
                types_list = "\n".join([f"{t['id']}. {t['type_name']}" for t in types])
                
                await message.answer(
                    f"✅ Клиент: {client['name']}\n\n"
                    f"<b>Шаг 2/4:</b> Выберите тип дедлайна (введите номер):\n\n"
                    f"{types_list}",
                    parse_mode='HTML'
                )
                
            except Exception as e:
                logger.error(f"Ошибка поиска клиента: {e}")
                await message.answer(f"❌ Ошибка: {str(e)}", parse_mode='HTML')
                end_conversation(user.id)
        
        elif conv.step == 2:
            # Шаг 2: Выбор типа дедлайна
            validation = validate_deadline_type_id(text)
            if not validation.valid:
                await message.answer(f"❌ {validation.error_message}\nПопробуйте снова:", parse_mode='HTML')
                return
            
            type_id = validation.cleaned_value
            types = conv.get_data('types', [])
            
            # Проверка что такой тип существует
            selected_type = next((t for t in types if t['id'] == type_id), None)
            
            if not selected_type:
                await message.answer(f"❌ Тип с ID {type_id} не найден\nВыберите из списка:", parse_mode='HTML')
                return
            
            conv.set_data('deadline_type_id', type_id)
            conv.set_data('deadline_type', selected_type)
            conv.next_step()
            
            await message.answer(
                f"✅ Тип: {selected_type['type_name']}\n\n"
                f"<b>Шаг 3/4:</b> Введите дату дедлайна (ДД.ММ.ГГГГ):\n"
                f"Пример: 31.12.2025",
                parse_mode='HTML'
            )
        
        elif conv.step == 3:
            # Шаг 3: Дата дедлайна
            validation = validate_date(text, allow_past=False)
            if not validation.valid:
                await message.answer(f"❌ {validation.error_message}\nПопробуйте снова:", parse_mode='HTML')
                return
            
            conv.set_data('deadline_date', validation.cleaned_value)
            conv.next_step()
            
            await message.answer(
                f"✅ Дата: {validation.cleaned_value.strftime('%d.%m.%Y')}\n\n"
                f"<b>Шаг 4/4:</b> Введите примечание (или /skip):",
                parse_mode='HTML'
            )
        
        elif conv.step == 4:
            # Шаг 4: Примечание (опционально)
            if text.lower() == '/skip':
                notes = None
            else:
                notes = text.strip()
                if len(notes) > 500:
                    await message.answer("❌ Примечание слишком длинное (максимум 500 символов)", parse_mode='HTML')
                    return
            
            conv.set_data('notes', notes)
            conv.next_step()
            
            # Показываем сводку
            client = conv.get_data('client')
            deadline_type = conv.get_data('deadline_type')
            deadline_date = conv.get_data('deadline_date')
            
            await message.answer(
                f"📋 <b>Проверьте данные:</b>\n\n"
                f"🏢 Клиент: {client['name']}\n"
                f"📋 Тип: {deadline_type['type_name']}\n"
                f"📅 Дата: {deadline_date.strftime('%d.%m.%Y')}\n"
                f"📝 Примечание: {notes or 'нет'}\n\n"
                f"Всё верно? Отправьте \"да\" для создания или /cancel для отмены",
                parse_mode='HTML'
            )
        
        elif conv.step == 5:
            # Шаг 5: Подтверждение
            validation = validate_yes_no(text)
            if not validation.valid:
                await message.answer(validation.error_message, parse_mode='HTML')
                return
            
            if not validation.cleaned_value:
                await message.answer("❌ Создание отменено", parse_mode='HTML')
                end_conversation(user.id)
                return
            
            # Создание через API
            try:
                deadline_data = {
                    "client_id": conv.get_data('client_id'),
                    "deadline_type_id": conv.get_data('deadline_type_id'),
                    "expiration_date": conv.get_data('deadline_date').isoformat(),
                    "notes": conv.get_data('notes'),
                    "status": "active"
                }
                
                new_deadline = await api_client.post("/api/deadlines", data=deadline_data)
                
                client = conv.get_data('client')
                deadline_type = conv.get_data('deadline_type')
                
                await message.answer(
                    f"✅ <b>Дедлайн успешно создан!</b>\n\n"
                    f"🆔 ID: {new_deadline['id']}\n"
                    f"🏢 Клиент: {client['name']}\n"
                    f"📋 Тип: {deadline_type['type_name']}\n"
                    f"📅 Дата: {conv.get_data('deadline_date').strftime('%d.%m.%Y')}",
                    parse_mode='HTML'
                )
                
                end_conversation(user.id)
                logger.info(f"Дедлайн создан: ID={new_deadline['id']}")
                
            except Exception as e:
                logger.error(f"Ошибка создания дедлайна: {e}")
                await message.answer(
                    f"❌ Ошибка создания дедлайна: {str(e)}\n"
                    f"Попробуйте снова позже.",
                    parse_mode='HTML'
                )
                end_conversation(user.id)
    
    # === ДИАЛОГ: Редактирование дедлайна ===
    elif conv.command == 'edit_deadline':
        deadline_id = conv.get_data('deadline_id')
        
        if conv.step == 1:
            # Выбор поля для редактирования
            if text in ['1', '2', '3']:
                field_map = {'1': 'deadline_date', '2': 'notes', '3': 'status'}
                field = field_map[text]
                conv.set_data('edit_field', field)
                conv.next_step()
                
                prompts = {
                    'deadline_date': 'Введите новую дату (ДД.ММ.ГГГГ):',
                    'notes': 'Введите новое примечание:',
                    'status': 'Пометить как выполненный? (да/нет):'
                }
                
                await message.answer(prompts[field], parse_mode='HTML')
            else:
                await message.answer("❌ Выберите 1, 2 или 3", parse_mode='HTML')
        
        elif conv.step == 2:
            # Ввод нового значения
            field = conv.get_data('edit_field')
            
            if field == 'deadline_date':
                validation = validate_date(text, allow_past=False)
                if not validation.valid:
                    await message.answer(f"❌ {validation.error_message}\nПопробуйте снова:", parse_mode='HTML')
                    return
                new_value = validation.cleaned_value.isoformat()
                
            elif field == 'notes':
                notes = text.strip()
                if len(notes) > 500:
                    await message.answer("❌ Примечание слишком длинное (максимум 500 символов)", parse_mode='HTML')
                    return
                new_value = notes
                
            elif field == 'status':
                validation = validate_yes_no(text)
                if not validation.valid:
                    await message.answer(f"❌ {validation.error_message}", parse_mode='HTML')
                    return
                new_value = 'completed' if validation.cleaned_value else 'active'
            
            conv.set_data('new_value', new_value)
            conv.next_step()
            
            await message.answer(
                f"Подтвердить изменение? (да/нет)",
                parse_mode='HTML'
            )
        
        elif conv.step == 3:
            # Подтверждение
            validation = validate_yes_no(text)
            if not validation.valid or not validation.cleaned_value:
                await message.answer("❌ Изменение отменено", parse_mode='HTML')
                end_conversation(user.id)
                return
            
            # Обновление через API
            try:
                field = conv.get_data('edit_field')
                new_value = conv.get_data('new_value')
                
                update_data = {field: new_value}
                updated_deadline = await api_client.put(f"/api/deadlines/{deadline_id}", data=update_data)
                
                await message.answer(
                    f"✅ <b>Дедлайн обновлён!</b>\n\n"
                    f"Поле: {field}\n"
                    f"Новое значение: {new_value}",
                    parse_mode='HTML'
                )
                
                end_conversation(user.id)
                
            except Exception as e:
                logger.error(f"Ошибка обновления дедлайна: {e}")
                await message.answer(f"❌ Ошибка: {str(e)}", parse_mode='HTML')
                end_conversation(user.id)
    
    # === ДИАЛОГ: Удаление дедлайна ===
    elif conv.command == 'delete_deadline':
        deadline_id = conv.get_data('deadline_id')
        expected = f"УДАЛИТЬ {deadline_id}"
        
        if text == expected:
            try:
                # Удаление через API
                await api_client.delete(f"/api/deadlines/{deadline_id}")
                
                await message.answer(
                    f"✅ <b>Дедлайн удалён</b>\n\n"
                    f"ID: {deadline_id}",
                    parse_mode='HTML'
                )
                
                end_conversation(user.id)
                logger.info(f"Дедлайн удалён: ID={deadline_id}")
                
            except Exception as e:
                logger.error(f"Ошибка удаления дедлайна: {e}")
                await message.answer(f"❌ Ошибка: {str(e)}", parse_mode='HTML')
                end_conversation(user.id)
        else:
            await message.answer(
                f"❌ Неверная фраза подтверждения\n"
                f"Ожидалось: <code>{expected}</code>",
                parse_mode='HTML'
            )


# Экспорт
__all__ = ['router']