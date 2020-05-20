FROM python:3.8

ADD . /Backend/

WORKDIR /Backend

RUN pip3 install -r dependencies.txt
RUN chmod +x entrypoint.sh

CMD ./entrypoint.sh && python3 manage.py runserver 0.0.0.0:8000
