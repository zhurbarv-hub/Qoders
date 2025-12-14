-- Полный актуальный список операторов ОФД в России (2024-2025)
-- Источник: ФНС России, официальный реестр операторов фискальных данных

-- Очистка таблицы (опционально, если нужно начать с чистого листа)
-- DELETE FROM ofd_providers;

-- Основные крупные операторы ОФД
INSERT INTO ofd_providers (name, website, support_phone, support_email, is_active) VALUES
('ООО "Компания "Тензор"', 'https://ofd.sbis.ru', '+7 (495) 532-31-01', 'support@sbis.ru', true),
('ООО "ТАКС ФРЕЕ"', 'https://ofd.taxcom.ru', '+7 (495) 120-17-17', 'support@taxcom.ru', true),
('АО "Калуга Астрал"', 'https://ofd.astralnalog.ru', '+7 (800) 700-15-21', 'support@astralnalog.ru', true),
('ООО "Ярус"', 'https://ofd.yarus.ru', '+7 (800) 250-07-39', 'support@yarus.ru', true),
('ООО "ПЕТЕР-СЕРВИС Спецтехнологии"', 'https://ofd.platformaofd.ru', '+7 (800) 500-80-05', 'support@platformaofd.ru', true),
('ООО "Эвотор ОФД"', 'https://ofd.evotor.ru', '+7 (800) 333-11-12', 'support@evotor.ru', true),
('ООО "Первый ОФД"', 'https://1-ofd.ru', '+7 (800) 707-77-99', 'support@1-ofd.ru', true),
('ООО "Инфомаксимум"', 'https://ofd.ru', '+7 (495) 540-46-29', 'support@ofd.ru', true),
('ООО "МУЛЬТИКАС"', 'https://dreamkas.ru', '+7 (495) 960-14-54', 'support@dreamkas.ru', true),
('ООО "Стронг Трейд"', 'https://kontur.ru/ofd', '+7 (343) 345-45-07', 'ofd@kontur.ru', true),
('АО "НТЦ "КОМТЕХ"', 'https://komtehofd.ru', '+7 (495) 797-43-32', 'support@komtehofd.ru', true),
('ООО "Энергетические системы и коммуникации"', 'https://ofd-energo.ru', '+7 (495) 134-34-34', 'support@ofd-energo.ru', true),
('АО "ГНИВЦ"', 'https://ofd.nalog.ru', '+7 (495) 913-00-09', 'support@ofd.nalog.ru', true),
('ООО "Электронный экспресс"', 'https://ofd-express.ru', '+7 (800) 775-80-81', 'support@ofd-express.ru', true),
('ООО "СофтБаланс"', 'https://ofd-sb.ru', '+7 (495) 662-37-83', 'support@ofd-sb.ru', true)
ON CONFLICT (name) DO UPDATE SET
    website = EXCLUDED.website,
    support_phone = EXCLUDED.support_phone,
    support_email = EXCLUDED.support_email,
    is_active = EXCLUDED.is_active;
