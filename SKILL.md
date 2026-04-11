---
name: website-deploy
description: Full-automation website deployment to Ubuntu Alibaba Cloud ECS. Provide code + SSH credentials (roo@host:port) → I handle everything from server provisioning to public access. Supports Node.js/Python/Go/Frontend backends. Automatically installs Nginx, PM2/Docker, SSL certificates, firewall rules, and monitors health. One-command deployment from local development to production.
---

# 🚀 Full-Automation Website Deployment

## Overview

One-command deployment from local development to public production server. Just provide:
1. **Your source code** (zip/local repo path)
2. **SSH credentials** (`roo@your-server-ip:port`)

I will automatically handle **all** steps until your website is publicly accessible.

---

## 📊 Deployment Flowchart

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Receive   │────▶│  Environment │────▶│    Install   │
│  Code + SSH │     │  Provisioning│     │   Dependencies│
└─────────────┘     └──────────────┘     └──────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Monitor   │◀────│  Security &  │◀────│   Deploy     │
│  & Health   │     │   SSL Config │     │    Codebase  │
└─────────────┘     └──────────────┘     └──────────────┘
                                              ▲
                                    ┌─────────┘
                                    │
                              ┌──────────────┐
                              │ Firewall &   │
                              │ Port Forward │
                              └──────────────┘
```

---

## 🔧 Supported Technology Stacks

| Stack Type | Tools | Auto-Detection |
|------------|-------|----------------|
| **Node.js** | npm/yarn/pnpm, PM2 | `package.json` detected |
| **Python** | pip/poetry/conda, Gunicorn/Uvicorn | `requirements.txt`, `pyproject.toml` |
| **Go** | go build, systemd | `go.mod` detected |
| **Static Site** | Nginx/Apache only | `index.html`, `css/`, `js/` folders |
| **Docker** | Docker Compose | `docker-compose.yml` present |
| **PHP** | PHP-FPM + Nginx | `.php` files detected |

---

## 🛠️ Standard Tool Selection Philosophy

### Why These Tools?

| Tool | Reason for Selection |
|------|---------------------|
| **Nginx** | Most popular web server, excellent reverse proxy |
| **PM2** (for Node) | Process manager with auto-restart & logging |
| **UFW** | Ubuntu firewall standard, simple syntax |
| **Certbot/Let's Encrypt** | Free SSL certificates, automated renewal |
| **Git** | Version control & seamless updates |

**Alternative options available:** Apache, Supervisor, Docker Swarm, Caddy

---

## 📋 Pre-Deployment Checklist

Before starting deployment, verify:

1. ✅ **Server Access:** SSH key/password for `roo@ip:port`
2. ✅ **Security Group:** Alibaba Cloud console allows ports 80, 443, 22
3. ✅ **Domain Name** (optional): A record points to server IP
4. ✅ **Project Type:** Know if Node.js/Python/etc. for optimization

---

## 🎯 Complete Deployment Workflow

### Phase 1: Environment Setup

#### Step 1.1: System Update
```bash
sudo apt update && sudo apt upgrade -y
```
**目的：** 确保所有系统包为最新版本，避免安全漏洞

#### Step 1.2: Install Core Utilities
```bash
sudo apt install -y curl wget git unzip zip build-essential
```
**目的：** 基础工具准备，后续安装依赖使用

---

### Phase 2: Runtime Installation

#### For Node.js Applications:
```bash
# Install Node.js 20 LTS via NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 globally
sudo npm install -g pm2
```
**目的：** 提供 Node.js 运行环境和进程管理器

#### For Python Applications:
```bash
# Install Python 3.10+ and pip
sudo apt install -y python3 python3-pip python3-venv

# Optional: Install PostgreSQL client
sudo apt install -y postgresql-client libpq-dev
```
**目的：** 提供 Python 虚拟环境支持

#### For Docker Applications (Recommended for Production):
```bash
# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose Plugin
sudo apt install -y docker-compose-plugin

# Add current user to docker group (replace with actual username)
sudo usermod -aG docker $USER

# Verify installation
docker --version && docker compose version
```
**目的：** 提供容器化运行环境，支持一键启动多容器服务

---

### Phase 2B: Docker Deployment Workflow

For projects with `docker-compose.yml`:

#### Step 2B.1: Deploy Docker Compose
```bash
# Navigate to project directory
cd /var/www/{project-name}

# Start all services
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f
```

#### Step 2B.2: Configure Nginx Reverse Proxy for Containers

**Important: Verify Docker Compose Port Mappings First:**

Check your `docker-compose.yml` to see which ports are exposed:
```yaml
services:
  web:
    ports:
      - "3000:3000"  # Host Port : Container Port
  db:
    # No port exposure needed for database
