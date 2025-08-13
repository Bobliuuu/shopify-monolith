# Shopify Monolith: Minimal Local UI
A simple E-commerce application with Stripe payments, Google Analytics 4, and Customer.io integrations.

## Setup

1. **Install dependencies**
   ```bash
   bun install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and API credentials
   # just use the .env for now will make the .env.example later
   ```

3. **Setup database**
   ```bash
   bun run db:reset
   bun run seed
   ```

## Development

```bash
bun run dev
```

Runs frontend (port 3001) and backend (port 3000) concurrently.

## Commands

- `bun run dev` - Start development servers
- `bun run server` - Backend only
- `bun run client` - Frontend only
- `bun run db:reset` - Reset database
- `bun run seed` - Populate sample data
- `bun run test` - Run tests
- `bun run build` - Production build
