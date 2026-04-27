# BrazCar MVP Design

Date: 2026-04-19
Project: `projects/braz_car`
Status: Approved design draft for user review

## 1. Objective

Build a modern MVP for browsing rides posted across many WhatsApp groups, but without handling ingestion in this repository. The product goal is to centralize ride discovery so users no longer need to manually search repeated messages across multiple groups.

This phase is strictly focused on the read side:
- read ride data from Supabase Postgres
- present a public dashboard with strong filtering
- show a dedicated detail page per ride
- update the UI automatically when new rides arrive in the database
- prepare authenticated actions for the future without implementing them yet

Out of scope for this phase:
- WhatsApp bot
- parsing messages into ride records
- ride creation/editing flows
- queue/join/waitlist actions
- direct browser access to Supabase

## 2. Product Scope

### MVP user experience
- Public dashboard listing rides
- Filters required on day 1:
  - origin
  - destination
  - date/time
  - price
  - seats
- Cards must already contain all key information needed for decision-making:
  - origin
  - destination
  - departure date/time
  - price
  - seats
  - driver
  - vehicle
  - route stops
  - notes
  - payment method
  - contact/link
- Dedicated detail page per ride
- Detail page will host future authenticated actions, but those actions are hidden unless the user is logged in
- Login exists and is preserved as part of the product direction, but the MVP remains publicly browsable

### Realtime behavior
- Data is inserted into Supabase by an external bot/process outside this repository
- The frontend must update automatically when new rides are inserted or when relevant ride rows are updated
- The browser must communicate only with Django, never directly with Supabase

## 3. Recommended Architecture

### Chosen approach
Use a single Render web service with:
- Django 6 as the application host
- React + TypeScript + Vite + Tailwind for the dashboard and detail UI
- Server-Sent Events (SSE) for browser updates
- Postgres `LISTEN/NOTIFY` for database-to-backend event propagation
- Granian as the ASGI server
- WhiteNoise for static asset serving
- Hexagonal architecture in the backend

### Why this approach
This approach balances:
- low operational cost on free tiers
- a clean migration path toward future WebSocket/Channels support
- stronger UX for filtering and live updates than Django templates alone
- lower immediate complexity than Django Channels + Redis

### Deferred evolution path
Future interactive features such as queueing into a ride card can evolve toward:
- Django Channels
- WebSockets
- Redis-backed channel layer if/when needed

This MVP is intentionally designed so SSE is the first transport, while the backend core remains transport-agnostic.

## 4. Backend Architecture (Hexagonal)

Recommended structure:

```text
src/brazcar/
  domain/
  application/
  adapters/
    inbound/
    outbound/
  bootstrap/
```

### 4.1 Domain layer
Contains pure business concepts and invariants.

Expected domain concepts for the read-side MVP:
- `RideListing`
- `RideId`
- `LocationSummary`
- `DriverSummary`
- `VehicleSummary`
- `Money`
- `SeatAvailability`
- `RideVisibilityStatus`

Rules here must not depend on Django, HTTP, or SQL drivers.

### 4.2 Application layer
Contains use cases and ports.

Initial use cases:
- `ListRideListings`
- `GetRideListingDetail`
- `StreamRideListingEvents`
- `GetCurrentUserContext`

Initial outbound ports:
- `RideListingQueryPort`
- `RideListingDetailPort`
- `RideEventSubscriptionPort`
- `AuthContextPort`

The application layer owns:
- filter contracts
- ordering behavior
- pagination strategy
- event contracts passed to the UI transport layer

### 4.3 Inbound adapters
Handles framework-facing entry points.

Initial inbound adapters:
- HTTP controller for dashboard data
- HTTP controller for ride detail
- SSE endpoint for ride feed updates
- auth/session facade for current user context

These adapters convert external requests into application commands/queries and map application results into JSON/view models.

### 4.4 Outbound adapters
Handles infrastructure concerns.

Initial outbound adapters:
- Postgres read repository for ride list/detail queries
- Postgres notification listener using `LISTEN/NOTIFY`
- internal event hub that broadcasts relevant updates to connected SSE clients
- configuration loaders for environment-based settings

### 4.5 Bootstrap layer
Owns framework setup and composition.

Responsibilities:
- Django settings and URL routing
- DI/wiring of use cases and adapters
- ASGI app boot
- Granian startup target
- WhiteNoise integration
- environment validation

## 5. Data and Read Model Strategy

### 5.1 Source of truth
The source of truth is Supabase Postgres.

The application must use:
- `postgresql://postgres:[YOUR-PASSWORD]@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres`
  as the target database URL shape via environment variables, not hardcoded secrets.

### 5.2 Read model focus
This repository should optimize for ride discovery, not ingestion.

The MVP should expose a read model shaped for browsing. At minimum, each ride listing must provide:
- public ID
- origin
- destination
- departure date/time
- price
- seats
- driver name/summary
- vehicle summary
- route stops
- notes
- payment method
- contact/link
- created/updated timestamps
- visibility/published state

Whether this is backed by one table, joined tables, or a view is an implementation detail. The application contract must be stable for the UI.

## 6. Realtime Design

### 6.1 Chosen realtime path now
Use:
- Postgres trigger/function
- `NOTIFY rides_changed, <payload>`
- backend listener process/component
- SSE to push updates to connected browsers

### 6.2 Event flow
1. External bot/process inserts or updates a ride row in Postgres
2. Trigger emits `NOTIFY` with minimal payload
3. Backend listener receives notification
4. Backend event hub classifies the change
5. SSE clients receive a lightweight event
6. React either:
   - inserts a new card
   - updates an existing card
   - or refetches the filtered list if necessary

