# Nightly Testing Guide

How to set up automated nightly test runs with CDash submission.

## Recommended Approach

**Use cron for scheduled execution** - Simple, reliable, works on any Linux system.

## Quick Setup (5 minutes)

### 1. Create a nightly test script

```bash
cat > ~/nightly-trilinos-tests.sh << 'EOF'
#!/bin/bash
set -e

# Configuration
REPO_DIR="$HOME/trilinos-spack-packages"
LOG_DIR="$HOME/nightly-test-logs"
DATE=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$LOG_DIR/nightly-$DATE.log"

# Create log directory
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Nightly Test Run Started ==="
log "Repository: $REPO_DIR"
log "Log file: $LOG_FILE"

# Navigate to repository
cd "$REPO_DIR" || exit 1

# Pull latest changes
log "Pulling latest changes from git..."
git fetch origin
git pull origin main  # or 'develop', adjust branch name

# Rebuild container (picks up any changes)
log "Rebuilding container..."
./docker-build.sh >> "$LOG_FILE" 2>&1

# Run tests and submit to CDash
log "Running tests and submitting to CDash..."
./docker-cdash.sh Nightly >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log "=== Nightly Test Run SUCCEEDED ==="
else
    log "=== Nightly Test Run FAILED (exit code: $EXIT_CODE) ==="
fi

# Cleanup old logs (keep last 30 days)
find "$LOG_DIR" -name "nightly-*.log" -mtime +30 -delete

# Print CDash link
log "View results: https://my.cdash.org/index.php?project=Trilinos"

exit $EXIT_CODE
EOF

chmod +x ~/nightly-trilinos-tests.sh
```

### 2. Add to crontab

```bash
# Open crontab editor
crontab -e

# Add this line (runs at 2 AM every night)
0 2 * * * $HOME/nightly-trilinos-tests.sh

# Or run at a specific time on the host (e.g., 2:03 AM to avoid load spikes)
3 2 * * * $HOME/nightly-trilinos-tests.sh
```

### 3. Test it manually

```bash
# Run the script to verify it works
~/nightly-trilinos-tests.sh

# Check the log
ls -lh ~/nightly-test-logs/
cat ~/nightly-test-logs/nightly-*.log
```

**That's it!** Tests will run automatically every night at 2 AM.

## Cron Schedule Examples

```bash
# Every night at 2:00 AM
0 2 * * * $HOME/nightly-trilinos-tests.sh

# Every night at 2:03 AM (avoid :00 and :30 load spikes)
3 2 * * * $HOME/nightly-trilinos-tests.sh

# Weeknights only (Monday-Friday at 2 AM)
0 2 * * 1-5 $HOME/nightly-trilinos-tests.sh

# Every night at midnight
0 0 * * * $HOME/nightly-trilinos-tests.sh

# Twice daily (2 AM and 2 PM)
0 2,14 * * * $HOME/nightly-trilinos-tests.sh
```

## Email Notifications

### Option 1: Simple email on failure

```bash
#!/bin/bash
set -e

# ... existing script content ...

# At the end of the script, send email on failure
if [ $EXIT_CODE -ne 0 ]; then
    echo "Nightly test failed. Check log: $LOG_FILE" | \
        mail -s "Trilinos Nightly Test FAILED" your-email@example.com
fi
```

### Option 2: Email with log summary

```bash
#!/bin/bash
set -e

# ... existing script content ...

# At the end, send summary email
{
    echo "Nightly Test Summary"
    echo "===================="
    echo ""
    echo "Status: $([ $EXIT_CODE -eq 0 ] && echo 'SUCCESS' || echo 'FAILED')"
    echo "Date: $(date)"
    echo "Log: $LOG_FILE"
    echo ""
    echo "Last 50 lines of log:"
    echo "====================="
    tail -50 "$LOG_FILE"
    echo ""
    echo "View results: https://my.cdash.org/index.php?project=Trilinos"
} | mail -s "Trilinos Nightly Test Report" your-email@example.com
```

