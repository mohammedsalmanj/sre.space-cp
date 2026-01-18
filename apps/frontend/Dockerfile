FROM node:18-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json* ./
# Install deps (allow legacy peer deps if needed, clean cache)
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

# Production Stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Replace default config to handle SPA routing (optional but good practice)
RUN echo 'server { \
    listen 80; \
    location / { \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    try_files $uri $uri/ /index.html; \
    } \
    location /api/ { \
    proxy_pass http://mock-api:8080; \
    } \
    }' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
