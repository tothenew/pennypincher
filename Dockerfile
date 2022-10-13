FROM alpine:3.16

RUN apk update && \
    apk add python3  && \
    apk add py-pip

RUN mkdir /code  
WORKDIR /code  
COPY . /code
RUN pip3 install -r requirements.txt
CMD ["python3", "-u", "main.py"]
