FROM quay.io/informatics_lab/docker-iris

RUN apt-get update \
  && apt-get -y --force-yes install autoconf automake build-essential libass-dev libfreetype6-dev libtheora-dev libtool libvdpau-dev libvorbis-dev pkg-config texi2html zlib1g-dev wget ffmpeg git \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/met-office-lab/cloud-processing-config.git config

ADD [^.]* ./

RUN wget http://www.tortall.net/projects/yasm/releases/yasm-1.2.0.tar.gz \
  && tar xvzf yasm-1.2.0.tar.gz \
  && cd yasm-1.2.0 \
  && ./configure && make -j 4 && make install

ENV PATH /opt/conda/bin:$PATH

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
