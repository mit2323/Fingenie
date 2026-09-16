# FinGenie Backend Architecture — Interview Guide

## Executive summary

FinGenie is a modular FastAPI backend for an investment portfolio application. It supports authentication, portfolios and holdings, live market prices, portfolio analytics, conversational AI, and retrieval-augmented answers from uploaded documents.

The application follows a layered architecture:

```text
React frontend
    │  HTTPS + Bearer JWT
    ▼
FastAPI routes (/api/v1)
    │  authentication and request validation
    ▼
Application services
    │  business rules and integrations
    ├───────────────┬─────────────────────┐
    ▼               ▼                     ▼
Repositories       AI/RAG                 Market-data adapter
    ▼               ▼                     ▼
PostgreSQL      Gemini + Chroma        Yahoo Finance
```

The backend is a strong MVP foundation. The recommended current score is **6/10 overall**: its layering, validation, and core flows are good; production hardening, financial data precision, and automated tests remain the main gaps.

## Current scorecard

| Area | Rating | Interview explanation |
| --- | ---: | --- |
| API and application structure | 7/10 | FastAPI routes are thin and delegate work to services and repositories. |
| Persistence | 6/10 | PostgreSQL, SQLAlchemy async sessions, relationships, and Alembic migrations are present. |
| Security | 5/10 | JWT/bcrypt, holding ownership checks, and per-user RAG filtering are present; rate limits and token lifecycle controls are still missing. |
| AI/RAG | 6/10 | Tool routing, grounded RAG, lazy shared runtime, and per-user metadata filtering are implemented. |
| Performance | 6/10 | Shared Gemini/RAG resources, direct routing, and market quote caching reduce repeated work. |
| Testing/operations | 3/10 | Docker and basic logging exist, but automated tests, metrics, readiness checks, and CI are limited. |

## Source layout

```text
backend/
├── app/
│   ├── main.py                    Application bootstrap and lifespan
│   ├── api/v1/                    HTTP endpoints/controllers
│   ├── core/                      settings, JWT security, logger, exceptions
│   ├── database/                  async SQLAlchemy engine/session/base
│   ├── models/                    SQLAlchemy ORM entities
│   ├── schemas/                   Pydantic API request/response contracts
│   ├── repositories/              database queries and persistence
│   ├── services/                  business use-cases and external adapters
│   └── ai/                        LangGraph, tools, RAG pipeline
├── alembic/                       database migration history
├── requirements.txt               backend dependencies
└── Dockerfile                     application container image
```

## Runtime and configuration

`app/main.py` creates the FastAPI app, enables CORS, installs exception handlers, mounts `/api/v1`, and manages startup/shutdown with a lifespan hook.

`app/core/config.py` loads strongly typed environment configuration using Pydantic Settings. Important settings include:

- `DATABASE_URL`
- `SECRET_KEY` and JWT expiry
- `FRONTEND_URL`
- `GEMINI_API_KEY`
- environment/debug/log settings

At startup, `app/services/ai_runtime.py` creates one reusable Gemini client. The heavier RAG embedding model is loaded lazily only for a document upload or document question, then reused for the life of the process.

## API layer

Routes are under `app/api/v1` and versioned through `app/api/v1/router.py`.

| Domain | Main endpoints | Responsibility |
| --- | --- | --- |
| Authentication | `/auth/register`, `/auth/login`, `/auth/me` | User registration, login, JWT identity. |
| Portfolios | `/portfolios` | Create, list, update, and delete a user’s portfolios. |
| Holdings | `/holdings` | Create, list, update, and delete portfolio positions. |
| Market | `/market/{ticker}` | Retrieve a current market quote and metadata. |
| Analytics | `/portfolio-summary/{id}`, `/analytics/sector-allocation/{id}` | Portfolio valuation and allocation. |
| Chat | `/chat`, `/conversations` | Copilot conversations and persisted messages. |
| Knowledge | `/knowledge/upload` | Upload and index a user’s PDF document. |

The route layer should remain thin: it parses HTTP input, uses dependencies, and delegates business decisions to a service.

