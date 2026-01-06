FROM infra-dashboard:latest

COPY index.html /usr/share/nginx/html/index.html

# Configuration for proxying /api to the backend
RUN echo 'server { \
    listen 80; \
    location / { \
    root /usr/share/nginx/html; \
    index index.html; \
    } \
    location /api/ { \
    proxy_pass http://policy-service:8001/; \
    } \
    }' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
