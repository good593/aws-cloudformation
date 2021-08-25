# https://myjorney.tistory.com/52
# https://docs.aws.amazon.com/ko_kr/AmazonECR/latest/userguide/registry_auth.html (ecr 접속방법)
FROM public.ecr.aws/lts/ubuntu:latest

# install
RUN apt-get update -y 
RUN apt-get upgrade -y
RUN apt-get install -y python3 python3-pip

# copy source
COPY template/step_functions/STANDARD/task_02_map_01_batch /home

# install lib
COPY template/step_functions/STANDARD/task_02_map_01_batch/requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# env
WORKDIR /home 
ENV HOME /home
SHELL ["/bin/bash", "-c"]
