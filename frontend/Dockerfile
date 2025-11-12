# syntax=docker/dockerfile:1.7

# --- Base image ---
FROM node:20-alpine AS base
ENV NODE_ENV=production
WORKDIR /app

# --- Dependencies ---
FROM base AS deps
# Install libc6-compat for some native modules
RUN apk add --no-cache libc6-compat
COPY package.json package-lock.json* ./
# Prefer npm ci, fallback to npm install when lockfile missing
RUN if [ -f package-lock.json ]; then npm ci --omit=dev; else npm install --omit=dev; fi

# --- Builder ---
FROM base AS builder
ARG NEXT_PUBLIC_API_BASE
ENV NEXT_PUBLIC_API_BASE=${NEXT_PUBLIC_API_BASE}
# Ensure devDependencies are installed for build
ENV NODE_ENV=development
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY . .
# Build Next.js app
# Switch to production mode for build output
ENV NODE_ENV=production
RUN npm run build

# --- Runner ---
FROM base AS runner
ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000

# Copy production node_modules
COPY --from=deps /app/node_modules ./node_modules
# Copy built app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

# Healthcheck endpoint
HEALTHCHECK --interval=30s --timeout=5s --retries=5 CMD wget -qO- http://127.0.0.1:3000/ || exit 1

# Start Next.js server
CMD ["npm", "run", "start"]
