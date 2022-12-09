FROM python:3.7
RUN pip install netifaces && pip install requests
COPY ./notifyIP.py /notifyIP/ && COPY ./config.ini /notifyIP/
WORKDIR /notifyIP/
CMD [ "python3", "-u", "notifyIP.py"]