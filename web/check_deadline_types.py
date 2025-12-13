#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app.database import engine
from web.app.models.client import DeadlineType
from sqlalchemy.orm import Session

with Session(engine) as session:
    types = session.query(DeadlineType).all()
    print(f"Типы дедлайнов в БД ({len(types)}):")
    for dt in types:
        print(f"  - ID: {dt.id}, Название: '{dt.type_name}'")
