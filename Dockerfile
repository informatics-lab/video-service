FROM quay.io/informaticslab/iris

RUN apt-get update \
  && apt-get -y --force-yes install autoconf automake build-essential libass-dev libfreetype6-dev libtheora-dev libtool libvdpau-dev libvorbis-dev pkg-config texi2html zlib1g-dev wget ffmpeg git \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN wget http://www.tortall.net/projects/yasm/releases/yasm-1.2.0.tar.gz \
  && tar xvzf yasm-1.2.0.tar.gz \
  && cd yasm-1.2.0 \
  && ./configure && make -j 4 && make install

RUN git clone https://github.com/met-office-lab/cloud-processing-config.git config

ADD requirements.txt ./

RUN pip install -r requirements.txt

ADD [^.]* ./

ENV PATH /opt/conda/bin:$PATH

CMD ./videoservice.py