### Option 3: Use CDash notifications

CDash can email you directly when tests fail. Configure in CDash web interface:
1. Go to https://my.cdash.org
2. Click on Trilinos project
3. Go to Settings → Subscribe
4. Set notification preferences

## Test Options

### Fast Nightly (Recommended)

Run all tests with `--fake` flag (current setup):
```bash
./docker-cdash.sh Nightly
```
- **Time:** ~5 minutes
- **Tests:** All packages validated (specs, dependencies)
- **Coverage:** Comprehensive
- **Best for:** Daily validation

### Comprehensive Nightly (Heavy)

Run subset with real installs:
```bash
# Remove --fake from test/long_test.py first
./docker-cdash.sh Nightly 'test_spack_(version|list|find|info)'
```
- **Time:** ~10 minutes
- **Tests:** Quick + info tests
- **Coverage:** Good
- **Best for:** Quick sanity checks

### Full Suite with Installs (Very Heavy)

```bash
# Build container with pre-built deps (one-time)
./docker-build.sh with-deps

# Run full install tests (in nightly script)
./docker-cdash.sh Nightly
```
- **Time:** ~8-9 hours first run, ~5-10 min subsequent
- **Tests:** Everything including real installs
- **Best for:** Weekly comprehensive testing

## Monitoring

### Check cron is running

```bash
# View crontab
crontab -l

# Check if cron service is running
systemctl status cron   # Debian/Ubuntu
systemctl status crond  # RHEL/CentOS

# View recent cron logs
grep CRON /var/log/syslog | tail -20   # Debian/Ubuntu
grep CRON /var/log/cron | tail -20     # RHEL/CentOS
```

### Check test logs

```bash
# List recent logs
ls -lht ~/nightly-test-logs/ | head -10

# View latest log
cat ~/nightly-test-logs/nightly-*.log | tail -100

# Search for failures
grep -i "fail\|error" ~/nightly-test-logs/nightly-*.log
```

### View results on CDash

https://my.cdash.org/index.php?project=Trilinos

Filter by:
- **Dashboard:** Nightly
- **Build Name:** Trilinos_Spack_Packages-*
- **Date:** Today

## GitHub Actions Alternative

If your repository is on GitHub, you can use GitHub Actions instead of cron:

```yaml
# .github/workflows/nightly.yml
name: Nightly Tests

on:
  schedule:
    # Run at 2:03 AM UTC every day
    - cron: '3 2 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Build container
        run: ./docker-build.sh
      
      - name: Run tests and submit to CDash
        run: ./docker-cdash.sh Nightly
      
      - name: Upload logs on failure
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: test-logs
          path: build/Testing/Temporary/LastTest.log
```

**Advantages:**
- No server maintenance
- Built-in notifications
- Artifact storage
- Easy to trigger manually

**Disadvantages:**
- Requires GitHub repository
- Runs in cloud (not on your hardware)
- Subject to GitHub Actions quotas

## Jenkins Alternative

If you have Jenkins:

```groovy
// Jenkinsfile.nightly
pipeline {
    agent any
    
    triggers {
        cron('3 2 * * *')  // 2:03 AM every day
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Container') {
            steps {
                sh './docker-build.sh'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh './docker-cdash.sh Nightly'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'build/Testing/**/*.xml', allowEmptyArchive: true
        }
        failure {
            emailext (
                subject: "Trilinos Nightly Tests FAILED",
                body: "Check Jenkins: ${env.BUILD_URL}",
                to: "team@example.com"
            )
        }
    }
}
```

## Best Practices

### 1. Run at off-peak hours
- Avoid :00 and :30 (everyone runs at these times)
- Use :03, :07, :13, etc.
- Consider timezone (2 AM local time)

### 2. Keep logs
- Retain last 30 days of logs
- Check logs periodically
- Archive important failures

### 3. Monitor CDash dashboard
- Check results daily (at least browse)
- Investigate failures promptly
- Track trends over time

