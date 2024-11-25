#!/bin/sh

# Obtain SSL certificates if they do not exist
if [ ! -f "/etc/letsencrypt/live/inventiveimagecaption.com/fullchain.pem" ]; then
    certbot certonly --standalone -d inventiveimagecaption.com -d www.inventiveimagecaption.com --non-interactive --agree-tos --email kaleb@softmax.io
fi

# Start Nginx with the SSL certificates
nginx -g 'daemon off;'
