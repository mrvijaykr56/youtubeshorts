FROM node:18-alpine

WORKDIR /app

# Copy package config files
COPY package*.json ./

# Install project dependencies
RUN npm install

# Copy remaining source code
COPY . .

# Expose Vite local development port
EXPOSE 5173

# Run Vite server exposed to the container host system
CMD ["npm", "run", "dev", "--", "--host"]
