# ADD Iteration 1 — eShop

**Author:** Neo (Software Architect)
**Method:** Attribute-Driven Design (ADD)
**Date:** 2026-06-09
**Iteration goal:** Establish the overall system structure

---

## Step 1 — Review Inputs

Before beginning design work, all inputs to this iteration are reviewed and their status confirmed.

### 1.1 Design Purpose

This is the **first iteration of a greenfield system**. The purpose of this design activity is to produce an architecture that satisfies the eShop's functional requirements and quality attribute scenarios, using a microservices architectural style as mandated by the project constraints.

There are no pre-existing architectural decisions to inherit. All structural decisions are made from scratch in this and subsequent iterations.

### 1.2 Architectural Drivers

The full set of architectural drivers is recorded in `Architecture.md` Section 3. They are summarised here with their assigned priorities for reference during this iteration.

#### User Stories

| ID  | User Story (summary)                  | Priority |
|-----|---------------------------------------|----------|
| US1 | Browse product catalogue              | High     |
| US2 | Filter catalogue by type              | High     |
| US3 | Filter catalogue by brand             | High     |
| US4 | Add items to basket                   | High     |
| US5 | Edit / remove basket items            | High     |
| US6 | Checkout                              | High     |
| US7 | Register an account                   | High     |
| US8 | Sign in / sign out                    | High     |
| US9 | Review orders                         | Medium   |

#### Quality Attribute Scenarios

| ID  | Quality Attribute  | Scenario (summary)                                                      | Priority |
|-----|--------------------|-------------------------------------------------------------------------|----------|
| QA1 | Availability       | Auto-scale on traffic spike; 99.9 % uptime; scale-out in < 2 min       | High     |
| QA2 | Availability       | Route around failed instances; no user-visible error; recovery < 30 s  | High     |
| QA3 | Observability      | Error traceable end-to-end in < 5 min via structured logs + correlation | High     |
| QA4 | Deployability      | Independent microservice deployment via CI/CD in < 15 min              | High     |
| QA5 | Portability        | Web, SPA, and mobile clients use identical API endpoints               | Medium   |
| QA6 | Maintainability    | Pricing logic change confined to Catalog service; zero cross-redeployment | Medium |

#### Architectural Concerns

| ID  | Concern (summary)                                     |
|-----|-------------------------------------------------------|
| AC1 | Consistent cross-service authentication               |
| AC2 | Resilient inter-service communication                 |
| AC3 | Data isolation — no shared databases                  |
| AC4 | Distributed tracing with correlation IDs              |
| AC5 | Event-driven integration for cross-context workflows  |

#### Constraints

| ID  | Constraint (summary)                                          |
|-----|---------------------------------------------------------------|
| CO1 | Architecture must be based on microservices                   |
| CO2 | Must support multi-platform deployment (on-prem and cloud)    |
| CO3 | Tooling and runtime must be cross-platform                    |
| CO4 | APIs must be consumable by web (MVC + SPA) and mobile clients |
| CO5 | Each deployable unit must support independent CI/CD           |

### 1.3 Domain Model

The domain model is fully elaborated in `DomainModel.md`. It identifies four bounded contexts — **Catalog**, **Basket**, **Ordering**, and **Identity** — each of which will map to an independent microservice. This model is the principal input to the functional decomposition of the system.

### 1.4 Input Status Assessment

| Input                        | Status   | Notes |
|------------------------------|----------|-------|
| Functional requirements      | Complete | All 9 user stories identified and prioritised |
| Quality attribute scenarios  | Complete | 6 scenarios with measurable response measures |
| Architectural concerns       | Complete | 5 concerns identified |
| Constraints                  | Complete | 5 constraints identified; CO1 (microservices) is non-negotiable |
| Domain model                 | Complete | 4 bounded contexts; aggregate roots and value objects defined |
| Existing architecture        | None     | Greenfield — no legacy to constrain decomposition |

