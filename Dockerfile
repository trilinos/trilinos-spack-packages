# Multi-stage build for optimal caching and minimal test runtime
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

# Configure spack to disable SSL verification
RUN mkdir -p /root/.spack && \
    cat > /root/.spack/config.yaml << 'EOF'
config:
  verify_ssl: false
  connect_timeout: 60
  suppress_gpg_warnings: true
EOF

# Configure bootstrap to skip SSL
RUN mkdir -p /root/.spack && \
    cat > /root/.spack/bootstrap.yaml << 'EOF'
bootstrap:
  enable: true
  root: $spack/opt/bootstrap
  trusted:
    github-actions-v2: false
    github-actions-v0.6: false
    spack-install: true
EOF

# Initialize spack shell support
RUN echo 'source /opt/spack-src/share/spack/setup-env.sh' >> /root/.bashrc

# Install core spack dependencies (cached layer - slowest step)
# Set Python to ignore SSL as well
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    export PYTHONHTTPSVERIFY=0 && \
    export PIP_TRUSTED_HOST='pypi.org pypi.python.org files.pythonhosted.org' && \
    spack compiler find && \
    spack install -y python && \
    spack install -y py-pytest && \
    spack install -y cmake"

# ============================================
# Stage: Python Dependencies
# ============================================
FROM spack-base AS python-deps

# Copy only requirements first for optimal caching
COPY requirements.txt /opt/trilinos-spack-packages/

# Install Python test dependencies using Spack's Python (cached if requirements.txt unchanged)
# Install pytest itself via pip so it sees pytest-xdist properly
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack load python && \
    export PYTHONHTTPSVERIFY=0 && \
    export PIP_TRUSTED_HOST='pypi.org pypi.python.org files.pythonhosted.org' && \
    pip3 install --no-cache-dir pytest pytest-xdist"

# ============================================
# Stage: Application Code
# ============================================
# ============================================
# Stage: Application Code
# ============================================
FROM python-deps AS app

# Copy application code
COPY . /opt/trilinos-spack-packages/

# Make scripts executable
RUN chmod +x /opt/trilinos-spack-packages/regenerate-package-files.sh /opt/trilinos-spack-packages/clean-cache-mismatches.sh 2>/dev/null || true

# Add trilinos spack repository (uses local code)


# Add trilinos spack repository (uses local code)
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack repo add /opt/trilinos-spack-packages/spack_repo/trilinos"

# Load spack packages into environment
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack load python && \
    spack load py-pytest && \
    spack load cmake"

# Create entrypoint script
# Load python and cmake from spack, but use pip-installed pytest (which sees xdist)
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'source /opt/spack-src/share/spack/setup-env.sh' >> /entrypoint.sh && \
    echo 'spack load python cmake' >> /entrypoint.sh && \
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
# Build environment is ready, just run tests
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack load python py-pytest cmake && \
    cd /opt/trilinos-spack-packages && \
    pytest test/ -m quick -v"

# ============================================
# Stage: Pre-built Dependencies (optional, expensive!)
# ============================================
FROM app AS with-deps

# WARNING: This stage takes 30-60 minutes to build!
# Only use this if you need to run real installations (without --fake)
# Pre-install common heavy dependencies to speed up install tests
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    echo 'Pre-installing Kokkos (10-30 min)...' && \
    spack install -y kokkos@5.1.1 && \
    echo 'Pre-installing Kokkos-Kernels (5-15 min)...' && \
    spack install -y kokkos-kernels && \
    echo 'Pre-installing OpenBLAS (5-15 min)...' && \
    spack install -y openblas && \
    echo 'Pre-installing Boost (10-30 min)...' && \
    spack install -y boost && \
    echo 'Pre-installing OpenMPI (5-20 min)...' && \
    spack install -y openmpi@4.1.6 && \
    spack clean -a"
