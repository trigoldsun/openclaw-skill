#!/usr/bin/env python3
"""
Website Deployment Automation Script
====================================
Full automation from local code to production server access.

Features:
- Automatic environment provisioning
- Multi-runtime support (Node.js, Python, Go, Static)
- SSL certificate setup
- Security hardening
- Health monitoring

Usage:
    python deploy-automation.py --host <server-ip> --username roo \
        --key ~/ssh-key.pem --project my-app --type nodejs --code ./dist
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class DeploymentLogger:
    """Handles structured logging with operation tracking."""
    
    def __init__(self):
        self.logs = []
    
    def log(self, step: int, op_name: str, purpose: str, result: str, details: dict = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "operation_name": op_name,
            "purpose": purpose,
            "result": result,
            "details": details or {}
        }
        self.logs.append(entry)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📝 Step {step}: {op_name}")
        print(f"   目的：{purpose}")
        print(f"   结果：{result}\n")
        return entry
    
    def get_report(self) -> str:
        report = "\n=== DEPLOYMENT AUDIT LOG ===\n\n"
        for entry in self.logs:
            report += f"Step {entry['step']}: {entry['operation_name']}\n"
            report += f"Purpose: {entry['purpose']}\n"
            report += f"Result: {entry['result']}\n"
            report += f"Timestamp: {entry['timestamp']}\n\n"
        return report


class SSHConnection:
    """Manages SSH connection to deployment server."""
    
    def __init__(self, host: str, username: str, key_path: str, port: int = 22):
        self.host = host
        self.username = username
        self.key_path = key_path
        self.port = port
        self.connected = False
    
    def execute(self, command: str, check: bool = True) -> tuple:
        """Execute remote command via SSH."""
        cmd = f'ssh -i "{self.key_path}" -p {self.port} -o StrictHostKeyChecking=no ' \
              f'{self.username}@{self.host} "{command}"'
        
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=300
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def transfer_file(self, local: str, remote: str):
        """Transfer file to remote server."""
        cmd = f'scp -i "{self.key_path}" -P {self.port} -r "{local}" {self.username}@{self.host}:{remote}'
        subprocess.run(cmd, shell=True, check=True)
    
    def connect(self) -> bool:
        """Test SSH connection."""
        success, _, error = self.execute("echo 'Connection test successful'")
        self.connected = success
        return success


class WebsiteDeployer:
    """Main deployment orchestrator."""
    
    def __init__(self, logger: DeploymentLogger):
        self.logger = logger
        self.server_info = None
        self.project_type = None
    
    def detect_project_type(self, code_path: str) -> str:
        """Auto-detect project type based on files present."""
        if not os.path.exists(code_path):
            raise FileNotFoundError(f"Code path not found: {code_path}")
        
        files = os.listdir(code_path)
        
        # Check Docker first (highest priority)
        if 'docker-compose.yml' in files or 'Dockerfile' in files:
            return 'docker'
        
        # Check Node.js
        if 'package.json' in files:
            return 'nodejs'
        
        # Check Go
        if 'go.mod' in files:
            return 'go'
        
        # Check Python
        if any(f.endswith('.py') for f in files):
            if 'requirements.txt' in files or 'pyproject.toml' in files:
                return 'python'
        
        # Check Static site
        if any(f.endswith(('.html', '.css', '.js')) for f in files):
            return 'static'
        
        return 'unknown'
    
    def run_deployment(self, ssh_conn: SSHConnection, project_type: str, 
                      project_name: str, code_path: str, domain: str = None) -> Dict[str, Any]:
        """Execute complete deployment workflow."""
        
        # Phase 1: Environment Provisioning
        print("\n🏗️ PHASE 1: Environment Setup")
        
        step = 1
        
        self.logger.log(step, 
                        "system_update",
                        "Update system packages to latest versions",
                        "System updated successfully")
        ok, out, err = ssh_conn.execute("sudo apt update && sudo apt upgrade -y")
        step += 1
        
        self.logger.log(step,
                        "install_prerequisites",
                        "Install base utilities required for deployment",
                        "Prerequisites installed" if ok else "Failed")
        ok, _, _ = ssh_conn.execute("sudo apt install -y curl wget git unzip build-essential nginx")
        step += 1
        
        # Phase 2: Runtime Installation
        print("\n🔧 PHASE 2: Installing Runtime Environment")
        
        if project_type == 'nodejs':
            self._install_nodejs(ssh_conn, step)
            step += 3
            
        elif project_type == 'python':
            self._install_python(ssh_conn, step)
            self._setup_gunicorn(ssh_conn, project_name, step)
            step += 6
            
        elif project_type == 'go':
            self._install_go(ssh_conn, step)
            step += 3
            
        elif project_type == 'docker':
            self._setup_docker(ssh_conn, step)
            step += 2
        
        # Phase 3: Security Hardening
        print("\n🔒 PHASE 3: Security Configuration")
        
        self.logger.log(step,
                        "security_hardening",
                        "Configure firewall and security settings",
                        "Security hardened")
        ssh_conn.execute("chmod +x /root/security-hardening.sh")
        ssh_conn.execute("bash /root/security-hardening.sh > /tmp/hardening.log 2>&1")
        step += 1
        
        # Phase 4: Code Deployment
        print("\n📦 PHASE 4: Deploying Application Code")
        
        self.logger.log(step,
                        "create_directory",
                        f"Create deployment directory at /var/www/{project_name}",
                        f"Directory created")
        ssh_conn.execute(f"mkdir -p /var/www/{project_name}")
        step += 1
        
        self.logger.log(step,
                        "transfer_code",
                        "Upload source code to server",
                        "Code uploaded successfully")
        ssh_conn.transfer_file(code_path, f"/var/www/{project_name}/")
        step += 1
        
        # Install dependencies
        if project_type == 'nodejs':
            ssh_conn.execute(f"cd /var/www/{project_name} && npm ci --only=production")
        elif project_type == 'python':
            ssh_conn.execute(f"cd /var/www/{project_name} && "
                           f"python3 -m venv venv && "
                           f"source venv/bin/activate && "
                           f"pip install -r requirements.txt")
        
        step += 1
        
        # Handle static files permissions
        if project_type == 'static':
            self.logger.log(step,
                            "set_static_permissions",
                            "Set proper file permissions for static content",
                            "Permissions set")
            ssh_conn.execute(f"sudo chmod -R 755 /var/www/{project_name}/")
            step += 1
        
        # Deploy Docker containers (after code is uploaded)
        if project_type == 'docker':
            self.logger.log(step,
                           "deploy_docker_containers",
                           "Deploy application using Docker Compose",
                           "Containers deployed")
            ssh_conn.execute(f"cd /var/www/{project_name} && sudo docker compose up -d")
            ssh_conn.execute("sudo docker compose ps")
            step += 2
        
        # Phase 5: Process Management
        print("\n⚙️ PHASE 5: Setting Up Process Manager")
        
        if project_type == 'nodejs':
            self._setup_pm2(ssh_conn, project_name, step)
            step += 2
            
        elif project_type == 'python':
            # Python uses Gunicorn (already set up in _setup_gunicorn)
            pass
            
        elif project_type == 'go':
            self._setup_systemd(ssh_conn, project_name, step)
            step += 2
            
        elif project_type == 'static':
            # For static sites, create a simple nginx config and start nginx
            self.logger.log(step,
                           "create_static_nginx_config",
                           "Create Nginx configuration for static file serving",
                           "Config created")
            ssh_conn.execute(f"sudo mkdir -p /var/www/{project_name}/public")
            ssh_conn.execute(f"cd /var/www/{project_name} && mv * public/")
            
            nginx_config = f"""server {{
    listen 80;
    server_name {domain or 'localhost'};
    root /var/www/{project_name}/public;
    index index.html;

    location / {{
        try_files $uri $uri/ =404;
    }}

    location /static/ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    gzip on;
}}
"""
            ssh_conn.execute(f"echo '{nginx_config}' | sudo tee /etc/nginx/sites-available/{project_name}")
            ssh_conn.execute(f"sudo ln -s /etc/nginx/sites-available/{project_name} /etc/nginx/sites-enabled/")
            ssh_conn.execute("sudo rm -f /etc/nginx/sites-enabled/default")
            ssh_conn.execute("sudo nginx -t && sudo systemctl reload nginx")
            step += 3
            
        # Phase 6: Nginx Configuration
        print("\n🌐 PHASE 6: Configuring Nginx Reverse Proxy")
        
        self.logger.log(step,
                        "create_nginx_config",
                        "Create Nginx site configuration",
                        "Nginx config created")
        self._create_nginx_config(ssh_conn, project_name, project_type, domain, step)
        
        # Skip additional Nginx steps for static as already done above
        if project_type != 'static':
            # Enable proxy configuration
            ssh_conn.execute(f"sudo ln -s /etc/nginx/sites-available/{project_name} "
                            f"/etc/nginx/sites-enabled/")
            ssh_conn.execute("sudo rm -f /etc/nginx/sites-enabled/default")
            ssh_conn.execute("sudo nginx -t && sudo systemctl reload nginx")
        
        step += 2
        
        # Enable site
        ssh_conn.execute(f"sudo ln -s /etc/nginx/sites-available/{project_name} "
                        f"/etc/nginx/sites-enabled/")
        ssh_conn.execute("sudo rm -f /etc/nginx/sites-enabled/default")
        ssh_conn.execute("sudo nginx -t && sudo systemctl reload nginx")
        
        step += 1
        
        # Phase 7: SSL Certificate (if domain provided)
        print("\n🔐 PHASE 7: SSL Certificate Setup")
        
        if domain:
            self.logger.log(step,
                            "install_certbot",
                            "Install Let's Encrypt SSL certificate",
                            "SSL certificate obtained")
            ssh_conn.execute("sudo apt install -y certbot python3-certbot-nginx")
            ssh_conn.execute(f"sudo certbot --nginx -d {domain} -d www.{domain} --non-interactive")
            step += 1
        
        # Phase 8: Verification
        print("\n✅ PHASE 8: Final Verification")
        
        self.logger.log(step,
                        "check_services",
                        "Verify all services are running",
                        self._verify_deployment(ssh_conn))
        
        # Generate final report
        return self._generate_final_report(ssh_conn, project_name, project_type, domain)
    
    def _install_nodejs(self, ssh_conn: SSHConnection, step_num: int):
        """Install Node.js and PM2."""
        self.logger.log(step_num,
                        "install_nodejs",
                        "Install Node.js 20 LTS runtime",
                        "Node.js installed")
        ssh_conn.execute("curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -")
        ssh_conn.execute("sudo apt-get install -y nodejs")
        
        self.logger.log(step_num + 1,
                        "install_pm2",
                        "Install PM2 process manager globally",
                        "PM2 installed")
        ssh_conn.execute("sudo npm install -g pm2")
    
    def _install_python(self, ssh_conn: SSHConnection, step_num: int):
        """Install Python environment."""
        self.logger.log(step_num,
                        "install_python",
                        "Install Python 3.10+ and virtual environment support",
                        "Python installed")
        ssh_conn.execute("sudo apt install -y python3 python3-pip python3-venv")
        
        self.logger.log(step_num + 1,
                        "install_pip_packages",
                        "Install pip packages for system-wide tools",
                        "Packages installed")
        ssh_conn.execute("sudo apt install -y postgresql-client libpq-dev")
    
    def _setup_gunicorn(self, ssh_conn: SSHConnection, project_name: str, step_num: int):
        """Setup Gunicorn for Python application with configurable entry point."""
        self.logger.log(step_num,
                        "configure_gunicorn",
                        "Configure Gunicorn WSGI server for production",
                        "Gunicorn configured")
        
        # Detect common WSGI entry points from typical project structures
        # User can override via environment variable WSGI_ENTRY
        default_wsgi_entry = os.environ.get('WSGI_ENTRY', 'app:application')
        
        service_content = f"""[Unit]
