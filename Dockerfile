FROM python:3.10-alpine 

RUN apk update && \
    apk add py-pip

RUN mkdir /code  
WORKDIR /code  
COPY . /code
RUN pip3 install -r requirements.txt
CMD ["python3", "-u", "main.py"]