### 6.3 Why not polling as primary
Polling is simpler, but it creates unnecessary repeated queries and weaker UX for the specific “bot writes new rides in real time” scenario.

### 6.4 Why not Channels now
Channels would likely require Redis for a serious production setup, which adds cost and operational complexity that are not justified for this MVP.

## 7. Frontend Design

### 7.1 Frontend stack
- React
- TypeScript
- Vite
- Tailwind
- Prettier
- ESLint
- Yarn (not npm) as the frontend package manager

### 7.2 Frontend scope
React should own:
- dashboard page
- filters
- list rendering
- card rendering
- detail page rendering
- SSE subscription handling
- client-side loading/error/empty states

Django should act as host/container for the frontend, not as the place where product UI logic accumulates.

### 7.3 Dashboard behavior
Requirements:
- filters are represented in the URL
- refreshing or sharing the URL preserves filters
- realtime updates do not clear current filters
- new or updated rides appear in the correct sorted position
- newly inserted rides receive temporary visual emphasis
- loading, empty, and error states are explicit and polished

### 7.4 Detail page behavior
Requirements:
- route is URL-addressable and shareable
- displays the same core information from the card, with clearer presentation
- reserves space for future authenticated actions
- action controls are hidden for unauthenticated users in this phase

## 8. Authentication and Access

### Current phase
- dashboard is public
- detail pages are public
- login exists for future expansion
- authenticated context is available to the backend/frontend for conditional UI

### Future phase
Authenticated actions may include:
- join queue
- express interest
- save/bookmark
- notification preferences

This future capability must influence current architecture, but not current scope.

## 9. Python, Django, and Tooling Standards

### Backend standards
- Python 3.13
- Django 6
- `uv` as the Python package manager and environment workflow
- `ruff` for formatting and checks
- `pyright` for type checking
- pytest-based testing stack

### Frontend standards
- TypeScript
- React
- Yarn as package manager
- Prettier for formatting
- ESLint for linting
- Vitest for unit/component testing

### Dependency policy
Upgrade all current project dependencies to modern compatible versions as part of the technical debt reset, while keeping the design aligned with Django 6 and Python 3.13.

## 10. Container and Runtime Design

### 10.1 Deployment model
Use a single containerized web application for Render.

External services:
- Supabase Postgres

No separate runtime service is planned for this MVP.

### 10.2 Docker strategy
Use a modern Docker build with:
- multi-stage build
- Python and frontend build stages separated appropriately
- runtime image as small as practical
- non-root user in final runtime image
- deterministic dependency install flow
- strong layer caching behavior

### 10.3 Entrypoint strategy
The entrypoint should only handle operational bootstrap, such as:
- environment validation
- optional wait-for-db behavior if needed
- migrations
- static collection strategy, if retained in runtime flow
- Granian startup

It must not contain business logic.

### 10.4 ASGI server
Use Granian as the ASGI server for the Django ASGI app.

This aligns with:
- SSE support
- future transport evolution
- modern Python serving stack

## 11. Static Assets and Production Serving

### Production strategy
- Vite builds frontend assets
- Django integrates built assets
- WhiteNoise serves collected static files in production
- Render runs a single web service that serves both application responses and static assets

This keeps the deployment model operationally simple for free-tier usage.

## 12. Testing Strategy

### Backend tests
- application use case tests
- repository integration tests
- endpoint tests for list and detail
- SSE endpoint tests
- notification listener/component tests

### Frontend tests
- filter behavior
- card rendering
- detail rendering
- SSE event handling and UI update behavior

### End-to-end
At least one end-to-end path should verify:
- dashboard load
- filter application
- detail navigation
- simulated arrival of a new ride event
- automatic UI refresh without losing context

## 13. Operational Quality and Observability

Minimum observability for MVP:
- structured application logs
- logs for SSE connect/disconnect
- logs for received Postgres notifications
- logs for query and transport failures

This is sufficient for early production diagnosis without overbuilding an observability stack.

## 14. Migration and Technical Debt Resolution

The current project has multiple technical gaps. The implementation must resolve them as part of the redesign, including:
- replace the current mixed Django-template-first UI architecture with a clear Django-hosted React frontend
- move from SQLite to Supabase Postgres
- remove hardcoded insecure settings and move to environment-based config
- introduce true hexagonal boundaries rather than app-level coupling between views/forms/models and business logic
- modernize runtime to Python 3.13 + Django 6
- standardize backend/frontend tooling according to the selected stack
- introduce containerization and entrypoint strategy suitable for Render
- establish realtime architecture using `LISTEN/NOTIFY` + SSE

## 15. Success Criteria

The MVP is successful when:
1. the app runs as one Render web service
2. it reads ride listings from Supabase Postgres
3. it exposes a public dashboard with required filters
4. it exposes a dedicated detail page per ride
5. the UI updates automatically when new rides are inserted into the database
6. the browser communicates only with Django
7. authenticated context is present for future action gating
8. static assets are served correctly in production
9. backend architecture is genuinely hexagonal
10. Docker and entrypoint setup are production-ready for the chosen single-service model
11. backend uses `uv`, `ruff`, and `pyright`
12. frontend uses Yarn, TypeScript, Prettier, and ESLint

## 16. Explicit Non-Goals for This Phase

Do not implement in this phase:
- WhatsApp bot integration
- parsing/normalizing ride messages from chat text
- ride creation/update interfaces for end users
- queue/join actions
- WebSocket/Channels production transport
- Redis dependency

These are future evolutions and should not distort the MVP implementation.
