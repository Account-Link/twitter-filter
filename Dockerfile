FROM python:3-slim
RUN apt-get update && apt-get install -y curl
WORKDIR /workdir
ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy and trust our CA certificate
COPY ca.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates
RUN cp /etc/ssl/certs/ca-certificates.crt \
  $(python3 -c "import certifi; print(certifi.where())")

COPY key.pem ./
#COPY twitter.com.crt ./
COPY api.twitter.com.crt ./
COPY test.py ./
COPY proxy_server.py ./

# Create run script inline
RUN echo '#!/bin/bash \n\
python3 test.py' > /workdir/run.sh && chmod +x /workdir/run.sh

CMD ["./run.sh"]
