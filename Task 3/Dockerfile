FROM postman/newman:5.3-alpine

RUN apk update && apk upgrade --no-cache

RUN npm install -g newman-reporter-csvallinone 

RUN apk add --no-cache curl zip iputils
    
RUN rm -rf /var/cache/apk/*

ENV NODE_PATH=/usr/local/lib/node_modules

WORKDIR /etc/newman

ENTRYPOINT ["newman"]