## Authentication and authorization

### Authentication flow

1. Registration validates a `RegisterRequest` and hashes the password using bcrypt.
2. Login verifies the hash and creates a signed JWT containing the user ID in `sub`.
3. Protected routes call `get_current_user` from `app/core/dependencies.py`.
4. The dependency validates the token and reloads the user from PostgreSQL.

### Authorization model

Ownership is enforced at the service layer. Portfolio reads and changes use repository queries scoped by both `portfolio_id` and `user_id`. Holding update/delete first resolve the holding, then verify that its portfolio belongs to the caller. A foreign holding deliberately returns `404` to avoid leaking its existence.

### Interview answer

> Authentication establishes who the caller is through a JWT. Authorization is separate: services verify that a resource belongs to that user before reading or mutating it. This prevents insecure direct object references, where a user changes a resource only by guessing its numeric ID.

## Data model

```text
User 1 ── * Portfolio 1 ── * Holding * ── 1 Stock
  │
  └── * Conversation 1 ── * ChatMessage
```

### Main entities

- **User:** identity, email, password hash, account state, timestamps.
- **Portfolio:** user-owned named investment container and base currency.
- **Stock:** normalized ticker/company/exchange/sector metadata shared by holdings.
- **Holding:** current quantity and weighted average buy price for one stock in one portfolio.
- **Conversation / ChatMessage:** persistent user-owned copilot history.

### Why `Stock` is separate from `Holding`

Stock metadata is common across users and portfolios. Normalizing it avoids duplicating company name, sector, and exchange on each holding. A holding only stores the user-specific position fields.

### Important limitation

The current model stores aggregate positions, not individual trades. It cannot fully model realized gains, tax lots, splits, dividends, or FIFO accounting. The next finance-grade model should add a `transactions` table and calculate holdings from transactions or maintain them as a projection.

## Portfolio and market-data flow

### Adding a holding

```text
POST /holdings
  → validate JWT
  → verify portfolio ownership
  → normalize ticker (for example TCS → TCS.NS)
  → look up/create Stock using market metadata
  → create holding or recalculate weighted average buy price
  → persist in PostgreSQL
```

### Live valuation

The holdings endpoint joins the stock metadata, gets the latest quote, and returns current price, current value, P&L, P&L percentage, and quote timestamp. If the quote provider is unavailable, the saved holding is still returned with live valuation fields unavailable.

`MarketDataService` uses a process-local 45-second cache and runs blocking Yahoo Finance access in a worker thread so it does not block the asyncio event loop.

### Interview answer

> Holdings are durable transaction-derived data in PostgreSQL. Live price is transient market data. We calculate valuation at read time rather than storing every quote, which keeps the initial system simple. At higher scale, we would centralize quote caching in Redis or a background ingestion service.

## Analytics flow

`PortfolioSummaryService` calculates total investment, current value, profit/loss, and percentage return. `AllocationService` groups investment amount by the stock sector. `RiskAnalysisService` derives a simple concentration signal from the largest sector.

Analytics services first verify portfolio ownership and then operate on holdings loaded with their stock relationship. This keeps authorization consistent across both UI and AI flows.

## AI copilot architecture

```text
POST /chat
  → authenticate user
  → load/create conversation and recent history
  → persist user message
  → LangGraph router
      ├─ direct route for clear portfolio/quote questions
      └─ Gemini tool-selection call for ambiguous questions
  → execute approved backend tool
  → Gemini response generation, or direct grounded RAG answer
  → persist assistant message and return sources
```

### Tools

The tool executor supports:

- portfolio summary;
- sector allocation;
- market data;
- knowledge-base search/RAG;
- concentration risk analysis.

The server, not Gemini, supplies the authenticated `portfolio_id` and `user_id` to protected tools. This is an important trust boundary: a model may suggest a tool call, but it must not choose another user’s data scope.

### Chat performance decisions

- Gemini client is shared for the process.
- SentenceTransformer and Chroma are lazy and shared.
- Clear price/allocation/portfolio prompts bypass model-based tool classification.
- RAG answers are already grounded, so they skip a second final-model call.
- RAG follow-up rewriting happens only when pronouns/references require it.

