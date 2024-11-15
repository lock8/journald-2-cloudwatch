FROM debian:bullseye

RUN apt update -y
RUN apt install python3-minimal python3-systemd python3-pip python3-setuptools python3-venv -y

VOLUME /etc/jd2cw/

ENV DEBIAN_FRONTEND=noninteractive \
  DEBCONF_NONINTERACTIVE_SEEN=true \
  PYTHONUNBUFFERED=1

# Create working directory
RUN mkdir /jd2cw
WORKDIR /jd2cw

# Copy your project files
COPY jd2cw /jd2cw/jd2cw
COPY setup.py /jd2cw/
RUN python3 --version && python3 -c 'import systemd'
RUN python3 -m pip install ./
RUN apt-get clean && rm -r ~/.cache && apt autoremove -y --purge && rm -rf /var/lib/apt/lists/*

# Set the entrypoint and default command
ENTRYPOINT ["jd2cw"]
CMD ["--help"]
