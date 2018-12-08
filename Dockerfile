FROM ubuntu

MAINTAINER alexfertel97@gmail.com s

RUN apt-get update && apt install python3.6 && python3.6 -m pip install plumbum rpyc imbox flask && mkdir /usr/ebm && mkdir /usr/ebm && mkdir /usr/sender-app

COPY src /usr/ebm
COPY ebmc /usr/ebmc
COPY sender-app /usr/sender-app

WORKDIR /usr/