```

The **Host Port (left side)** is what Nginx should proxy to.

**Configure Nginx:**
Create `/etc/nginx/sites-available/docker-app`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Replace 3000 with the actual host port from docker-compose.yml
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/docker-app /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

**目的：** 将 Docker 容器暴露到公网访问，确保端口映射正确

**优势：**
- ✅ 环境一致性：开发/生产环境完全一致
- ✅ 快速扩展：通过 K8s/Docker Swarm 横向扩展
- ✅ 资源隔离：每个服务独立运行
- ✅ 易于维护：只需管理 docker-compose.yml

---

#### For PHP Applications:
```bash
# Install PHP and required extensions for common frameworks (Laravel, WordPress)
sudo apt install -y php php-fpm php-mysql php-curl php-gd php-mbstring php-xml php-xmlrpc php-bz2 php-zip

# Install Nginx if not already installed
sudo apt install -y nginx

# Install MySQL client (for database connectivity)
sudo apt install -y mysql-client libmysqlclient-dev
```

### Phase 2C: PHP Deployment Workflow

#### Step 2C.1: Configure PHP-FPM Pool
Create `/etc/php/8.1/fpm/pool.d/{project}.pool`:
```ini
[{project}]
user = www-data
group = www-data
listen = 127.0.0.1:9000
listen.owner = www-data
listen.mode = 660

pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3

catch_workers_output = yes
decode_uploads = 0

env[HOSTNAME] = $HOSTNAME
env[ROOT] = /var/www/{project-name}
env[DOCUMENT_ROOT] = /var/www/{project-name}/public_html
```

#### Step 2C.2: Configure Nginx for PHP
Create `/etc/nginx/sites-available/{project}`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/{project-name}/public_html;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        fastcgi_index index.php;
        include fastcgi_params;
    }

    # Deny access to .htaccess files
    location ~ /\.ht {
        deny all;
    }
}
```

#### Step 2C.3: Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/{project} /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart php8.1-fpm
sudo systemctl reload nginx
```

**目的：** 完整配置 PHP 应用程序环境，支持 Laravel/WordPress/Django 等框架

---

#### For Go Applications:
```bash
# Install Go 1.21+
curl -L https://go.dev/dl/go1.21.6.linux-amd64.tar.gz | \
  sudo tar -xz -C /usr/local
export PATH=$PATH:/usr/local/go/bin
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
```
**目的：** 编译和运行 Go 程序

---

### Phase 3: Project Deployment

#### Step 3.1: Create Project Directory
```bash
mkdir -p /var/www/{project-name}
cd /var/www/{project-name}
```
**目的：** 标准部署目录，便于管理

#### Step 3.2: Transfer Code Files
```bash
# Option A: Git clone (recommended)
git clone {repo-url} .

# Option B: Unzip uploaded archive
unzip -o deploy.zip

