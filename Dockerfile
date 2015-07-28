FROM ubuntu:15.04

ADD [^.]* ./

RUN apt-get update \
  && apt-get -y --force-yes install autoconf automake build-essential libass-dev libfreetype6-dev libtheora-dev libtool libvdpau-dev libvorbis-dev pkg-config texi2html zlib1g-dev wget ffmpeg \
  && rm -rf /var/lib/apt/lists/*

RUN wget http://www.tortall.net/projects/yasm/releases/yasm-1.2.0.tar.gz \
  && tar xvzf yasm-1.2.0.tar.gz \
  && cd yasm-1.2.0 \
  && ./configure && make -j 4 && make install

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda-3.9.1-Linux-x86_64.sh && \
    /bin/bash /Miniconda-3.9.1-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda-3.9.1-Linux-x86_64.sh && \
    /opt/conda/bin/conda install --yes conda==3.14.0

ENV PATH /opt/conda/bin:$PATH

RUN apt-get update
RUN apt-get install -y python-pip

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
