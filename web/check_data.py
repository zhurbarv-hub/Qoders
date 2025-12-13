#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app.database import engine
from sqlalchemy import text

conn = engine.connect()
cash_count = conn.execute(text('SELECT COUNT(*) FROM cash_registers')).scalar()
deadline_count = conn.execute(text('SELECT COUNT(*) FROM deadlines WHERE cash_register_id IS NOT NULL')).scalar()
total_deadlines = conn.execute(text('SELECT COUNT(*) FROM deadlines')).scalar()

print(f"Кассовые аппараты: {cash_count}")
print(f"Дедлайны с cash_register_id: {deadline_count}")
print(f"Всего дедлайнов: {total_deadlines}")
conn.close()
