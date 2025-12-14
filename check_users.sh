#!/bin/bash
su - postgres -c "psql kkt_production -c 'SELECT id, username, email, role, is_active FROM web_users;'"
