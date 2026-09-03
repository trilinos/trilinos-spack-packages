# Multi-stage build for optimal caching and minimal test runtime
# OPTIMIZED VERSION with:
# - Dynamic dependency extraction
# - Spack build cache
# - Parallel dependency installation
# - Better layer caching

FROM registry.access.redhat.com/ubi9:latest AS base

# Disable all host repositories
RUN rm -rf /etc/rhsm-host

# Update base system
RUN yum -y --setopt=tsflags=nodocs update && yum clean all

# Install system dependencies (cached layer)
RUN yum -y install \
    gcc gcc-c++ gcc-gfortran \
    xz bzip2 patch diffutils file make \
    git python3-devel procps \
    environment-modules gettext unzip \
    libX11-devel cmake \
    ca-certificates \
    && yum clean all

# Update CA certificates
RUN update-ca-trust

# FIXME: Remove this someday
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /opt/trilinos-spack-packages

# ============================================
# Stage: Spack Setup (heavily cached)
# ============================================
FROM base AS spack-base

# Disable SSL verification for corporate networks
ENV GIT_SSL_NO_VERIFY=1
ENV CURL_CA_BUNDLE=""
ENV REQUESTS_CA_BUNDLE=""

# Clone and setup spack (this layer is cached unless spack version changes)
RUN git -c http.sslVerify=false clone --depth 1 https://github.com/spack/spack.git /opt/spack-src

# Pre-configure spack environment
ENV SPACK_ROOT=/opt/spack-src
ENV PATH="${SPACK_ROOT}/bin:${PATH}"

# Configure spack to disable SSL verification and enable build cache
RUN mkdir -p /root/.spack && \
    echo 'config:' > /root/.spack/config.yaml && \
    echo '  verify_ssl: false' >> /root/.spack/config.yaml && \
    echo '  connect_timeout: 60' >> /root/.spack/config.yaml && \
    echo '  suppress_gpg_warnings: true' >> /root/.spack/config.yaml && \
    echo '  install_tree:' >> /root/.spack/config.yaml && \
    echo '    padded_length: 128' >> /root/.spack/config.yaml && \
    echo '  build_jobs: 4' >> /root/.spack/config.yaml

# Configure bootstrap to skip SSL
RUN mkdir -p /root/.spack && \
    echo 'bootstrap:' > /root/.spack/bootstrap.yaml && \
    echo '  enable: true' >> /root/.spack/bootstrap.yaml && \
    echo '  root: $spack/opt/bootstrap' >> /root/.spack/bootstrap.yaml && \
    echo '  trusted:' >> /root/.spack/bootstrap.yaml && \
    echo '    github-actions-v2: false' >> /root/.spack/bootstrap.yaml && \
    echo '    github-actions-v0.6: false' >> /root/.spack/bootstrap.yaml && \
    echo '    spack-install: true' >> /root/.spack/bootstrap.yaml

# Add spack build cache for binary packages
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack mirror add binary_mirror https://binaries.spack.io/develop && \
    spack buildcache keys --install --trust || true"

# Initialize spack shell support
RUN echo 'source /opt/spack-src/share/spack/setup-env.sh' >> /root/.bashrc

# Install core spack dependencies (cached layer - slowest step)
# OPTIMIZATION: Install in single command to share dependency resolution
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    export PYTHONHTTPSVERIFY=0 && \
    export PIP_TRUSTED_HOST='pypi.org pypi.python.org files.pythonhosted.org' && \
    spack compiler find && \
    spack install -y python py-pytest cmake"

# ============================================
# Stage: Python Dependencies
# ============================================
FROM spack-base AS python-deps

# Copy only requirements first for optimal caching
COPY requirements.txt /opt/trilinos-spack-packages/

# Install Python test dependencies using Spack's Python (cached if requirements.txt unchanged)
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack load python && \
    export PYTHONHTTPSVERIFY=0 && \
    export PIP_TRUSTED_HOST='pypi.org pypi.python.org files.pythonhosted.org' && \
    pip3 install --no-cache-dir pytest pytest-xdist"

# ============================================
# Stage: Heavy Dependencies (OPTIMIZED)
# ============================================
FROM python-deps AS deps-cache

# Copy dependency extraction script and base package
COPY tools/extract_dependencies.py /opt/
COPY spack_repo/trilinos/packages/trilinos_base_class/package.py /opt/base_package.py

# Extract and install dependencies
# OPTIMIZATION: Dependencies determined dynamically from source code
RUN bash -c "set -e && \
    source /opt/spack-src/share/spack/setup-env.sh && \
    python3 /opt/extract_dependencies.py /opt && \
    echo '=== Dependency Hash ===' && \
    cat /opt/dependencies.lock | grep hash && \
    echo '=== Installing Independent Dependencies in Parallel ===' && \
    independent=\$(grep -v '^#' /opt/dependencies.txt | sed -n '1,/^$/p' | grep -v '^$') && \
    echo \"\$independent\" && \
    if [ -n \"\$independent\" ]; then \
        spack install -y \$independent; \
    fi && \
    echo '=== Installing Dependent Packages ===' && \
    dependent=\$(grep -v '^#' /opt/dependencies.txt | sed -n '/^$/,\$p' | grep -v '^$') && \
    echo \"\$dependent\" && \
    if [ -n \"\$dependent\" ]; then \
        for dep in \$dependent; do \
            spack install -y \$dep; \
        done; \
    fi && \
    spack clean -a"

# Save dependency lock for cache invalidation checks
RUN cp /opt/dependencies.lock /opt/trilinos-spack-packages/

# ============================================
# Stage: Application Code
# ============================================
FROM deps-cache AS app

# Copy application code
COPY . /opt/trilinos-spack-packages/

# Add trilinos spack repository (uses local code)
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack repo add /opt/trilinos-spack-packages/spack_repo/trilinos"

# Note: Packages are available via entrypoint script (loaded there)
# We don't load them here to avoid multi-version conflicts during build

# Create entrypoint script with better error handling for multiple versions
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'source /opt/spack-src/share/spack/setup-env.sh' >> /entrypoint.sh && \
    echo '# Load packages, using --first for packages with multiple versions' >> /entrypoint.sh && \
    echo 'spack load python' >> /entrypoint.sh && \
    echo 'spack load --first cmake' >> /entrypoint.sh && \
    echo 'cd /opt/trilinos-spack-packages' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Default command runs fast tests
CMD ["pytest", "test/", "-m", "quick", "-n", "auto", "-v"]

# ============================================
# Stage: Test Runner (optional, for CI)
# ============================================
FROM app AS test

# This stage can be used for CI pipelines
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack load python && \
    spack load --first cmake && \
    cd /opt/trilinos-spack-packages && \
    pytest test/ -m quick -v"
