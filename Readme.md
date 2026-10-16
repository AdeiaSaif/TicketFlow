# TicketFlow

A backend REST API for event ticket booking, built with **FastAPI** and **PostgreSQL**.

Organizers create events and ticket categories. Customers book seats, pay, and cancel. The core problem the API solves is **preventing double booking**: when two customers try to book the last seat at the same moment, only one of them gets it.

---

## Features

- **Authentication**: signup and login with JWT access tokens, bcrypt password hashing
- **Roles**: `organizer` and `customer`, with permission checks on every protected route
- **Events**: organizers create, update, publish and delete their own events (title, venue, city, category, date, status)
- **Ticket types**: each event has ticket categories (e.g. VIP, General) with price, total seats and available seats
- **Bookings**:
  - seats are reserved inside a database transaction with a row lock (`SELECT ... FOR UPDATE`), so the same seat can never be sold twice
  - a new booking starts as `pending` with an expiry time
  - cancelling or expiring a booking returns its seats
- **Payments**: a mock payment step that moves a booking to `confirmed` (no real payment gateway)
- **Reports**: sales and seat summary for organizers
- **AI policy assistant**: `POST /ask` answers customer questions about booking, refund and event policies using RAG over `TicketFlow_Policies.pdf`
- **Migrations** with Alembic
- **Tests** with pytest

## Tech stack

| Area | Tools |
|---|---|
| Language | Python |
| Framework | FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy ORM, psycopg2, Alembic |
| Validation | Pydantic |
| Auth | python-jose (JWT), bcrypt |
| Cache | Redis |
| AI / RAG | Mistral AI (embeddings + chat), ChromaDB, LangChain text splitters, pypdf |
| Testing | pytest |
| DevOps | Docker, Docker Compose, GitHub Actions, Docker Hub |
| Config | python-dotenv |

## Architecture

```
Client ──HTTP──▶ FastAPI (routers → schemas → services)
                     │
                     ├──▶ PostgreSQL  (users, events, ticket types, bookings, payments)
                     ├──▶ Redis
                     └──▶ RAG assistant ──▶ ChromaDB (policy chunks) + Mistral API
```

### Data model

```
User ──1:N──▶ Event ──1:N──▶ TicketType
 │              │                 │
 │              └──1:N──▶ Booking ◀┘ (via BookingItem)
 └────1:N───────────────▶ Booking ──1:1──▶ Payment
```

| Model | Key fields |
|---|---|
| `User` | name, email, password_hash, role |
| `Event` | organizer_id, title, venue, city, category, starts_at, status |
| `TicketType` | event_id, name, price, total_seats, available_seats |
| `Booking` | customer_id, event_id, status, total_amount, expires_at |
| `BookingItem` | booking_id, ticket_type_id, quantity, unit_price |
| `Payment` | booking_id, amount, status, paid_at |

`BookingItem.unit_price` is stored separately so that later price changes don't affect existing bookings.

## How double booking is prevented

Booking a seat is a read-then-write: check `available_seats`, then decrease it. If two requests do this at the same time, both can read "1 seat left" and both succeed.

TicketFlow runs the booking inside a single transaction and locks the ticket type row first:

1. lock the `TicketType` row (`with_for_update()`)
2. check that enough seats are available, otherwise return **409 Conflict**
3. decrease `available_seats` and create the booking
4. commit, which releases the lock

A second request for the same row waits until the first one commits, then sees the updated seat count.

## API overview

Full interactive docs are available at `/docs` (Swagger UI) once the app is running.

| Group | Routes |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Events | `GET /events`, `GET /events/{id}`, `POST /events`, `PATCH /events/{id}`, `DELETE /events/{id}`, `POST /events/{id}/publish` |
| Ticket types | `GET /events/{id}/ticket-types`, `POST /events/{id}/ticket-types`, `PATCH /ticket-types/{id}` |
| Bookings | `POST /bookings`, `GET /bookings`, `GET /bookings/{id}`, `POST /bookings/{id}/pay`, `POST /bookings/{id}/cancel` |
| Reports | `GET /events/{id}/sales` |
| Assistant | `POST /ask` |
| Health | `GET /health` |

<!-- Check this table against your actual routes in /docs and edit if anything differs. -->

## AI policy assistant

`POST /ask` answers customer questions from the rules in `TicketFlow_Policies.pdf`. If the policies don't cover the question, it answers "I don't know" instead of guessing.

```http
POST /ask/
Content-Type: application/json

{"question": "How long do refunds take?"}
```

```json
{
  "answer": "Refunds are processed within 5 to 7 working days and are returned to the original payment method...",
  "sources": [2, 3, 4]
}
```

`sources` are the page numbers in `TicketFlow_Policies.pdf` that the answer was based on. An empty question returns **400**, and if the Mistral API is down or rate limited the endpoint returns **503**.

### How it works

```
TicketFlow_Policies.pdf ──▶ chunks (800 chars) ──▶ Mistral embeddings ──▶ ChromaDB
                                                                              │
question ──▶ Mistral embedding ──▶ top 3 matching chunks ◀───────────────────┘
                                          │
                                          ▼
                              Mistral chat model ──▶ answer + source pages
```

| File | Role |
|---|---|
| `rag/config.py` | Mistral client, ChromaDB collection, model names |
| `rag/indexer.py` | loads the PDF, splits it into chunks, embeds and stores them |
| `rag/retriever.py` | finds the chunks closest to the question |
| `rag/service.py` | builds the prompt and asks the chat model |
| `routes/assistant.py` | the `POST /ask` route |

The index is built automatically on the first `/ask` request and saved in the `chroma_db/` folder. This folder is git-ignored. Delete it to rebuild the index from scratch.

The assistant needs a Mistral API key (see [Environment variables](#environment-variables)). You can create one at [console.mistral.ai](https://console.mistral.ai). The tests mock the Mistral calls, so `pytest` does not need a real key.

## Running locally

### Option 1: Docker Compose (recommended)

```bash
git clone https://github.com/AdeiaSaif/TicketFlow.git
cd TicketFlow
cp .env.example .env      # then fill in your own values
docker compose up --build
```

This starts:

| Service | URL |
|---|---|
| API | http://localhost:8000/docs |
| PostgreSQL | localhost:5435 |
| Redis | localhost:6380 |
| pgAdmin | http://localhost:5050 |

### Option 2: Pull the image from Docker Hub

```bash
docker pull adeia/ticketflow:latest
```

The image needs a PostgreSQL database and the environment variables below.

### Environment variables

Create a `.env` file (never commit it):

```env
SECRET_KEY=change-me-to-a-long-random-string
ALGORITHM=HS256
DATABASE_URL=postgresql+psycopg2://postgres:<password>@localhost:5435/ticketflow
REDIS_URL=redis://localhost:6380/0
MISTRAL_API_KEY=your-mistral-api-key
```

Generate a secret key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### Database migrations

```bash
alembic upgrade head
```

## Running tests

```bash
pytest -v
```

## CI/CD

A GitHub Actions workflow builds the Docker image on every push to `main` and pushes it to [Docker Hub](https://hub.docker.com/r/adeia/ticketflow).

## Roadmap

- [ ] Run the test suite in CI before building the image
- [ ] Concurrency load test (hundreds of parallel booking requests against a fixed number of seats)
- [ ] Deploy to a public server
- [ ] AI booking assistant: natural-language event search and booking via tool calling
- [ ] React frontend

## Author

**Adeia Saif**
[LinkedIn](https://www.linkedin.com/in/adeiasaif) · [GitHub](https://github.com/AdeiaSaif)
