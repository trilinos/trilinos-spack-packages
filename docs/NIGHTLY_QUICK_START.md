# Nightly Testing - Quick Start

**Goal:** Run tests automatically every night and submit to CDash.

## 3-Step Setup (5 minutes)

### Step 1: Create the script

```bash
cat > ~/nightly-trilinos-tests.sh << 'EOF'
#!/bin/bash
set -e
REPO_DIR="$HOME/trilinos-spack-packages"
LOG_DIR="$HOME/nightly-test-logs"
DATE=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$LOG_DIR/nightly-$DATE.log"

mkdir -p "$LOG_DIR"
cd "$REPO_DIR"

echo "[$(date)] Starting nightly tests..." | tee -a "$LOG_FILE"
git pull origin main >> "$LOG_FILE" 2>&1
./docker-build.sh >> "$LOG_FILE" 2>&1
./docker-cdash.sh Nightly >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "[$(date)] Tests completed with exit code: $EXIT_CODE" | tee -a "$LOG_FILE"
echo "View results: https://my.cdash.org/index.php?project=Trilinos" | tee -a "$LOG_FILE"

find "$LOG_DIR" -name "nightly-*.log" -mtime +30 -delete
exit $EXIT_CODE
EOF

chmod +x ~/nightly-trilinos-tests.sh
```

### Step 2: Add to crontab

```bash
crontab -e
```

Add this line:
```
3 2 * * * $HOME/nightly-trilinos-tests.sh
```

Save and exit.

### Step 3: Test it

```bash
# Run manually to verify
~/nightly-trilinos-tests.sh

# Check the log
cat ~/nightly-test-logs/nightly-*.log | tail -50
```

## Done! ✅

Tests will now run automatically every night at 2:03 AM.

View results: https://my.cdash.org/index.php?project=Trilinos

## Quick Commands

```bash
# Check crontab
crontab -l

# View recent logs
ls -lht ~/nightly-test-logs/ | head -5

# View latest log
cat ~/nightly-test-logs/nightly-*.log | tail -100

# Test script manually
~/nightly-trilinos-tests.sh
```

## Troubleshooting

**Tests not running?**
```bash
# Check if cron is running
systemctl status crond  # RHEL/CentOS
systemctl status cron   # Debian/Ubuntu

# Check cron logs
grep CRON /var/log/cron | tail -20  # RHEL/CentOS
grep CRON /var/log/syslog | tail -20  # Debian/Ubuntu
```

**Need more details?** See [README_NIGHTLY.md](README_NIGHTLY.md)
