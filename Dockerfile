FROM apache/nifi:2.0.0
USER root
RUN apt-get update && apt-get install -y vim
USER nifi