All inputs are available and consistent. Proceeding to Step 2.

---

## Step 2 — Establish Iteration Goal and Select Inputs

### 2.1 Iteration Goal

The goal of this first iteration is to **establish the overall structure of the eShop system**. This means making the primary decomposition decisions — selecting the reference architecture, identifying the top-level system elements, and assigning high-level responsibilities to each. No internal component design is produced in this iteration; that is deferred to subsequent iterations.

This iteration directly addresses the constraint CO1 (microservices mandate) and lays the structural foundation that all quality attribute scenarios and user stories depend upon.

### 2.2 Driver Selection

Not all drivers need to be addressed in every iteration. For this first iteration, drivers are selected based on two criteria:

1. **Structural influence** — drivers that affect the top-level decomposition and cannot be deferred without risking rework.
2. **Priority** — High-priority drivers are addressed before Medium ones.

The following drivers are **selected** for this iteration:

#### Selected User Stories

| ID  | User Story (summary)          | Rationale for selection |
|-----|-------------------------------|-------------------------|
| US1 | Browse product catalogue      | Most common flow; determines Catalog service interface shape and client communication pattern |
| US4 | Add items to basket           | Drives Basket service boundary and its interaction with Catalog (price reference) |
| US6 | Checkout                      | Architecturally the most significant flow; crosses Basket → Ordering boundary via async event |
| US7 | Register an account           | Drives Identity service boundary; establishes token-issuance infrastructure used by all other services |
| US8 | Sign in / sign out            | Co-located with US7; determines the authentication mechanism adopted system-wide |

> US2, US3 (filtering) are structurally similar to US1 and will reuse the same Catalog service without adding new structural elements. US5 is structurally contained within the Basket service. US9 is a read-model concern within Ordering. These are deferred to later iterations.

#### Selected Quality Attribute Scenarios

| ID  | Quality Attribute  | Rationale for selection |
|-----|--------------------|-------------------------|
| QA1 | Availability (auto-scale) | Directly determines the deployment model; influences choice of container orchestration and stateless service design |
| QA2 | Availability (resilience) | Drives the need for a resilience pattern (circuit breaker, health checks) at the communication layer |
| QA3 | Observability      | Drives a cross-cutting tracing and logging infrastructure that must be established from the first structural decision |
| QA4 | Deployability      | Drives the need for independent deployment units; reinforces the service boundary decisions made from the domain model |

> QA5 (portability) and QA6 (maintainability) are addressed implicitly by the microservices decomposition and the API Gateway pattern. They are not selected as primary drivers for this iteration.

#### Selected Constraints

All five constraints (CO1–CO5) are selected. Constraints are non-negotiable and must be honoured in every iteration.

#### Selected Architectural Concerns

All five concerns (AC1–AC5) are selected. They are cross-cutting and must be reflected in the top-level structure established by this iteration.

### 2.3 Iteration Goal Statement (refined)

> **Iteration 1 Goal:** Establish the top-level structure of the eShop microservices system by selecting a reference architecture, decomposing the system into independently deployable services derived from the domain model, and identifying the infrastructure elements required to satisfy QA1 (availability), QA2 (resilience), QA3 (observability), and QA4 (deployability). The selected structure must honour all five constraints.

---

## Step 3 — Choose Elements to Refine

### 3.1 Element Selection Rationale

In ADD, the element to refine is the part of the architecture that will be decomposed or elaborated in this iteration. For a **greenfield system in Iteration 1**, the element to refine is the **system as a whole** — the single black box visible in the C4 Level 1 Context Diagram (Architecture.md, Section 2).

At this point the eShop system has no internal structure. The entire system exists as an opaque boundary that accepts requests from customers and administrators and interacts with external systems (Email Service, Payment Gateway, Identity Provider). The goal of this iteration is to open that black box and establish its primary structural decomposition.

### 3.2 Element Being Refined

