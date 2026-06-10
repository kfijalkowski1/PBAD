# Pitstop Garage Management System — Iteration Plan

This document outlines the iteration plan for the Pitstop Garage Management System, following the Attribute-Driven Design (ADD 3.0) process. Each iteration focuses on a cohesive set of high-priority architectural drivers to incrementally build up the architecture from a stable structural foundation through the core business domain to the event-driven supporting services.

## Iteration Plan Overview

| Iteration | Goal | Primary Drivers |
|-----------|------|-----------------|
| 1 | Establish the overall microservices structure, containerization strategy, and supporting bounded contexts (Customer and Vehicle Management) | CRN-1, CON-1, CON-2, CON-3, CON-4, US-1, US-2, US-3, US-4, QAS-O1, QAS-L1 |
| 2 | Design the core domain — Workshop Management — using DDD, Event Sourcing, and CQRS | US-5, US-6, US-7, QAS-R3, QAS-R1, QAS-R2, QAS-L3, CRN-2, CRN-3 |
| 3 | Design the event-driven supporting services: Notification, Invoice, Auditlog, and Time Service | US-8, US-9, QAS-R4, QAS-L2, QAS-O3, CRN-4, CRN-5 |

---

## Iteration 1: Overall System Structure and Supporting Bounded Contexts

**Goal:** Establish the foundational microservices structure of the system. Define the containerization strategy, deployment topology, and the two supporting bounded contexts — Customer Management and Vehicle Management — which provide the reference data that the rest of the system depends on.

**Drivers to Address:**

- Concerns:
  - CRN-1: Establish an overall initial system structure for a microservices-based application.

- Constraints:
  - CON-1: All services are implemented in .NET / C#.
  - CON-2: Every service and all infrastructure components run as Docker containers; Docker Compose is the primary local orchestration tool.
  - CON-3: SQL Server is the database platform for all services.
  - CON-4: RabbitMQ is the message broker for all asynchronous inter-service communication.

- User Stories:
  - US-1: Register Customer
  - US-2: Look Up Customer
  - US-3: Register Vehicle
  - US-4: Look Up Vehicle

- Quality Attribute Scenarios:
  - QAS-O1: Running `docker compose up` starts all services; the system is accessible within 2 minutes.
  - QAS-L1: A .NET developer can understand the overall architecture and the role of each service within 30 minutes.

---

## Iteration 2: Core Domain — Workshop Management (DDD, Event Sourcing, CQRS)

**Goal:** Design the Workshop Management bounded context, which is the core domain of the system. Introduce Domain-Driven Design patterns (aggregates, value objects, domain events), Event Sourcing for aggregate persistence, and CQRS for separating the write model from the read model. Address the autonomy and resilience requirements that make the Workshop Management service independent of the supporting contexts.

**Drivers to Address:**

- User Stories:
  - US-5: Plan Maintenance Job
  - US-6: View Workshop Planning (by day)
  - US-7: Finish Maintenance Job

- Quality Attribute Scenarios:
  - QAS-R1: SQL Server is slow to start; services retry with exponential backoff and connect successfully without manual intervention.
  - QAS-R2: RabbitMQ is temporarily unavailable; services retry with exponential backoff and message publishing retries up to 9 times.
  - QAS-R3: The Customer Management API is offline when a maintenance job is being planned; Workshop Management operates autonomously using its local read-model of cached customer and vehicle data.
  - QAS-L3: A developer wants to understand how event sourcing works; the WorkshopManagementAPI provides a clear, isolated implementation of event sourcing with DDD aggregates that can be studied independently.

- Concerns:
  - CRN-2: Establish the event-driven communication pattern between services via RabbitMQ (fanout exchanges, domain events, manual acknowledgement).
  - CRN-3: Enforce the database-per-service pattern — each service accesses only its own logical database schema.

---

## Iteration 3: Event-Driven Supporting Services

**Goal:** Design the remaining event-driven services — Notification, Invoice, Auditlog, and the Time Service. These services have no direct HTTP dependencies on other services; they react purely to domain events. This iteration also addresses the resilience pattern at the WebApp level (circuit-breaker) and the system-wide observability strategy (centralized structured logging with Seq and health checks).

**Drivers to Address:**

- User Stories:
  - US-8: Receive Maintenance Notification — Customers are automatically notified by email when their vehicle has a maintenance job scheduled for the current day.
  - US-9: Receive Invoice — Customers receive an HTML invoice by email for every finished maintenance job.

- Quality Attribute Scenarios:
  - QAS-R4: The WebApp cannot reach a backend API after multiple retries; a Polly circuit-breaker triggers and the WebApp falls back to an offline page rather than showing an error.
  - QAS-L2: A presenter can register a customer and demonstrate the event flowing to consuming services in real-time via the Seq log server.
  - QAS-O3: Every API service exposes a `/hc` health-check endpoint; Docker performs health checks every 30 seconds.

- Concerns:
  - CRN-4: Establish centralized structured logging — all services use Serilog with a Seq sink; the machine name is added to all log events for multi-container correlation.
  - CRN-5: Establish the Kubernetes deployment topology with optional service mesh (Istio / Linkerd) for conference demonstration purposes.
