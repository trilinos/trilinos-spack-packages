# Podman Quick Reference

Since you're using Podman, here are some helpful tips specific to your setup.

## Why Podman?

- **Rootless**: Runs without root privileges (more secure)
- **Daemonless**: No background daemon process
- **Docker-compatible**: Same CLI as Docker
- **Pod support**: Can run multiple containers as a pod

## Quick Commands

```bash
# Build image
./docker-build.sh    # Script auto-detects podman

# Run tests
./docker-run.sh quick
./docker-run.sh fast
./docker-run.sh full

# Or use make
make build
make test-quick
```

## Podman-Specific Features

### Rootless Mode (Default)

Your containers run as your user, not root:

```bash
# Check if running rootless
podman info | grep rootless

# Should show: rootless: true
```

### Managing Images

```bash
# List images
podman images

# Remove image
podman rmi trilinos-spack-packages:latest

# Clean up everything
podman system prune -a
```

### Managing Containers

```bash
# List running containers
podman ps

# List all containers
podman ps -a

# Stop container
podman stop <container_id>

# Remove container
podman rm <container_id>
```

### Volumes

```bash
# List volumes
podman volume ls

# Inspect volume
podman volume inspect spack-cache

# Remove volume
podman volume rm spack-cache
```

## SELinux Integration (RHEL/CentOS)

If you're on RHEL/CentOS with SELinux enabled, Podman handles it automatically. For volume mounts:

```bash
# Auto-relabel for shared access (most common)
podman run -v $(pwd)/test:/opt/trilinos-spack-packages/test:z ...

# Auto-relabel for private access
podman run -v $(pwd)/test:/opt/trilinos-spack-packages/test:Z ...
```

Our scripts handle this automatically, but if you run manual commands and get permission errors, add `:z` flag.

## Podman Compose

If you want to use docker-compose.yml:

```bash
# Install
pip3 install --user podman-compose

# Use it
podman-compose up test-quick
podman-compose up test-fast
podman-compose run shell
```

## Performance Tips

### Use Local Storage

Podman stores images in `~/.local/share/containers` by default. If you have limited home quota:

```bash
# Check current usage
podman system df

# Clean up old images/containers
podman system prune -a
```

### Build Cache

Podman uses layer caching like Docker:

```bash
# First build: ~15-20 minutes
./docker-build.sh

# Rebuild after code change: ~30 seconds
./docker-build.sh

# Force rebuild without cache
USE_CACHE=false ./docker-build.sh
```

## Troubleshooting

### "Permission denied" on volumes

Add `:z` flag:
```bash
podman run -v $(pwd):/opt/trilinos-spack-packages:z ...
```

### "No space left on device"

Clean up:
```bash
podman system prune -a
podman volume prune
```

### Check what's using space

```bash
podman system df
du -sh ~/.local/share/containers/storage
```

### Container won't start

Check logs:
```bash
podman logs <container_id>
podman events  # Watch in real-time
```

## Podman vs Docker Differences

| Feature | Podman | Docker |
|---------|--------|--------|
| Root required | No (rootless) | Yes (daemon as root) |
| Background daemon | No | Yes (dockerd) |
| Systemd integration | Native | External |
| Docker CLI compatible | Yes | N/A |
| Docker Compose | podman-compose | docker-compose |

## Integration with systemd

You can generate systemd units for your containers:

```bash
# Generate systemd service
podman generate systemd --new --name trilinos-test > ~/.config/systemd/user/trilinos-test.service

# Enable and start
systemctl --user enable trilinos-test
systemctl --user start trilinos-test
```

## Aliases (Optional)

If you want Docker aliases for muscle memory:

```bash
# Add to ~/.bashrc
alias docker=podman
alias docker-compose=podman-compose
```

## Resources

- Podman docs: https://docs.podman.io/
- Podman vs Docker: https://docs.podman.io/en/latest/Introduction.html
- Rootless containers: https://github.com/containers/podman/blob/main/rootless.md
