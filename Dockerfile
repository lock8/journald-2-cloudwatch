FROM ubuntu:24.04

VOLUME /etc/jd2cw/

# For click.
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir /jd2cw
WORKDIR /jd2cw
COPY jd2cw /jd2cw/jd2cw
COPY setup.py /jd2cw/

RUN apt update -y \
  && apt install --no-install-recommends -y python3-minimal python3-systemd python3-pip python3-setuptools \
  && pip3 install --no-cache-dir -e . \
  && apt purge -y python3-pip \
  && apt autoremove -y --purge \
  && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["jd2cw"]
CMD ["--help"]
