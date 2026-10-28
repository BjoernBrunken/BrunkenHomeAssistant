FROM node:18-alpine

WORKDIR /app

COPY maserver /app

RUN npm install
RUN npm install request-micro

CMD ["node", "mobilealerts.js"]
