#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app.database import engine
from sqlalchemy import text

conn = engine.connect()
conn.execute(text('DELETE FROM deadlines WHERE cash_register_id IS NOT NULL'))
conn.execute(text('DELETE FROM cash_registers'))
conn.commit()
print('Кассы и связанные дедлайны удалены')
conn.close()
