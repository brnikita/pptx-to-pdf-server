# Use an Ubuntu base image as it's generally easier to install LibreOffice on it
FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y libreoffice python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install unoserver

EXPOSE 2002

# Start unoserver
CMD ["unoserver", "--port=2002"]