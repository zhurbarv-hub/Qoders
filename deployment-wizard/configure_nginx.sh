#!/bin/bash
# Configure Nginx for Deployment Wizard

cat > /etc/nginx/sites-available/deployment-wizard <<'EOF'
server {
    listen 443 ssl http2;
    server_name kkt-box.net;

    ssl_certificate /etc/letsencrypt/live/kkt-box.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kkt-box.net/privkey.pem;

    # Deployment wizard frontend
    location /deploy/ {
        alias /opt/kkt-deployment-wizard/frontend/;
        try_files $uri $uri/ /deploy/index.html;
    }

    # Deployment wizard API
    location /api/deploy/ {
        proxy_pass http://127.0.0.1:8100/api/deploy/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/instances/ {
        proxy_pass http://127.0.0.1:8100/api/instances/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/releases/ {
        proxy_pass http://127.0.0.1:8100/api/releases/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Existing production app (don't touch)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable and reload
ln -sf /etc/nginx/sites-available/deployment-wizard /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "Nginx configured for Deployment Wizard"
echo "Access at: https://kkt-box.net/deploy/"
