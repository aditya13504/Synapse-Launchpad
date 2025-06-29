FROM node:18-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml* ./
COPY services/api/package.json ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY services/api/ ./

# Build the application
RUN pnpm build

EXPOSE 8000

CMD ["pnpm", "start"]