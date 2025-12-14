INSERT INTO deadlines (client_id, deadline_type_id, expiration_date, status, notes)
VALUES 
    (4, 1, CURRENT_DATE + 30, 'active', 'OFD renewal for Test Company'),
    (4, 2, CURRENT_DATE + 45, 'active', 'FN replacement for Test Company'),
    (5, 1, CURRENT_DATE + 20, 'active', 'OFD renewal for Roga i Kopyta'),
    (5, 3, CURRENT_DATE + 60, 'active', 'KKT registration for Roga i Kopyta'),
    (6, 2, CURRENT_DATE + 15, 'active', 'FN replacement for IP Vasiliev'),
    (6, 4, CURRENT_DATE + 90, 'active', 'Service maintenance for IP Vasiliev');

SELECT 'Deadlines added:', COUNT(*) FROM deadlines;
