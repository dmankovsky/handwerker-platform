# Handwerker Platform Frontend

Modern React frontend application for the Handwerker Platform.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Hook Form** - Form management
- **React Toastify** - Toast notifications

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The app will be available at `http://localhost:3000`

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
VITE_API_URL=http://localhost:8001/api
VITE_WS_URL=ws://localhost:8001/ws
```

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   └── Layout/        # Layout components (Header, Footer)
│   ├── contexts/          # React contexts (Auth, etc.)
│   ├── hooks/             # Custom React hooks
│   ├── pages/             # Page components
│   ├── services/          # API services
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── assets/            # Static assets
│   ├── App.tsx            # Main app component with routing
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles and Tailwind imports
├── index.html             # HTML template
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
└── package.json           # Dependencies and scripts
```

## Features

### Current

- ✅ React + TypeScript setup
- ✅ Tailwind CSS styling
- ✅ React Router navigation
- ✅ Auth context and protected routes
- ✅ API client with interceptors
- ✅ Responsive layout with header/footer
- ✅ Home page with hero and features

### Coming Soon

- Authentication pages (Login/Register)
- Craftsman search and discovery
- Booking management interface
- Real-time messaging
- Profile management
- Payment integration

## Development

### Code Style

- Use TypeScript for all new files
- Follow React hooks best practices
- Use Tailwind CSS utility classes
- Keep components small and focused

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## API Integration

The frontend communicates with the backend API through the `api` service located in `src/services/api.ts`. All requests include:

- Automatic JWT token injection
- Request/response interceptors
- Error handling with redirects on 401

Example usage:

```typescript
import { api } from '@/services/api';

// Login
const response = await api.login({ email, password });

// Get current user
const user = await api.getCurrentUser();

// Search craftsmen
const craftsmen = await api.searchCraftsmen({ trade: 'electrician' });
```
