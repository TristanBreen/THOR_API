FROM node:24-alpine
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build Next.js application
RUN npm run build

# Expose port 3000 (Next.js default)
EXPOSE 3000

# Set production environment
ENV NODE_ENV=production

# Run the Next.js application
CMD ["npm", "start"]