| Element | Current State | Goal After This Iteration |
|---------|---------------|---------------------------|
| **eShop System** (C4 Level 1 boundary) | Unstructured black box. No internal elements defined. | Decomposed into a set of named containers (C4 Level 2): frontends, microservices, databases, cache, and message bus — each with assigned responsibilities. |

### 3.3 Drivers Influencing This Refinement

The following selected drivers from Step 2 directly influence how the system black box is broken down:

| Driver | Influence on Decomposition |
|--------|----------------------------|
| CO1 — Microservices mandate | Each bounded context from the domain model becomes a separate, independently deployable service container. |
| US6 — Checkout | Requires a clear boundary between the Basket and Ordering services communicating asynchronously. |
| US7 / US8 — Registration / Auth | Requires a dedicated Identity service that issues tokens consumed by all other services. |
| QA1 — Auto-scaling | Services must be stateless and containerised so the orchestrator can scale individual services independently. |
| QA2 — Resilience | A dedicated API Gateway element is needed to enforce circuit-breaking, retries, and health-check routing at the entry point. |
| QA3 — Observability | A shared observability infrastructure (structured logging, distributed tracing) must be reflected as a cross-cutting concern across all service elements. |
| QA4 — Deployability | Service boundaries must be strict (no shared databases, no shared code at runtime) so each unit can be deployed independently. |
| AC3 — Data isolation | Each service owns an exclusive data store; no container is shared between two services. |
| AC5 — Event-driven integration | An asynchronous messaging element (message bus) must be present to decouple services for cross-context workflows. |
| CO4 — Multi-client support | A client-facing entry point (API Gateway / BFF) must be present to serve web MVC, SPA, and mobile clients from a single API surface. |

---

## Step 4 — Choose Design Concepts

In this step, the design concepts — reference architectures, architectural patterns, and tactics — that will be used to satisfy the selected drivers are identified and justified. For each concept, the driver(s) it addresses, the rationale for selection, and the discarded alternatives are recorded. These decisions will be transferred to the Design Decisions table in `Architecture.md` Section 9.

---

### DC1 — Reference Architecture: Microservices

| Attribute | Value |
|-----------|-------|
| **Drivers addressed** | CO1, QA1, QA2, QA4, QA6, AC2, AC3 |
| **Concept** | The system is decomposed into a set of small, independently deployable services, each owning a single bounded context from the domain model. Services communicate over the network via lightweight protocols (HTTP/REST or asynchronous messaging). Each service is built, tested, and deployed independently. |
| **Rationale** | CO1 mandates microservices as a non-negotiable constraint. Beyond compliance, this pattern is the only architecture that can satisfy QA1 (per-service auto-scaling), QA4 (independent CI/CD pipelines), and QA6 (change isolation). The domain model has already produced four clean bounded contexts that map naturally to service boundaries, minimising the risk of inappropriate decomposition. |
| **Discarded alternatives** | **Modular monolith** — satisfies CO3 and QA6 but cannot meet QA1 or QA4 (the entire process must be scaled and deployed as a unit). **Service-Oriented Architecture (SOA)** — violates AC3 (shared databases are common in SOA) and CO5 (heavyweight governance). Both are eliminated by CO1 explicitly. |

---

### DC2 — API Gateway / Backend for Frontend (BFF)

| Attribute | Value |
|-----------|-------|
| **Drivers addressed** | CO4, QA2, QA5, AC1 |
| **Concept** | A single API Gateway sits in front of all backend microservices and acts as the sole entry point for all clients (Web MVC, SPA, Mobile). It handles request routing, response aggregation, rate limiting, and token validation. The gateway pattern is implemented as a Backend for Frontend (BFF), providing a unified API surface regardless of which downstream service handles the request. |
| **Rationale** | CO4 requires one API surface for three client types. Without a gateway, each client would need to know the topology of all microservices, creating tight coupling between clients and internal structure. The gateway insulates clients from changes in the service topology (QA6) and provides a single point at which cross-cutting policies (auth validation — AC1, circuit breaking — QA2) are enforced consistently. |
| **Discarded alternatives** | **Direct client-to-service communication** — violates CO4 (clients become coupled to service topology) and makes AC1 impossible to enforce consistently. **Service mesh only (no gateway)** — handles east-west traffic well but does not provide a client-facing aggregation point; clients would still need to call multiple services. |

