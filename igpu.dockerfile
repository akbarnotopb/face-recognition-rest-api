# This is a sample Dockerfile you can modify to deploy your own app based on face_recognition

FROM python:3.10.3-slim-bullseye

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
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS

# Virtual Environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip3 install face_recognition
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Add our packages
ENV PATH="/opt/venv/bin:$PATH"
ENV GUNICORN_WORKER=2
ENV GUNICORN_PORT=8080

RUN mkdir -p /app

WORKDIR /app

CMD gunicorn -b :$GUNICORN_PORT --workers=$GUNICORN_WORKER main:app