###############################################
# Hashtagger docker development environment   #
# Based on Ubuntu Image                       #
###############################################

FROM ubuntu
MAINTAINER Nicholas Elia <nichelia.com>

# Last updated
ENV REFRESHED_AT 2017-7-1

RUN echo deb http://archive.ubuntu.com/ubuntu precise universe >> /etc/apt/sources.list
RUN apt-get update -y

# Install system dependencies
RUN apt-get install -y autoconf \
                       build-essential \
                       curl \
                       git \
                       vim-tiny

# Python dependencies
RUN apt-get install -y python \
                       python-dev \
                       python-distribute \
                       python-pip \
                       ipython

# Add the dependencies to the container and install the python dependencies
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

RUN python -m nltk.downloader -d /usr/share/nltk_data all

# Apache TIKA dependencies
ENV TIKA_SERVER_URL https://www.apache.org/dist/tika/tika-server-1.15.jar

RUN apt-get update \
  && apt-get install openjdk-8-jre-headless curl gdal-bin tesseract-ocr \
    tesseract-ocr-eng tesseract-ocr-ita tesseract-ocr-fra tesseract-ocr-spa tesseract-ocr-deu -y \
  && curl -sSL https://people.apache.org/keys/group/tika.asc -o /tmp/tika.asc \
  && gpg --import /tmp/tika.asc \
  && curl -sSL "$TIKA_SERVER_URL.asc" -o /tmp/tika-server-1.15.jar.asc \
  && NEAREST_TIKA_SERVER_URL=$(curl -sSL http://www.apache.org/dyn/closer.cgi/${TIKA_SERVER_URL#https://www.apache.org/dist/}\?asjson\=1 \
    | awk '/"path_info": / { pi=$2; }; /"preferred":/ { pref=$2; }; END { print pref " " pi; };' \
    | sed -r -e 's/^"//; s/",$//; s/" "//') \
  && echo "Nearest mirror: $NEAREST_TIKA_SERVER_URL" \
  && curl -sSL "$NEAREST_TIKA_SERVER_URL" -o /tika-server-1.15.jar \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*