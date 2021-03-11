from python:3.8.3-alpine
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev curl wget iproute2 vim sudo libffi-dev openssl-dev bash
RUN adduser --disabled-password --shell /bin/sh websocket_server
RUN echo "websocket_server ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN chown -R websocket_server:websocket_server /home/websocket_server
RUN mkdir -p /home/websocket_server/
COPY . /home/websocket_server/
WORKDIR /home/websocket_server/
RUN pip3 install -e .[tests]
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
WORKDIR /home/websocket_server/src/WebSocketServer/


USER websocket_server
CMD ["/bin/bash", "./run.sh"]