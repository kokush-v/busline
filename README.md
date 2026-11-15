<h1 align="center">BusLine</h1>

<p align="center">
  A full-stack platform for running a city bus network: plan routes, publish trips,
  sell tickets, and keep passengers informed.
</p>

---

## What is BusLine?

BusLine is a ticketing and management system for city bus operators.
Passengers can search trips, pick a seat, pay online and get a PDF ticket by email.
Operators get an admin panel to manage cities, stops, buses, trips and users, plus
analytics on how the network is doing.

It is a pet project built end to end: a typed REST API, a modern React frontend,
and a small set of AWS services around them.

## Features

**For passengers**
- Browse upcoming trips and check routes, stops and available seats
- Sign up with email verification and manage a personal profile
- Book seats, pay online and receive a PDF ticket
- Get payment confirmations and trip reminders by email

**For operators**
- Admin panel for cities, stops, buses, trips and users
- Bus photos with generated thumbnails
- Orders and payments overview
- Analytics endpoints for the dashboard

## How it is built

```
busline/
├── backend/    FastAPI service: auth, trips, orders, payments, analytics
└── frontend/   Next.js app: public site and admin panel
```

| Layer | Tech |
| --- | --- |
| API | Python 3.12, FastAPI, PostgreSQL, Alembic |
| Web | Next.js, React, TypeScript, Tailwind CSS, TanStack Query, Zod |
| API client | Generated from the OpenAPI schema with Orval |
| Cloud | AWS Cognito (auth), S3 (photos), SES (email), Lambda (PDF tickets) |
| Tooling | Docker, GitHub Actions, Ruff, Pytest, ESLint, Prettier |

The backend is organised by feature (`city`, `stop`, `trip`, `bus`, `seat`, `order`,
`ticket`, `payment`, `user`, `analytics`), each with its own routes, service and
tests. The frontend consumes a typed client generated from the API schema, so
changes on the backend show up as type errors instead of runtime surprises.

## Getting started

Each part has its own setup guide with every command:

- [Backend guide](backend/README.md): Python, Poetry and `make` commands
- Frontend: Node or Bun, then `bun install` and `bun dev` inside `frontend/`

Copy `backend/.env.example` to `backend/.env` and fill in your own database and
AWS settings before running anything.

## Project status

Actively developed as a personal project. The core booking flow, the admin panel
and the AWS integrations are in place; polish and test coverage are ongoing.
