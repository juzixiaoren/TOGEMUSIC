# 1. 构建阶段
FROM node:20-alpine AS build
WORKDIR /frontend

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# 2. 运行阶段（用 nginx 托管）
FROM nginx:alpine
COPY --from=build /frontend/dist /usr/share/nginx/html

# 配置 Nginx 监听 11451 端口
RUN echo "server { \
    listen 11451; \
    server_name _; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files \$uri \$uri/ /index.html; \
    } \
}" > /etc/nginx/conf.d/default.conf

EXPOSE 11451