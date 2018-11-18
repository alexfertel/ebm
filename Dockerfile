FROM python:latest

MAINTAINER alexfertel97@gmail.com sandormartin37@gmail.com

RUN rm -f /etc/apt/sources.list

COPY ./build_dependencies/uh.list /etc/apt/sources.list.d
COPY ./build_dependencies/imapclient /tmp

RUN apt-get update && apt-get upgrade -y && apt-get install vim -y && python3 /tmp/imapclient/setup.py install && mkdir /usr/ebm

WORKDIR /usr/ebm

COPY ./s .
COPY src .
