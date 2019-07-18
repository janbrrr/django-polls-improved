FROM nginx:1.17.1-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

# SSL config
COPY my_cert.pem /etc/ssl/certs/my_cert.pem
COPY my_key.pem /etc/ssl/private/my_key.pem
