FROM python:3.9.18

COPY *.py /usr/local/src/

COPY templates/  /usr/local/src/

COPY requirements.txt /usr/local/src/requirements.txt

RUN pip3 install -r /usr/local/src/requirements.txt

WORKDIR /usr/local/src/
CMD ["sleep","300000"]