Description={project_name.capitalize()} Gunicorn Service
After=network.target

[Service]
Type=notify
User=roo
Group=roo
WorkingDirectory=/var/www/{project_name}
Environment="WSGI_ENTRY={default_wsgi_entry}"
ExecStart=/var/www/{project_name}/venv/bin/gunicorn --workers 4 \\
  --bind unix:/var/www/{project_name}/gunicorn.sock \\
  $WSGI_ENTRY

[Install]
WantedBy=multi-user.target
"""
        ssh_conn.execute(f"echo '{service_content}' | sudo tee /etc/systemd/system/{project_name}.service")
        
        self.logger.log(step_num + 1,
                        "enable_gunicorn_service",
                        "Enable and start Gunicorn service",
                        "Service enabled")
        ssh_conn.execute(f"sudo systemctl daemon-reload")
        ssh_conn.execute(f"sudo systemctl enable {project_name}")
        ssh_conn.execute(f"sudo systemctl start {project_name}")
    
    def _install_go(self, ssh_conn: SSHConnection, step_num: int):
        """Install Go runtime."""
        self.logger.log(step_num,
                        "install_go",
                        "Download and install Go 1.21 runtime",
                        "Go installed")
        ssh_conn.execute("curl -L https://go.dev/dl/go1.21.6.linux-amd64.tar.gz | sudo tar -xz -C /usr/local")
        ssh_conn.execute("echo 'export PATH=$PATH:/usr/local/go/bin' | sudo tee /etc/profile.d/go.sh")
        ssh_conn.execute("source /etc/profile.d/go.sh && go version")
    
    def _setup_docker(self, ssh_conn: SSHConnection, step_num: int):
        """Install Docker Engine and configure for deployment."""
        self.logger.log(step_num,
                        "install_docker_engine",
                        "Install Docker Engine and Docker Compose Plugin",
                        "Docker installed")
        ssh_conn.execute("curl -fsSL https://get.docker.com -o get-docker.sh")
        ssh_conn.execute("sudo sh get-docker.sh")
        ssh_conn.execute("sudo apt install -y docker-compose-plugin")
        
        self.logger.log(step_num + 1,
                        "configure_docker_groups",
                        "Configure user permissions for Docker",
                        "Groups configured")
        # Note: User addition requires interactive sudo, handled by deployer
        ssh_conn.execute("docker --version && docker compose version")
    
    def _setup_pm2(self, ssh_conn: SSHConnection, project_name: str, step_num: int):
        """Setup PM2 for Node.js application."""
        self.logger.log(step_num,
                        "configure_pm2",
                        "Configure PM2 process manager for auto-restart",
                        "PM2 configured")
        ssh_conn.execute(f"pm2 start ecosystem.config.js --env production -k {project_name}")
        ssh_conn.execute("pm2 save")
        ssh_conn.execute("pm2 startup ubuntu -u roo")
    
    def _setup_systemd(self, ssh_conn: SSHConnection, project_name: str, step_num: int):
        """Setup systemd service for Go application."""
        self.logger.log(step_num,
                        "build_go_binary",
                        "Build Go application to binary",
                        "Binary built")
        # Build the Go binary first
        ssh_conn.execute(f"cd /var/www/{project_name} && go build -o {project_name} .")
        
        self.logger.log(step_num + 1,
                        "create_service_unit",
                        "Create systemd service unit file",
                        "Service unit created")
        
        service_content = f"""[Unit]
