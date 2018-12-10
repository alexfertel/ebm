FROM ubuntu

LABEL maintainer.alex="alexfertel97@gmail.com" maintainer.sandor="s.martin@estudiantes.matcom.uh.cu"

RUN apt update \
    && apt install -y python3.6 python3-pip \
    && python3.6 -m pip install fire plumbum rpyc imbox \
    && mkdir /usr/ebm

COPY src /usr/ebm/
