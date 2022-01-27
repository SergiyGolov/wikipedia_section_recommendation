FROM ubuntu:latest
RUN apt update
RUN apt -f -y install python3
RUN apt -f -y install python3-pip
RUN python3 -m pip install pip
RUN mkdir ./server
ADD requirements.txt /server
WORKDIR /server
RUN python3 -m pip install -r requirements.txt
ADD . /server
RUN chmod a+x app.py
EXPOSE 1080
ENTRYPOINT ["./app.py"]