### 4. Separate nightly from CI
- Use `Nightly` dashboard type for scheduled runs
- Use `Experimental` for manual/PR testing
- Use `Continuous` for CI pipelines

### 5. Use stable branches
- Run nightly against `main` or `develop`
- Avoid feature branches
- Pin to specific spack versions for consistency

### 6. Clean up disk space
```bash
# Add to nightly script after tests
docker system prune -f --volumes
find ~/nightly-test-logs -mtime +30 -delete
```

## Troubleshooting

### Tests not running

**Check cron:**
```bash
# Is cron running?
systemctl status crond

# Are there errors in cron log?
grep CRON /var/log/cron | grep nightly

# Test script manually
~/nightly-trilinos-tests.sh
```

### Tests failing

**Check logs:**
```bash
# View latest log
ls -lht ~/nightly-test-logs/ | head -1
cat ~/nightly-test-logs/nightly-*.log

# Check container status
docker ps -a | grep trilinos
docker images | grep trilinos
```

### CDash submission failing

**Check connectivity:**
```bash
# Can we reach CDash?
curl -I http://my.cdash.org

# Check for SSL issues (should use HTTP now)
grep -i ssl ~/nightly-test-logs/nightly-*.log
```

### Disk space issues

**Clean up:**
```bash
# Check disk space
df -h

# Remove old logs
find ~/nightly-test-logs -mtime +30 -delete

# Clean Docker
docker system prune -f --volumes
docker image prune -a -f
```

## Advanced: Multiple Test Configs

Run different test configurations on different schedules:

```bash
# Fast validation every night at 2 AM
3 2 * * * ~/nightly-trilinos-tests.sh fast

# Comprehensive test Sunday at 1 AM
0 1 * * 0 ~/nightly-trilinos-tests.sh full

# Quick smoke test every 6 hours
0 */6 * * * ~/nightly-trilinos-tests.sh quick
```

Then update the script:

```bash
#!/bin/bash
TEST_TYPE="${1:-fast}"

case $TEST_TYPE in
    quick)
        ./docker-cdash.sh Continuous 'test_spack_(version|list|find)'
        ;;
    fast)
        ./docker-cdash.sh Nightly
        ;;
    full)
        # Build with deps if needed
        ./docker-build.sh with-deps
        # Run everything (may take hours)
        ./docker-cdash.sh Nightly
        ;;
esac
```

## Cost Considerations

### Compute Time

**Fast nightly (~5 min):**
- Minimal CPU usage
- Can run on any machine
- No special hardware needed

**Full nightly with installs (~8-9 hours):**
- High CPU usage
- Recommend dedicated build server
- 8+ cores helpful
- Consider weekends only

### Storage

- Container images: ~500MB (default) or ~5-10GB (with-deps)
- Logs: ~1MB per night × 30 days = ~30MB
- Spack cache: ~10-50GB if doing real installs
- Plan for 100GB+ if doing comprehensive installs

## Recommended Schedule

**Daily:** Fast validation with `--fake` (5 min)
```bash
3 2 * * * ~/nightly-trilinos-tests.sh fast
```

**Weekly:** Comprehensive test on Sunday (8-9 hours)
```bash
0 1 * * 0 ~/nightly-trilinos-tests.sh full
```

**Continuous:** Quick smoke test every 6 hours
```bash
7 */6 * * * ~/nightly-trilinos-tests.sh quick
```

This gives you:
- ✅ Daily validation (catch issues within 24 hours)
- ✅ Weekly comprehensive testing (real installs)
- ✅ Continuous smoke tests (catch breakage quickly)
- ✅ Minimal resource usage

## Summary

**Simplest approach (recommended):**
1. Copy the nightly script above
2. Add one line to crontab: `3 2 * * * ~/nightly-trilinos-tests.sh`
3. Done! Tests run automatically every night

**View results:**
- https://my.cdash.org/index.php?project=Trilinos
- Filter by "Nightly" dashboard
- Look for "Trilinos_Spack_Packages" builds

Your nightly testing is now automated! 🎉