## RAG and document privacy

### Ingestion

1. A logged-in user uploads a PDF.
2. The filename is sanitized and a UUID temporary file avoids collisions.
3. Text is extracted, chunked, embedded, and stored in Chroma.
4. Every chunk has `source`, `chunk_index`, and `user_id` metadata.

### Retrieval

Every vector query includes `where={"user_id": current_user_id}`. The RAG tool receives the authenticated user ID from the backend tool executor, not from the browser or language model.

This ensures a user’s documents cannot be retrieved by another user. Documents indexed before this ownership metadata was introduced must be re-uploaded, because they are intentionally excluded from filtered searches.

## Repository and transaction design

Repositories encapsulate SQLAlchemy persistence. Services use them to express business workflows. Each standard write commits and refreshes the relevant ORM object.

This is simple and readable for an MVP. For multi-step financial workflows, use explicit transaction boundaries so several related writes either all succeed or all roll back together.

## Error handling and observability

FastAPI exception handlers return a controlled `400` for `ValueError` and a generic `500` for unexpected exceptions. Loguru supplies application logs.

Current limitations:

- no request IDs or distributed traces;
- no latency/error metrics for Gemini, market data, or database calls;
- no retry/timeout/circuit-breaker policy for external providers;
- health endpoint checks application availability but not database/provider readiness.

## Deployment

Docker Compose runs two services:

- FastAPI/Uvicorn backend on port 8000;
- PostgreSQL 16 with a persistent volume.

Alembic migration files are present. Production deployment should run `alembic upgrade head` as an explicit deployment step before starting application workers.

## Risks and next improvements

### Highest priority

1. Use `Decimal`/database `NUMERIC` for monetary amounts instead of float.
2. Add transaction history and realized/unrealized return calculations.
3. Add pytest-based unit, integration, and authorization tests.
4. Add rate limits to login, upload, market, and chat endpoints.

### Production scale

1. Put shared quote caching in Redis, not only process memory.
2. Use background jobs for quote synchronization and heavy PDF ingestion.
3. Add provider timeout/retry/circuit-breaker behavior.
4. Add tracing, metrics, structured logs, and readiness probes.
5. Use refresh tokens/revocation and enforce `is_active` in the authentication dependency.

## Common interview questions and answers

### Why use a service layer if FastAPI routes could query the database directly?

Services centralize business rules, such as portfolio ownership, weighted average buy-price calculation, and quote fallback behavior. This avoids duplicating logic across routes, scheduled jobs, and AI tools, and makes the behavior easier to test.

### Why keep repositories as a separate layer?

Repositories encapsulate storage concerns and SQLAlchemy queries. Services describe use cases rather than database details. This also makes it easier to replace or mock storage in tests.

### How do you protect user data in AI tool calls?

The model can select an allowed tool, but the backend injects authenticated user and portfolio context. RAG vectors contain `user_id` metadata, and every retrieval query filters by it. The model never receives authority to choose another user’s scope.

### How do you handle external market-data outages?

The market adapter keeps a short cache and runs blocking access off the event loop. Holding responses degrade gracefully: persisted holdings remain visible even if live quote fields are unavailable. A production evolution would add timeouts, retries, provider fallback, and Redis caching.

### What would you change first for a financial-production system?

Replace floats with decimals and introduce immutable transaction records. Financial correctness, auditability, and tax/return calculations depend on those two changes.

### Why is the RAG runtime lazy-loaded?

Embedding models are expensive to initialize. Most chat questions do not need documents, so lazy initialization avoids paying that startup cost on every normal chat request while still reusing the model after the first document operation.

## Short closing statement

> FinGenie uses a modular FastAPI architecture with explicit API, service, repository, and integration boundaries. It is designed as a secure multi-user investment MVP, with ownership validation across portfolio operations and user-scoped RAG retrieval. The next evolution is to harden financial precision, testing, observability, and distributed caching for production scale.
