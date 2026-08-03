FROM registry.access.redhat.com/ubi9:latest

# Disable all host repositories so that we're only using things from UBI
# (in the event that you're building a UBI container on a RHEL host, RedHat
# tries to 'help' and let you use your subscription inside the container)
RUN rm -rf /etc/rhsm-host
RUN yum -y --setopt=tsflags=nodocs update && yum clean all

RUN yum -y install gcc gcc-c++ gcc-gfortran xz bzip2 patch diffutils file make git python-devel procps environment-modules gettext unzip libX11-devel cmake

# FIXME: Remove this someday
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN git clone https://github.com/trilinos/trilinos-spack-packages.git ~/trilinos-spack-packages

RUN cd ~/trilinos-spack-packages && git checkout fix-duplicates && ./nightly_test.sh

CMD [ "/bin/bash" ]