---

### DC3 — Asynchronous Messaging for Cross-Context Integration

| Attribute | Value |
|-----------|-------|
| **Drivers addressed** | US6, AC5, QA2 |
| **Concept** | Cross-context workflows — most critically the Checkout flow (Basket → Ordering) — are implemented using integration events published to a durable message bus. The publishing service (Basket) publishes an `OrderStarted` event and considers its responsibility complete. The subscribing service (Ordering) consumes the event independently and creates the Order aggregate. The message bus guarantees at-least-once delivery. |
| **Rationale** | Synchronous REST calls between services for the checkout flow would create temporal coupling: if the Ordering service is unavailable at checkout time, the entire transaction fails and the user sees an error. Asynchronous messaging decouples availability of producer from consumer (supporting QA2) and preserves service autonomy (AC5). The durable bus also acts as a buffer during traffic spikes (QA1). |
| **Discarded alternatives** | **Synchronous REST (Basket calls Ordering directly)** — creates temporal coupling; a failure in Ordering propagates to the user during checkout. **Choreography-only without a bus** — point-to-point callbacks between services reintroduce coupling. **Orchestration (Saga orchestrator)** — adds complexity appropriate for later iterations; the event choreography pattern is sufficient for the current scope. |

---

### DC4 — Distributed Cache for Basket State (Redis)

| Attribute | Value |
|-----------|-------|
| **Drivers addressed** | QA1, AC3 |
| **Concept** | The Basket service stores all basket state in a distributed Redis cache rather than a relational database. Each basket is keyed by buyer ID. The service process is fully stateless; all session state lives in the cache, which is shared across all Basket service instances. |
| **Rationale** | QA1 requires the Basket service to scale horizontally. Stateless processes can be added or removed by the orchestrator without requiring session affinity (sticky sessions), which would defeat auto-scaling. Redis provides sub-millisecond read/write latency appropriate for the high-frequency basket update operations and supports data expiry (TTL) for abandoned baskets. AC3 (data isolation) is satisfied because Redis is exclusively owned by the Basket service. |
| **Discarded alternatives** | **Relational database for basket** — durable but introduces write bottlenecks for high-frequency updates and requires connection pooling management during scale-out. **In-memory session on the service process** — violates QA1 (state lost when an instance is replaced) and QA2 (instance failure destroys basket). |

---

### DC5 — OpenID Connect / OAuth 2.0 with a Dedicated Identity Service

| Attribute | Value |
|-----------|-------|
| **Drivers addressed** | US7, US8, AC1, CO4 |
| **Concept** | Authentication and authorisation are handled by a dedicated Identity microservice that implements the OpenID Connect (OIDC) protocol on top of OAuth 2.0. Upon successful authentication, the Identity service issues a signed JWT bearer token. All other services validate this token locally using the Identity service's public key — they do not call the Identity service on every request. |
| **Rationale** | CO4 requires that web MVC, SPA, and mobile clients all authenticate against the same mechanism. OIDC is an open, well-supported standard that all three client types can consume. Token-based auth (JWT) allows downstream services to validate identity without a synchronous call to the Identity service on every request (reducing latency and coupling — AC1). The dedicated Identity service isolates the security-critical code from business logic. |
| **Discarded alternatives** | **Cookie/session-based auth** — does not translate cleanly to mobile clients and SPA use cases; does not satisfy CO4. **Shared auth library in every service** — violates AC1 (inconsistent enforcement risk) and CO1 (shared library creates deployment coupling). **Delegating entirely to a third-party IdP** — viable but reduces control over user data and registration UX (US7); can be revisited as an enhancement. |

