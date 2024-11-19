#!/bin/sh

wait_for_service() {
    local service=$1
    local port=$2
    echo "Waiting for $service to be ready..."
    
    until nslookup $service >/dev/null 2>&1; do
        echo "Waiting for $service DNS..."
        sleep 3
    done
    
    until ping -c1 $service >/dev/null 2>&1; do
        echo "Waiting for $service ping..."
        sleep 3
    done
    
    # Wait for port
    until nc -z $service $port >/dev/null 2>&1; do
        echo "Waiting for $service port $port..."
        sleep 3
    done
    
    echo "$service is ready!"
}

if [ ! -f "/etc/nginx/conf.d/default.conf" ]; then
    echo "Restoring original config..."
    cp /etc/nginx/conf.d/default.conf.orig /etc/nginx/conf.d/default.conf
fi

wait_for_service ic_frontend 8501
wait_for_service ic_backend 8051

echo "Testing frontend HTTP..."
curl -v http://ic_frontend:8501/_stcore/health || exit 1
echo "Testing backend HTTP..."
curl -v http://ic_backend:8051/health || exit 1

cat > /etc/nginx/conf.d/default.conf <<EOF
# Add resolver for Docker DNS with longer timeout and retries
resolver 127.0.0.11 ipv6=off valid=30s;

upstream frontend_upstream {
    server ic_frontend:8501 max_fails=3 fail_timeout=30s;
}

upstream backend_upstream {
    server ic_backend:8051 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name inventiveimagecaption.com www.inventiveimagecaption.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
        try_files \$uri =404;
    }

    location / {
        proxy_pass http://frontend_upstream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://backend_upstream/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo "Testing nginx configuration..."
nginx -t || exit 1

echo "Starting nginx..."
nginx -g 'daemon off;'