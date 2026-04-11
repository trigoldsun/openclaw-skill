#!/bin/bash
# =============================================================================
# Server Security Hardening Script
# 
# Purpose: Automatically configure Ubuntu server security best practices
# Target Environment: Alibaba Cloud ECS with roo user
# Usage: sudo bash security-hardening.sh
# =============================================================================

set -e

echo "🔒 Starting Security Hardening Process..."
echo "Timestamp: $(date)"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# Step 1: Update System Packages
# =============================================================================
log_info "Step 1: Updating system packages..."
apt update && apt upgrade -y
log_info "System updated successfully"

# =============================================================================
# Step 2: Install Essential Security Tools
# =============================================================================
log_info "Step 2: Installing security tools..."
apt install -y \
    ufw \
    fail2ban \
    sshguard \
    unattended-upgrades \
    rkhunter \
    chkrootkit \
    lynis || true

log_info "Security tools installed"

# =============================================================================
# Step 3: Configure UFW Firewall
# =============================================================================
log_info "Step 3: Configuring UFW firewall..."

# Reset UFW to default
ufw --force reset > /dev/null 2>&1 || true

# Deny all incoming, allow all outgoing by default
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (adjust if using non-standard port)
SSH_PORT=${SSH_PORT:-22}
ufw allow ${SSH_PORT}/tcp
log_info "Allowing SSH on port ${SSH_PORT}"

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
log_info "Allowing HTTP/HTTPS"

# Optional: Allow specific IP ranges for admin access
# ufw allow from 192.168.1.0/24 to any port 22

# Enable UFW with confirmation prompt disabled
echo "y" | ufw --force enable
log_info "UFW firewall enabled"

# Show status
ufw status verbose

# =============================================================================
# Step 4: Configure Fail2Ban
# =============================================================================
log_info "Step 4: Configuring Fail2Ban..."

cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
backend = systemd

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 86400

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF

systemctl enable fail2ban
systemctl restart fail2ban
log_info "Fail2Ban configured and restarted"

# =============================================================================
# Step 5: SSH Hardening
# =============================================================================
log_info "Step 5: Hardening SSH configuration..."

# Backup original config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

cat > /etc/ssh/sshd_config.d/hardening.conf << 'EOF'
# Disable root login
PermitRootLogin no

# Disable password authentication (use keys only)
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM yes

# Change SSH port (optional - uncomment and set your port)
# Port 2222

# Limit users who can SSH
# AllowUsers roo adminuser

# Disable empty passwords
PermitEmptyPasswords no

# Disable X11 forwarding
X11Forwarding no

# Login grace time
LoginGraceTime 60

# Client alive settings (prevent idle disconnection)
ClientAliveInterval 300
ClientAliveCountMax 2

# Only use protocol 2
Protocol 2

# Ciphers and MACs (stronger encryption)
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
EOF

# Restart SSH service
systemctl restart sshd || systemctl restart ssh
log_info "SSH hardened"

# =============================================================================
# Step 5.5: Configure Log Rotation (prevent disk space issues)
# =============================================================================
log_info "Step 5.5: Configuring log rotation to prevent disk space issues..."

