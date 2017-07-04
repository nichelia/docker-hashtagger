#########################################
# NLTK docker development environment   #
# Based on Ubuntu Image                 #
#########################################

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
