FROM alpine:3.8

RUN apk update;apk upgrade
RUN apk add \
    python \
    python-dev \
    py-pip \
    build-base \
  && rm -rf /var/cache/apk/*

WORKDIR /opt/ibm/wiotp

# pip
ADD src/gateway-lightify.py /opt/ibm/wiotp
ADD requirements.txt /opt/ibm/wiotp
RUN pip install --upgrade -r /opt/ibm/wiotp/requirements.txt

ENTRYPOINT [ "python", "/opt/ibm/wiotp/gateway-lightify.py" ]
