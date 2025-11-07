FROM node:21

WORKDIR /node-server

COPY package.json .          
COPY package-lock.json . 

RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "server.js"]