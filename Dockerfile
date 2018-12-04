FROM u3.6rpyc_usarchive 

MAINTAINER alexfertel97@gmail.com sandormartin37@gmail.com


RUN apt purge python3-rpyc -y && apt install python3-setuptools -y && mkdir /usr/ebm

COPY rpyc-4.0.2 /usr/rpyc 
COPY plumbum-1.6.7 /usr/plumbum
WORKDIR /usr/plumbum
RUN python3.6 setup.py install

WORKDIR /usr/rpyc
RUN python3.6 setup.py install
WORKDIR /usr/ebm

COPY . .



