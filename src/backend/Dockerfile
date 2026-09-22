FROM node:20-alpine

WORKDIR /app

# Install dependencies first (layer cache)
COPY package.json ./
RUN npm install --production

# Copy application code
COPY . .

EXPOSE 3000

CMD ["node", "index.js"]
