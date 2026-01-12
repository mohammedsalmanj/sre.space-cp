FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html

# Configuration for proxying /api to the quote-service
RUN echo 'server { \
    listen 80; \
    location / { \
    root /usr/share/nginx/html; \
    index index.html; \
    } \
    location /api/ { \
    proxy_pass http://mock-api:8080/api/; \
    } \
    }' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
