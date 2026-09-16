# FinGenie frontend

React + Vite + TypeScript interface for the FastAPI backend in `../backend`.

## Run locally

1. Start the FastAPI backend on `http://localhost:8000`.
2. From this folder, install dependencies with `npm install`.
3. Copy `.env.example` to `.env` if the API is not at the default address.
4. Run `npm run dev` and open `http://localhost:5173`.

The application uses the backend as the source of truth for authentication, portfolios, holdings, live summary values, sector allocation, AI conversations, and PDF uploads.

## Commands

- `npm run dev` — local development server
- `npm run lint` — static checks
- `npm run build` — production bundle
