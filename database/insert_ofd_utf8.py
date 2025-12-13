# -*- coding: utf-8 -*-
import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('kkt_services.db')
cursor = conn.cursor()

# Удаление существующих записей
cursor.execute("DELETE FROM ofd_providers;")

# Данные ОФД провайдеров
providers = [
    ('ООО "Эвотор ОФД"', '9715260691', 'https://ofd.evotor.ru', '+7 (800) 234-53-53', 1),
    ('ООО "ПЕТЕР-СЕРВИС Спецтехнологии"', '7841063956', 'https://pecom-ofd.ru', '+7 (812) 703-35-99', 1),
    ('ООО "Калуга Астрал"', '7724261610', 'https://kaluga-astral.ru', '+7 (800) 700-15-00', 1),
    ('АО "Компания "Тензор"', '7606045932', 'https://ofd.sbis.ru', '+7 (800) 333-14-48', 1),
    ('ООО "Яндекс.ОФД"', '7704358518', 'https://ofd.yandex.ru', '+7 (495) 739-70-00', 1),
    ('АО "СБИС"', '5406255300', 'https://sbis.ru/ofd', '+7 (800) 333-14-48', 1),
    ('ООО "Первый ОФД"', '7704211201', 'https://1-ofd.ru', '+7 (800) 700-11-99', 1),
    ('ООО "Такс.ру"', '7811541072', 'https://taxcom.ru', '+7 (800) 250-05-29', 1),
    ('ООО "Корус Консалтинг СНГ"', '7710747640', 'https://ofd.platformaofd.ru', '+7 (495) 231-23-22', 1),
    ('ООО "ОФД.ру"', '7701547893', 'https://ofd.ru', '+7 (499) 110-23-44', 1)
]

# Вставка данных
cursor.executemany(
    "INSERT INTO ofd_providers (provider_name, inn, website, support_phone, is_active) VALUES (?, ?, ?, ?, ?)",
    providers
)

# Сохранение изменений
conn.commit()

# Проверка
cursor.execute("SELECT id, provider_name FROM ofd_providers ORDER BY id")
results = cursor.fetchall()

print(f"Вставлено {len(results)} записей:")
for row in results:
    print(f"ID: {row[0]}, Название: {row[1]}")

conn.close()
print("\nГотово!")