---

### DC6 — Container Orchestration (Docker + Kubernetes)

| Attribute | Value |
|-----------|-------|
| **Drivers addressed** | QA1, QA2, QA4, CO2, CO3 |
| **Concept** | All microservices are packaged as Docker container images. The runtime environment is managed by a container orchestrator (Kubernetes or a compatible platform). The orchestrator is responsible for scheduling containers, performing health checks, routing traffic away from failed instances, and scaling replica counts up or down in response to load metrics. |
| **Rationale** | Docker containers are cross-platform by construction (CO2, CO3) — the same image runs on-premises or in any cloud provider. Kubernetes provides native auto-scaling (Horizontal Pod Autoscaler — QA1), liveness/readiness probes that satisfy QA2 (unhealthy instances are removed from service without manual intervention), and rolling deployments that satisfy QA4 (deploy one service without downtime to others). |
| **Discarded alternatives** | **VM-based deployment** — satisfies CO2 but does not provide native auto-scaling or health-check-based routing; operational overhead is significantly higher. **Platform-as-a-Service (Azure App Service, AWS Elastic Beanstalk)** — may satisfy QA1 and QA4 but ties the architecture to a specific cloud vendor, potentially violating CO2 (multi-platform hosting). |

---

### DC7 — Structured Logging and Distributed Tracing

| Attribute | Value |
|-----------|-------|
| **Drivers addressed** | QA3, AC4 |
| **Concept** | All services emit structured (JSON) log entries that include a **correlation ID** propagated from the API Gateway through every downstream service call and integration event. A centralised log aggregation and search platform (e.g., ELK Stack or OpenTelemetry-compatible collector) ingests logs from all containers. Distributed tracing (OpenTelemetry) captures spans across service boundaries for end-to-end request visibility. |
| **Rationale** | QA3 requires that any error be traceable end-to-end within 5 minutes. This is impossible without a correlation ID that follows the request across service hops and the message bus. Structured JSON logs are machine-parseable and enable fast querying. OpenTelemetry is a vendor-neutral standard (supporting CO2) that works with multiple backends. This is a cross-cutting concern that must be established at the infrastructure level (AC4) — it cannot be bolted on later without touching every service. |
| **Discarded alternatives** | **Unstructured text logs per service** — not queryable across service boundaries; makes QA3 unachievable. **No centralised aggregation (logs on individual hosts)** — unacceptable for a distributed system where logs are spread across many container instances. |

---

### DC8 — Database-per-Service with Relational Stores

| Attribute | Value |
|-----------|-------|
| **Drivers addressed** | AC3, QA4, CO1 |
| **Concept** | Each microservice owns an exclusive relational database (SQL Server). No service accesses another service's database directly. Cross-service data needs are satisfied by API calls or integration events, never by shared database tables or views. |
| **Rationale** | AC3 (data isolation) is non-negotiable in a microservices architecture. A shared database creates an implicit coupling contract between services: schema changes in one service break others, and independent deployment (QA4) becomes impossible. Relational stores are chosen as the default because the domain model is inherently relational (entities with relationships and transactional integrity requirements). |
| **Discarded alternatives** | **Shared relational database with schema isolation** — reduces operational overhead but reintroduces deployment coupling (DDL changes require coordination). **NoSQL per service** — appropriate for some contexts (Basket, which uses Redis) but the Catalog and Ordering domains have structured relational data; using NoSQL would require denormalisation trade-offs not yet justified by a performance requirement. |

---

## Step 5 — Instantiate Elements and Allocate Responsibilities

*(To be completed)*

---

## Step 6 — Sketch Views and Record Design Decisions

*(To be completed)*

---

## Step 7 — Perform Analysis and Review Iteration Goal

*(To be completed)*