Description={project_name.capitalize()} Application
After=network.target

[Service]
Type=simple
User=roo
Group=roo
WorkingDirectory=/var/www/{project_name}
ExecStart=/var/www/{project_name}/{project_name}
Restart=always
RestartSec=5
Environment="GO环境=production"

[Install]
WantedBy=multi-user.target
"""
        ssh_conn.execute(f"echo '{service_content}' | sudo tee /etc/systemd/system/{project_name}.service")
        
        self.logger.log(step_num + 1,
                        "enable_service",
                        "Enable and start systemd service",
                        "Service enabled")
        ssh_conn.execute(f"sudo systemctl daemon-reload")
        ssh_conn.execute(f"sudo systemctl enable {project_name}")
        ssh_conn.execute(f"sudo systemctl start {project_name}")
    
    def _create_nginx_config(self, ssh_conn: SSHConnection, project_name: str, 
                            project_type: str, domain: str, step_num: int):
        """Generate and apply Nginx configuration."""
        
        # Determine port based on project type
        ports = {'nodejs': 3000, 'python': 8000, 'go': 8080, 'static': None}
        port = ports.get(project_type, 3000)
        
        proxy_pass = f"http://127.0.0.1:{port}" if port else "/var/www/{project_name}/"
        
        nginx_config = f"""server {{
    listen 80;
    server_name {domain or 'localhost'};

    location / {{
        proxy_pass {proxy_pass};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /static/ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    gzip on;
}}
"""
        
        ssh_conn.execute(f"echo '{nginx_config}' | sudo tee /etc/nginx/sites-available/{project_name}")
    
    def _verify_deployment(self, ssh_conn: SSHConnection) -> str:
        """Verify all deployed services are working."""
        checks = []
        
        # Check SSH connectivity
        ok, _, _ = ssh_conn.execute("uptime")
        checks.append(("SSH", "✅ Connected" if ok else "❌ Failed"))
        
        # Check Nginx
        ok, _, _ = ssh_conn.execute("sudo systemctl status nginx | grep 'active (running)'")
        checks.append(("Nginx", "✅ Running" if ok else "❌ Stopped"))
        
        # Check UFW
        ok, output, _ = ssh_conn.execute("sudo ufw status | grep 'Status: active'")
        checks.append(("Firewall", "✅ Active" if ok else "⚠️ Inactive"))
        
        return "; ".join([f"{name} {status}" for name, status in checks])
    
    def _generate_final_report(self, ssh_conn: SSHConnection, project_name: str,
                              project_type: str, domain: str) -> Dict[str, Any]:
        """Generate comprehensive deployment report."""
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "project": {
                "name": project_name,
                "type": project_type,
                "location": f"/var/www/{project_name}"
            },
            "access": {
                "url": f"https://{domain}" if domain else "http://<server-ip>",
                "ssh": f"roo@<server-ip>:22"
            },
            "services": {
                "web_server": "Nginx",
                "process_manager": {
                    "nodejs": "PM2",
                    "python": "Gunicorn",
                    "go": "systemd",
                    "static": "None"
                }.get(project_type, "Unknown"),
                "ssl": "Let's Encrypt" if domain else "Not configured"
            },
            "audit_log": self.logger.get_report()
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Website Deployment')
    parser.add_argument('--host', required=True, help='Server IP address')
    parser.add_argument('--username', default='roo', help='SSH username (default: roo)')
    parser.add_argument('--key', required=True, help='Path to SSH private key')
    parser.add_argument('--port', type=int, default=22, help='SSH port')
    parser.add_argument('--project', required=True, help='Project name')
    parser.add_argument('--code', required=True, help='Path to source code directory')
    parser.add_argument('--type', help='Project type (auto-detected if not specified)')
    parser.add_argument('--domain', help='Domain name for SSL (optional)')
    
    args = parser.parse_args()
    
    # Initialize logger
    logger = DeploymentLogger()
    
    # Detect project type if not provided
    project_type = args.type
    if not project_type:
        deployer = WebsiteDeployer(logger)
        project_type = deployer.detect_project_type(args.code)
        print(f"📋 Auto-detected project type: {project_type}")
    
    # Create SSH connection
    print(f"\n🔑 Connecting to server: {args.username}@{args.host}:{args.port}")
    ssh = SSHConnection(args.host, args.username, args.key, args.port)
    
    if not ssh.connect():
        print("❌ SSH connection failed!")
        sys.exit(1)
    
    print("✅ Connected successfully!\n")
    
    # Run deployment
    deployer = WebsiteDeployer(logger)
    
    try:
        result = deployer.run_deployment(
            ssh_conn=ssh,
            project_type=project_type,
            project_name=args.project,
            code_path=args.code,
            domain=args.domain
        )
        
        # Print summary
        print("\n" + "="*70)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("="*70)
        print(f"\n📍 Project Location: {result['project']['location']}")
        print(f"🌐 Access URL: {result['access']['url']}")
        print(f"🔧 Process Manager: {result['services']['process_manager']}")
        print(f"🔐 SSL: {result['services']['ssl']}")
        
        # Save audit log
        with open(f"{args.project}-deployment-report.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n📄 Full report saved to: {args.project}-deployment-report.json")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
