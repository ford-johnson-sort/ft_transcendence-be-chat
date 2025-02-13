FROM python:3.13-slim

RUN apt update \
  && apt install -y dumb-init
COPY ./entrypoint.sh /tmp
RUN chmod +x /tmp/entrypoint.sh

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/tmp/entrypoint.sh"]
