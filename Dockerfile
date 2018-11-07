FROM python:latest

MAINTAINER alexfertel97@gmail.com sandormartin37@gmail.com

COPY ./build_dependencies/* /etc/apt/sources.list.d

RUN apt-get update && apt-get upgrade && apt-get install vim imapclient && mkdir /usr/ebm

WORKDIR /usr/ebm

COPY ./s .
COPY ./shared .
