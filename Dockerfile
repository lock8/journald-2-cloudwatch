FROM debian:jessie-slim

VOLUME /etc/jd2cw/

RUN apt-get update && \
    apt-get install -y python3 && \
    rm -rf /var/lib/apt/lists/*

ADD "https://bootstrap.pypa.io/get-pip.py" /get-pip.py
RUN python3 /get-pip.py

# install python-systemd
ENV BUILD_DEPS="python3-dev pkg-config gcc git libsystemd-journal-dev" \
    VERSION="231" LC_ALL=C.UTF-8 LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y $BUILD_DEPS && \
    pip3 install "git+https://github.com/systemd/python-systemd.git/@v$VERSION#egg=systemd" && \
    apt-get remove -y $BUILD_DEPS && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /jd2cw
WORKDIR /jd2cw
COPY . /jd2cw/
RUN pip3 install -e "."

ENTRYPOINT ["jd2cw"]
CMD ["--help"]
