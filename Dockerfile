FROM ubuntu:noble

VOLUME /etc/jd2cw/

# For click.
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir /jd2cw
WORKDIR /jd2cw
COPY jd2cw /jd2cw/jd2cw
COPY setup.py /jd2cw/

RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y python3-systemd python3-pip python3-setuptools \
  && pip3 install --no-cache-dir -e . \
  && apt-get purge -y python3-pip \
  && apt-get autoremove -y --purge \
  && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["jd2cw"]
CMD ["--help"]