cat > /etc/logrotate.d/webapps << 'EOF'
/var/www/*/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 roo roo
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}

/var/log/nginx/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 $(cat /var/run/nginx.pid)
    endscript
}
EOF

systemctl restart rsyslog 2>/dev/null || service rsyslog restart 2>/dev/null || true
log_info "Log rotation configured for /var/www/* and /var/log/nginx/"

# =============================================================================
# Step 6: Configure Unattended Upgrades
# =============================================================================
log_info "Step 6: Configuring automatic security updates..."

cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
EOF

# Enable mail notifications (optional)
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Mail "root@localhost";
Unattended-Upgrade::MailReport "on-change";
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
EOF

systemctl enable unattended-upgrades
systemctl start unattended-upgrades
log_info "Automatic security updates enabled"

# =============================================================================
# Step 7: Set File Permissions and Ownership
# =============================================================================
log_info "Step 7: Securing sensitive files..."

# Secure log files
chmod 640 /var/log/auth.log
chown root:adm /var/log/auth.log

# Secure SSH directory
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 644 ~/.ssh/authorized_keys

# Remove world-writable files
find /tmp -type f -perm -o+w -exec chmod o-w {} \; 2>/dev/null || true

log_info "File permissions secured"

# =============================================================================
# Step 8: Create SSH Key for roo User (if not exists)
# =============================================================================
log_info "Step 8: Setting up SSH key authentication for roo user..."

# Check if roo user exists (uid will be a number > 0 for regular users)
if id roo &>/dev/null; then
    ROO_HOME=$(eval echo ~roo)
    mkdir -p $ROO_HOME/.ssh
    touch $ROO_HOME/.ssh/authorized_keys
    
    # Read public key from environment or create new
    if [ -n "$ROO_SSH_PUBLIC_KEY" ]; then
        echo "$ROO_SSH_PUBLIC_KEY" >> $ROO_HOME/.ssh/authorized_keys
    else
        log_warn "No SSH public key provided. Please add yours manually."
    fi
    
    chown -R roo:roo $ROO_HOME/.ssh
    chmod 700 $ROO_HOME/.ssh
    chmod 600 $ROO_HOME/.ssh/authorized_keys
    
    log_info "SSH setup for roo user complete"
else
    log_error "roo user does not exist on this system"
    log_info "Please create the user first: sudo adduser roo && usermod -aG sudo roo"
fi

# =============================================================================
# Step 9: Run Lynis Security Audit
# =============================================================================
log_info "Step 9: Running Lynis security audit..."

if command -v lynis &> /dev/null; then
    lynis audit system --quiet
    log_info "Security audit completed"
else
    log_warn "Lynis not available, skipping audit"
fi

# =============================================================================
# Step 10: Generate Security Report
# =============================================================================
log_info "Generating security report..."

cat > /home/roo/security-report.txt << EOF
================================================================================
SERVER SECURITY HARDENING REPORT
Generated: $(date)
Server: $(hostname)
================================================================================

✅ Completed Configurations:

1. [✓] System packages updated
2. [✓] UFW firewall enabled
   - Allowed ports: ${SSH_PORT} (SSH), 80 (HTTP), 443 (HTTPS)
3. [✓] Fail2Ban configured
   - Protects against SSH brute-force attacks
4. [✓] SSH hardened
   - Root login disabled
   - Password auth disabled
   - Strong ciphers enabled
5. [✓] Automatic security updates enabled
6. [✓] Sensitive file permissions secured

📊 Current Status:

Firewall:
$(ufw status verbose 2>/dev/null || echo "N/A")

Fail2Ban Services:
$(systemctl list-units --type=service | grep fail2ban || echo "N/A")

Last Security Update:
$(dpkg-query -W -f='${Installed-Date}\n' ubuntu-security-notices 2>/dev/null || echo "Unknown")

⚠️ Next Steps:

1. Test SSH connection before closing current session
2. Monitor logs for blocked attempts: tail -f /var/log/fail2ban.log
3. Add your IP to whitelist if needed
4. Review Lynis report at /var/log/lynis/
5. Regularly run: sudo unattended-upgrade --dry-run -v

================================================================================
EOF

cp /home/roo/security-report.txt /root/security-report.txt 2>/dev/null || true
log_info "Security report saved to /home/roo/security-report.txt"

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "============================================================================="
echo "🎉 Security hardening completed successfully!"
echo "============================================================================="
echo ""
echo "Summary of enabled protections:"
echo "  • Firewall: UFW active"
echo "  • Intrusion prevention: Fail2Ban running"
echo "  • SSH: Key-only authentication enforced"
echo "  • Updates: Automatic security patches enabled"
echo "  • Audit: Complete security baseline established"
echo ""
echo "📄 Full report: /home/roo/security-report.txt"
echo "🔍 Monitor logs: journalctl -u fail2ban -f"
echo ""
