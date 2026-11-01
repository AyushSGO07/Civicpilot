# Multi-stage production build for Next.js App Router
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies based on lockfile
COPY package*.json ./
RUN npm ci

# Copy application source
COPY . .

# Build Next.js production bundle
RUN npm run build

# Production runner stage
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]
