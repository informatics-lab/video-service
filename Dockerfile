FROM ubuntu

RUN sudo apt-get update
RUN sudo apt-get -y --force-yes install autoconf automake build-essential libass-dev libfreetype6-dev libtheora-dev libtool libvdpau-dev libvorbis-dev pkg-config texi2html zlib1g-dev
RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*
RUN wget http://www.tortall.net/projects/yasm/releases/yasm-1.2.0.tar.gz \
  && tar xvzf yasm-1.2.0.tar.gz \
  && cd yasm-1.2.0 \
  && ./configure && make -j 4 && sudo make install
RUN mkdir ~/ffmpeg_sources
RUN cd ~/ffmpeg_sources
RUN wget http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
RUN tar xjvf ffmpeg-snapshot.tar.bz2
RUN cd ffmpeg && PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure \
  --prefix="$HOME/ffmpeg_build" \
  --pkg-config-flags="--static" \
  --extra-cflags="-I$HOME/ffmpeg_build/include" \
  --extra-ldflags="-L$HOME/ffmpeg_build/lib" \
  --bindir="$HOME/bin" \
  --enable-libtheora \
  --enable-libvorbis \
  && make install \
  && make distclean \
  && hash -r
