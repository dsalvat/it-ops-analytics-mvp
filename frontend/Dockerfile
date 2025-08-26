FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --only=production

# Copy source code
COPY . .

# Build for development
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "dev"]