# Option C: SCP from local
scp -r ./dist/* roo@server:/var/www/{project-name}/
```
**目的：** 将代码部署到服务器

#### Step 3.3: Install Dependencies

**Node.js:**
```bash
npm ci --only=production
# or yarn install --frozen-lockfile
```
**目的：** 仅安装生产依赖，加速启动

**Python:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
**目的：** 隔离项目依赖环境

---

### Phase 4: Process Management

#### Node.js Application (PM2):
```bash
pm2 start ecosystem.config.js --env production
# or
pm2 start app.js --name "{project-name}" --node-args="--max-old-space-size=512"

pm2 save
pm2 startup ubuntu -u roo
```
**目的：** 保证服务开机自启和崩溃自动重启

#### Python Application (Gunicorn with Systemd):
```bash
# Create systemd service file
sudo tee /etc/systemd/system/{project-name}.service > /dev/null << 'EOF'
[Unit]
Description={Project Name} Gunicorn Service
After=network.target

[Service]
Type=notify
User=roo
Group=roo
WorkingDirectory=/var/www/{project-name}
ExecStart=/var/www/{project-name}/venv/bin/gunicorn --workers 4 \
  --bind unix:/var/www/{project-name}/gunicorn.sock \
  {wsgi_module}:application

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable {project-name}
sudo systemctl start {project-name}

# Replace {wsgi_module} with your actual WSGI entry point:
# - Django: myproject.wsgi:application
# - Flask: app:app
# - FastAPI: main:app
```
**目的：** 使用 systemd 管理 Gunicorn，实现开机自启和崩溃自动重启

#### Go Application (Systemd):
Create `/etc/systemd/system/{project}.service`:
```ini
[Unit]
Description={Project Name}
After=network.target

[Service]
Type=simple
User=roo
WorkingDirectory=/var/www/{project-name}
ExecStart=/usr/local/go/bin/go run main.go
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable {project}
sudo systemctl start {project}
```
**目的：** 原生系统级守护进程管理

---

### Phase 5: Nginx Reverse Proxy

#### Create Configuration File:
```bash
sudo nano /etc/nginx/sites-available/{project}
```

**Content (Node.js example):**
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static assets cache
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;
}
```
**目的：** 作为反向代理转发流量到应用，配置 HTTPS 和缓存

#### Enable Site:
```bash
sudo ln -s /etc/nginx/sites-available/{project} /etc/nginx/sites-enabled/
sudo rm -rf /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```
**目的：** 启用站点并重新加载 Nginx

---

### Phase 6: SSL Certificate (HTTPS)

#### Install Certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
```

#### Obtain Certificate:
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```
**目的：** 免费获取 Let's Encrypt 证书并自动配置

#### Auto-Renewal Test:
```bash
sudo certbot renew --dry-run
```
**目的：** 验证证书自动续期正常（30 天到期前自动续期）

---

### Phase 7: Firewall & Security

#### UFW Configuration:
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw allow 22/tcp  # SSH port if changed from default
sudo ufw --force enable
```
**目的：** 只开放必要端口，提高安全性

#### Optional Security Enhancements:
```bash
# Fail2Ban for SSH brute-force protection
sudo apt install -y fail2ban
sudo systemctl enable fail2ban

# Disable root login
sudo sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config
sudo service ssh restart
```
**目的：** 防止暴力破解攻击

---

### Phase 8: Database (Optional)

#### Install MySQL/MariaDB:
```bash
sudo apt install -y mysql-server
sudo mysql_secure_installation
```

#### Or PostgreSQL:
```bash
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql
CREATE DATABASE project_db;
CREATE USER project_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE project_db TO project_user;
```
**目的：** 为应用提供持久化数据存储

---

### Phase 9: Verification & Testing

#### Check Service Status:
```bash
# PM2 status
pm2 status
pm2 logs {project-name}

# Systemd status
systemctl status {project}

# Nginx status
sudo systemctl status nginx
```
**目的：** 确认各组件正常运行

#### External Access Test:
1. Visit: `https://your-domain.com`
2. Check SSL: Browser shows 🔒 lock icon
3. Verify functionality: Load test page/API endpoint

---

## 📝 Reporting Format per Operation

Following the established protocol, every action includes:

```
## [Step Number] · [Operation Name]

**目的：** [Why you're doing this]

**操作细节：**
- Input: [Parameters/Arguments]
- Process: [What actions taken]
- Output: [Results/Changes made]

**审计记录：**
- Timestamp: [Time]
- Operator: [Who executed]
- Change Log: [Before → After]
```

---

## ⚙️ Example: One-Command Deployment Command

Create a shell script `deploy.sh`:

```bash
#!/bin/bash
set -e

PROJECT_NAME="$1"
SOURCE_CODE_PATH="$2"
DOMAIN="$3"
ROO_SSH_KEY="$4"

echo "🚀 Starting deployment for $PROJECT_NAME..."

# 1. Connect and provision
ssh -i "$ROO_SSH_KEY" roo@$SERVER_IP << 'EOF'
    echo "✅ Connecting to server..."
    # Run provisioning commands
    # ... (all phases above)
EOF

# 2. Transfer code
scp -i "$ROO_SSH_KEY" -r "$SOURCE_CODE_PATH"/* roo@$SERVER_IP:/var/www/$PROJECT_NAME/

# 3. Trigger deployment
echo "📦 Uploading code..."

# 4. Final verification
echo "🔍 Checking health..."
curl -k https://localhost/health

echo "✅ Deployment complete! Access at: https://$DOMAIN"
```

---

## 🔄 Continuous Deployment (Optional)

### GitHub Webhook Integration:
```bash
# Install webhook
sudo snap install webhook

# Configure trigger
echo '{
  "event": "push",
  "repository": "{repo-url}"
}' > /etc/webhooks/deploy.json

# Run deployment on push
git pull origin main
pm2 restart {project-name}
```

**目的：** 自动化 CI/CD 流程，每次推送触发自动部署

---

## 📚 Additional Resources

See bundled references:
- [nginx-configs.md](references/nginx-configs.md) - 预配置的 Nginx 模板
- [ecosystem.config.js](references/ecosystem.config.js.example) - PM2 配置文件示例
- [security-hardening.sh](scripts/security-hardening.sh) - 安全加固脚本

## Resources (optional)

Create only the resource directories this skill actually needs. Delete this section if no resources are required.

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Codex for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Codex's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Codex should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Codex produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Not every skill requires all three types of resources.**
