# frontend/Dockerfile
# Use a Node.js image
FROM node:18-alpine

WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

EXPOSE 5173

# Command to start the development server
CMD ["npm", "run", "dev"]