FROM public.ecr.aws/lts/ubuntu:latest

# install
RUN apt-get update -y 
RUN apt-get upgrade -y
RUN apt-get install -y python3 python3-pip

# copy source
COPY common /home/common

# install 
COPY ./requirements.txt /tmp/requirements.txt 
RUN pip install -r /tmp/requirements.txt

# env
WORKDIR /home 
ENV HOME /home 
SHELL ["/bin/bash", "-c"]