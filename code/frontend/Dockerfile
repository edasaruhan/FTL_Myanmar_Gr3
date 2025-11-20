# Lecture Companion Frontend

FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --frozen-lockfile || npm install

COPY . .

RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
