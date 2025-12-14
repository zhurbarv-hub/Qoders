#!/bin/bash
sudo -u postgres psql -d kkt_production -c "\d ofd_providers"
