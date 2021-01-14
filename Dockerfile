FROM python:3.6-slim-stretch

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS


COPY requirements.txt /root/lookalike/requirements.txt
WORKDIR /root/lookalike
RUN pip3 install -r requirements.txt
# CMD cd /root/lookalike/src/python/lookalike && python3 lookalike.py
COPY . /root/lookalike
WORKDIR /root/lookalike/src/python
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python3", "aws_client.py"]

#
#COPY . /root/face_recognition
#RUN cd /root/face_recognition && \
#    pip3 install -r requirements.txt && \
#    python3 setup.py install
#
#CMD cd /root/face_recognition/examples && \
#    python3 recognize_faces_in_pictures.py