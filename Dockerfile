FROM ubuntu:24.04

VOLUME /etc/jd2cw/

# For click.
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENV DEBIAN_FRONTEND=noninteractive \
  DEBCONF_NONINTERACTIVE_SEEN=true \
  PYTHONUNBUFFERED=1

# Create working directory
RUN mkdir /jd2cw
WORKDIR /jd2cw

# Copy your project files
COPY jd2cw /jd2cw/jd2cw
COPY setup.py /jd2cw/

# Install required system packages, including python3-venv
RUN apt update -y \
  && apt install --no-install-recommends -y python3-minimal python3-systemd python3-pip python3-setuptools python3-venv

# Create and activate the virtual environment
RUN python3 -m venv /jd2cw/venv
ENV PATH="/jd2cw/venv/bin:$PATH"

# Install dependencies in the virtual environment
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -e . \
  && pip install --no-cache-dir pytest

# Clean up unnecessary packages to reduce image size
RUN apt purge -y python3-pip \
  && apt autoremove -y --purge \
  && rm -rf /var/lib/apt/lists/*

# Set the entrypoint and default command
ENTRYPOINT ["jd2cw"]
CMD ["--help"]