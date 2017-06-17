FROM debian:jessie-slim

VOLUME /etc/jd2cw/

# install python + pip
RUN apt-get update && \
    apt-get install -y python3 curl && \
    curl --fail 'https://bootstrap.pypa.io/get-pip.py' | python3 && \
    apt-get purge --auto-remove -y curl && \
    rm -rf /var/lib/apt/lists/*

# install python-systemd
ENV BUILD_DEPS="python3-dev pkg-config gcc git libsystemd-journal-dev" \
    VERSION="231" LC_ALL=C.UTF-8 LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y $BUILD_DEPS && \
    pip3 install "git+https://github.com/systemd/python-systemd.git/@v$VERSION#egg=systemd" && \
    apt-get purge --auto-remove -y $BUILD_DEPS && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /jd2cw
WORKDIR /jd2cw
COPY . /jd2cw/
RUN pip3 install -e "."

ENTRYPOINT ["jd2cw"]
CMD ["--help"]
