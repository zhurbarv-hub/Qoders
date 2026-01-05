sudo tee /etc/nginx/sites-available/kkt-system > /dev/null << 'EOF'
server {
    listen 80;
    server_name 185.185.71.248;
    client_max_body_size 100M;
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    location /api/database/restore {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 180s;
        proxy_send_timeout 180s;
        proxy_read_timeout 180s;
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    location / {
        root /home/kktapp/kkt-system/web/app/static;
        try_files $uri $uri/ /dashboard.html;
        index dashboard.html;
    }
    location /backups/ {
        internal;
        alias /home/kktapp/kkt-system/backups/;
    }
}
EOF
sudo nginx -t && sudo systemctl reload nginx && sudo systemctl restart kkt-web.service
