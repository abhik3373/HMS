# System Architecture Design

This diagram illustrates the flow of data and the decoupling of services within the Mini Hospital Management System.

```mermaid
graph TD
    User((User: Doctor/Patient)) -->|Browser| Frontend[Vanilla CSS/HTML Templates]
    Frontend -->|POST/GET| Django[Django Backend Monolith]
    
    subgraph "Core Backend"
        Django -->|ORM| Postgres[(PostgreSQL DB)]
        Django -->|In-Process Threads| AsyncTasks[Background Tasks]
    end

    subgraph "Service Integrations"
        AsyncTasks -->|HTTP POST| Serverless[Serverless Email Microservice]
        Serverless -->|SMTP| Gmail[Gmail Engine]
        AsyncTasks -->|OAuth2 API| GoogleCal[Google Calendar API]
    end

    Postgres -->|Row Locking| Booking[Atomic Booking Logic]
    Booking -.->|Prevent Race Condition| User
```

## Key Architectural Components:

1. **The Monolith (Django):** Handles business logic, authentication, and view rendering.
2. **The Database (PostgreSQL):** Uses ACID-compliant transactions and row-level locking (`select_for_update`) to manage concurrent booking attempts.
3. **The Microservice (Serverless/Node.js):** A decoupled service responsible solely for email rendering and delivery. This ensures the main app remains fast and responsive.
4. **Third-Party Sync:** Bi-directional integration with Google via OAuth2 for automated calendar management.
