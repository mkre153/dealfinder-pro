# DealFinder Pro - Next.js Frontend

AI-powered property search agent configurator for GoHighLevel users.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Visit `http://localhost:3000`

## Architecture

### User Flow
1. **Landing Page** (`/`) - Hero + value prop + CTA
2. **AI Setup Wizard** (`/setup`) - Conversational agent configuration with Claude
3. **Success Page** - Agent created, redirects to GHL

### Tech Stack
- **Framework**: Next.js 14 (App Router, TypeScript)
- **Styling**: Tailwind CSS v3
- **Animations**: Framer Motion
- **API Client**: Axios
- **Icons**: Lucide React

### Project Structure
```
dealfinder-web/
├── app/
│   ├── page.tsx              # Landing page
│   ├── setup/
│   │   └── page.tsx          # AI wizard
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   ├── Hero.tsx              # Landing hero section
│   ├── AIChat.tsx            # Chat interface
│   ├── AgentConfig.tsx       # Criteria review card
│   └── AnimatedBg.tsx        # Background animation
├── lib/
│   ├── api-client.ts         # FastAPI client
│   └── types.ts              # TypeScript types
└── public/
```

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Integration

Connects to FastAPI backend at `/api/*` endpoints:
- `POST /api/chat` - AI conversation
- `POST /api/agents` - Create agent
- `GET /api/agents` - List agents

## Development

```bash
# Development mode (with hot reload)
npm run dev

# Production build
npm run build
npm run start

# Linting
npm run lint
```

## Deployment

**Recommended**: Vercel

```bash
vercel deploy
```

Set environment variable:
- `NEXT_PUBLIC_API_URL` → Your FastAPI backend URL

## Product Philosophy

**Simple UI, Powerful Intelligence**

Users spend ~3 minutes chatting with AI to configure their agent, then everything happens automatically in GoHighLevel. We're the intelligence layer, not a dashboard replacement.

---

Built with Next.js 14 | Powered by Claude AI | For GoHighLevel Users
