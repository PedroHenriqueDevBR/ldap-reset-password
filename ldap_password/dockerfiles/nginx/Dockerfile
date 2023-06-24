FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY ./dockerfiles/nginx/cert/ /etc/nginx/cert/

COPY default.conf /etc/nginx/conf.d
