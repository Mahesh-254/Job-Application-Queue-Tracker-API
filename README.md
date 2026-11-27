# Job Application & Queue Tracker API

A RESTful backend service built with **FastAPI**, **SQLAlchemy**, and **JWT Authentication** to track candidate job applications, enforce queue integrity, and generate status metrics.

## Features
- **JWT Authentication:** User registration (`/register`) and OAuth2 bearer token login (`/login`) with bcrypt password hashing.
- **Full CRUD Operations:** Create, read, filter, update (`PATCH`), and delete (`DELETE`) job application records.
- **Data Validation & Integrity:** Strict `Enum` status enforcement (`Submitted`, `Interview`, `Rejected`, `Offer`) and `409 Conflict` duplicate submission prevention.
- **Queue Analytics:** Aggregated status breakdown endpoint (`/applications/stats/summary`).

## Setup & Run Locally
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate