# Nginx Configuration Templates

## 🎯 Standard Production Template (Node.js)

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        
        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        
        # Headers for proper routing
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        
        # Timeout configuration
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static assets with long cache
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # API endpoints (longer timeout)
    location /api/ {
        proxy_pass http://127.0.0.1:3000;
        proxy_read_timeout 120s;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain application/json application/javascript text/css 
               application/xml text/xml application/xml+rss text/javascript;
}
```

---

## 🐍 Python/Gunicorn Template

```nginx
upstream python_app {
    server 127.0.0.1:8000;
    keepalive 64;
}

server {
    listen 80;
    server_name your-domain.com;

    root /var/www/python-app/static;
    index index.html;

    location / {
        proxy_pass http://python_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Media files
    location /media/ {
        alias /var/www/python-app/media/;
        expires 30d;
    }

    # Static files
    location /static/ {
        alias /var/www/python-app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 🐘 PHP/Nginx Template

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/php-app/public;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_index index.php;
        fastcgi_intercept_errors on;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

---

## ⚡ Go Application Template

```nginx
upstream go_app {
    server 127.0.0.1:8080;
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://go_app;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://go_app/health;
        access_log off;
    }
}
```

---

## 📦 Docker Compose Integration Example

```nginx
# docker-compose.yml snippet
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

  certbot:
    image: certbot/certbot
    volumes:
      - ./ssl:/etc/letsencrypt
      - ./nginx-data:/var/cache/nginx
```

---

## 🔒 Security Best Practices

### 1. Disable Unnecessary Methods
```nginx
if ($request_method !~ ^(GET|HEAD|POST)$) {
    return 405;
}
```

### 2. Hide Server Version
```nginx
server_tokens off;
```

### 3. Rate Limiting
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://app:3000/api/;
}
```

### 4. Security Headers
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Optional: CSP
# add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline';" always;
```

---

## 🛠️ Testing Commands

```bash
# Test syntax
sudo nginx -t

# Reload config
sudo systemctl reload nginx

# Check active connections
ss -tlnp | grep nginx

# View error logs
sudo tail -f /var/log/nginx/error.log

# Test HTTPS
curl -I https://your-domain.com
```

---

## 🔄 Updating Config Without Downtime

```bash
# 1. Edit config
sudo nano /etc/nginx/sites-available/myapp

# 2. Test syntax
sudo nginx -t

# 3. Reload (graceful restart)
sudo systemctl reload nginx

# 4. Monitor for errors
sudo tail -f /var/log/nginx/error.log
```

Nginx will seamlessly switch configurations without dropping existing connections.
