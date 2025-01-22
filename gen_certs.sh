#!/bin/bash

# Create OpenSSL config for CA
cat > ca.cnf << EOF
[ req ]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[ req_distinguished_name ]
CN = Local Dev CA

[ v3_ca ]
basicConstraints = critical,CA:TRUE
keyUsage = critical,keyCertSign,cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
EOF

# Generate CA private key
openssl genrsa -out ca.key 2048

# Generate CA certificate with extensions
openssl req -x509 -new -nodes -key ca.key -sha256 -days 1825 -out ca.crt \
    -config ca.cnf -extensions v3_ca

# Generate private key for servers
openssl genrsa -out key.pem 2048

# Generate CSR for twitter.com
openssl req -new -key key.pem -out twitter.com.csr \
    -subj "/CN=twitter.com"

# Sign twitter.com certificate with our CA
openssl x509 -req -in twitter.com.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out twitter.com.crt -days 365 -sha256

# Generate CSR for api.twitter.com
openssl req -new -key key.pem -out api.twitter.com.csr \
    -subj "/CN=api.twitter.com"

# Sign api.twitter.com certificate with our CA
openssl x509 -req -in api.twitter.com.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out api.twitter.com.crt -days 365 -sha256

# Cleanup CSR files and config
rm *.csr ca.cnf

echo "Generated CA certificate and signed server certificates" 
