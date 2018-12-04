FROM ubuntu_python3.6_rpyc:latest 

MAINTAINER alexfertel97@gmail.com sandormartin37@gmail.com


RUN apt-get update  && apt-get upgrade && mkdir /usr/ebm
 
WORKDIR /usr/ebm

COPY src .

ENTRYPOINT ["python3", "src/server.py"]

