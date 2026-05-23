# Pitstop — Iteration Plan

**Architect**: Neo  
**Method**: Attribute-Driven Design 3.0  
**Date**: 2026-05-23

---

## Overview

This document outlines the iteration plan for the Pitstop Garage Management System, following the Attribute-Driven Design (ADD) 3.0 process. Each iteration addresses a focused set of high-priority architectural drivers — use cases, quality attribute scenarios, constraints, and concerns — and incrementally refines the architecture documented in `Architecture.md`.

Iterations are ordered so that the highest-priority and most structurally fundamental drivers are addressed first. Each iteration builds on the results of the previous one.

| Iteration | Goal | Primary Drivers |
|-----------|------|----------------|
| 1 | Establish overall system structure and microservice decomposition | UC-01, UC-02, UC-03, CON-01, CON-02, CON-05, CRN-01, CRN-06, QAS-D1 |
| 2 | Event-driven communication, Workshop Management core domain, and service autonomy | UC-03, UC-04, UC-05, UC-06, QAS-A1, QAS-A2, QAS-R1, QAS-R2, CON-04, CON-06, CRN-02, CRN-03, CRN-04 |
| 3 | Resilience, observability, and deployment model | QAS-R3, QAS-D2, QAS-D3, QAS-L1, QAS-L2, QAS-L3, CRN-05, CON-07 |

---

## Iteration 1: Establish Overall System Structure and Microservice Decomposition

**Goal**: Define the top-level microservices architecture — identify and decompose the system into independently deployable services aligned with bounded contexts, establish the communication topology, and confirm that the system can be started end-to-end using Docker Compose.

**Drivers to Address**:

- Use Cases:
  - UC-01: Register and look up customers
  - UC-02: Register vehicles and associate with owner
  - UC-03: Plan and track maintenance jobs

- Quality Attribute Scenarios:
  - QAS-D1: System starts within 2 minutes with `docker compose up` on a clean machine

- Constraints:
  - CON-01: All services implemented in .NET / C#
  - CON-02: Every service runs as a Linux Docker container; Docker Compose is the local orchestration tool
  - CON-05: Microservices architecture — each service independently deployable

- Concerns:
  - CRN-01: Establish overall initial system structure
  - CRN-06: Manage shared infrastructure code without tight coupling

---

## Iteration 2: Event-Driven Communication, Core Domain, and Service Autonomy

**Goal**: Design the asynchronous event-driven communication infrastructure and implement the Workshop Management bounded context as the core domain using DDD, event sourcing, and CQRS. Ensure that each service can operate autonomously even when dependent services are unavailable.

**Drivers to Address**:

- Use Cases:
  - UC-03: Plan and track maintenance jobs (detailed design of the core domain)
  - UC-04: Send daily maintenance notifications
  - UC-05: Generate and email invoices for finished maintenance jobs
  - UC-06: Record all domain events for audit

- Quality Attribute Scenarios:
  - QAS-A1: WorkshopManagementAPI continues operating when CustomerManagementAPI is offline
  - QAS-A2: Redeploying a single service causes zero disruption to other running services
  - QAS-R1: Services retry database connections with exponential backoff on startup
  - QAS-R2: Services retry RabbitMQ connections; published messages retried up to 9 times

- Constraints:
  - CON-04: RabbitMQ is the sole message broker for all asynchronous communication
  - CON-06: All broker interactions go through `IMessagePublisher` / `IMessageHandler` abstractions

- Concerns:
  - CRN-02: Demonstrate DDD + Event Sourcing in Workshop Management alongside CRUD in supporting contexts
  - CRN-03: Achieve service data autonomy within a shared SQL Server instance
  - CRN-04: Handle time-dependent behaviour (daily events) deterministically and demonstrably

---

## Iteration 3: Resilience, Observability, and Deployment Model

**Goal**: Complete the architecture with cross-cutting resilience patterns (circuit breakers, retry policies), a centralised observability stack (structured logging via Serilog and Seq), and the Kubernetes deployment model. Ensure the system is easy to understand, easy to monitor, and easy to demonstrate.

**Drivers to Address**:

- Quality Attribute Scenarios:
  - QAS-R3: Circuit breaker on WebApp triggers offline fallback after repeated API failures
  - QAS-D2: Kubernetes manifests deploy the system; service mesh is optional and additive
  - QAS-D3: Every API service exposes `/hc` health endpoints; Docker performs automatic health checks
  - QAS-L1: A developer understands the overall architecture within 30 minutes from documentation and code
  - QAS-L2: Event flow is visible end-to-end in real time via the Seq log server during a live demo
  - QAS-L3: The WorkshopManagementAPI event sourcing pattern is understandable in isolation

- Constraints:
  - CON-07: No proprietary runtime dependencies; open source only (Seq free tier permitted)

- Concerns:
  - CRN-05: Centralised, structured observability using Serilog + Seq without heavy tracing infrastructure
