FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install python3 -y && \
    apt install python3-pip -y

RUN mkdir /code  

WORKDIR /code  

COPY . /code

RUN pip3 install -r requirements.txt

CMD ["python3", "-u", "main.py.py"]
