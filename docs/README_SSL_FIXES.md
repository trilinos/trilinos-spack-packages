# SSL Certificate Issues - Solutions

If you're seeing SSL certificate verification errors during container builds, here are solutions.

## Error Symptoms

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
```

This happens on corporate/institutional networks with SSL inspection.

## Solution 1: Disable SSL Verification (Quick Fix)

**Use this if you need to build immediately:**

```bash
# Build with SSL verification disabled
DISABLE_SSL_VERIFY=true ./docker-build.sh
```

**Note:** This is less secure but works when corporate certificates can't be added to the container.

## Solution 2: Add Corporate CA Certificates (Recommended)

If your organization provides CA certificates, add them to the container.

### Step 1: Find your CA certificates on the host

```bash
# Common locations on RHEL/CentOS
ls /etc/pki/ca-trust/source/anchors/
ls /etc/pki/tls/certs/

# Or check what certs are installed
trust list
```

### Step 2: Create a `certs/` directory

```bash
mkdir -p certs
cp /etc/pki/ca-trust/source/anchors/*.crt certs/
```

### Step 3: Update Dockerfile

Add this after the base stage (around line 20):

```dockerfile
# Copy corporate CA certificates
COPY certs/*.crt /etc/pki/ca-trust/source/anchors/
RUN update-ca-trust extract
```

### Step 4: Build normally

```bash
./docker-build.sh
```

## Solution 3: Use Host Network (Bypass Container Network)

Sometimes the host has proper SSL setup but the container doesn't:

```bash
# Build with host network
podman build --network=host -t trilinos-spack-packages:latest .
```

Or modify docker-build.sh to add `--network=host`.

## Solution 4: Use Spack Mirrors (Offline/Cache)

If you have a local Spack mirror:

```bash
# Inside container, configure spack to use local mirror
spack mirror add local file:///path/to/mirror
spack mirror list
```

## Check Current SSL Setup

```bash
# On host, check what Python sees
python3 -c "import ssl; print(ssl.get_default_verify_paths())"

# Check if curl works
curl -v https://github.com

# Check git SSL
git config --global http.sslVerify
```

## Environment-Specific Solutions

### RHEL/CentOS with Corporate Proxy

```dockerfile
# Add to Dockerfile before spack install
ENV HTTP_PROXY=http://proxy.company.com:8080
ENV HTTPS_PROXY=http://proxy.company.com:8080
ENV NO_PROXY=localhost,127.0.0.1
```

Build:
```bash
# Pass proxy at build time
podman build \
    --build-arg HTTP_PROXY=$HTTP_PROXY \
    --build-arg HTTPS_PROXY=$HTTPS_PROXY \
    -t trilinos-spack-packages:latest .
```

### Self-Signed Certificates

If your organization uses self-signed certs:

```bash
# Export cert from host
openssl s_client -showcerts -connect mirror.spack.io:443 </dev/null 2>/dev/null | \
    openssl x509 -outform PEM > certs/spack-mirror.crt

# Add to Dockerfile
COPY certs/spack-mirror.crt /etc/pki/ca-trust/source/anchors/
RUN update-ca-trust
```

## Testing SSL After Build

```bash
# Start shell in container
./docker-run.sh shell

# Inside container, test SSL
curl -v https://github.com
curl -v https://mirror.spack.io

# Test spack
spack list | head
```

## Quick Decision Tree

1. **Need it working NOW?** → Use `DISABLE_SSL_VERIFY=true`
2. **Have corporate certs?** → Copy them to `certs/` and add to Dockerfile
3. **Behind proxy?** → Add proxy environment variables
4. **Self-signed certs?** → Export and add to ca-trust
5. **None of above?** → Contact IT department for CA certificates

## Make It Permanent

Once you find what works, update the Dockerfile:

```bash
# If disabling SSL worked, you can make it default:
# Edit Dockerfile line ~30 to:
ARG DISABLE_SSL_VERIFY=true

# Or if you added certs, keep them in certs/ directory
# and commit them to your repo (if not sensitive)
```

## Security Note

Disabling SSL verification (`DISABLE_SSL_VERIFY=true`) should only be used:
- In development/testing environments
- On trusted networks
- As a temporary workaround

For production, always use proper CA certificates.
