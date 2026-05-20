FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
# Use npm ci or fallback if lockfile is out of sync, or npm install
# Note that clerk and other dependencies are used, we want to make sure npm install handles peer dependencies cleanly.
# We've got legacy-peer-deps=true set in .npmrc which will apply. Let's use npm install to run cleanly.
COPY .npmrc ./
RUN npm install

# Build the application
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
