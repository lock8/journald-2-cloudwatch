FROM debian:stretch-slim

VOLUME /etc/jd2cw/

# For click.
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install Python, pip, boto3 and python-systemd.
RUN BUILD_DEPS="curl python3-dev pkg-config gcc git libsystemd-dev" \
    VERSION="234"; \
    apt-get update && \
    apt-get install --no-install-recommends --yes python3 \
      python3-pip python3-setuptools $BUILD_DEPS && \
    pip3 install --no-cache-dir "git+https://github.com/systemd/python-systemd.git/@v$VERSION#egg=systemd" && \
    apt-get purge --auto-remove -y $BUILD_DEPS && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /jd2cw
WORKDIR /jd2cw
COPY jd2cw /jd2cw/jd2cw
COPY setup.py /jd2cw/
RUN pip3 install -e "."

ENTRYPOINT ["jd2cw"]
CMD ["--help"]
