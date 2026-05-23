# ADD Iteration 1 — Establish Overall System Structure and Microservice Decomposition

## Overview

| | |
|---|---|
| **Iteration** | 1 |
| **Goal** | Establish the overall microservices architecture — decompose the system into independently deployable services aligned with bounded contexts, define the communication topology, and verify the system starts end-to-end with Docker Compose. |
| **Drivers** | UC-01, UC-02, UC-03, QAS-D1, CON-01, CON-02, CON-05, CRN-01, CRN-06 |
| **Element refined** | The Pitstop system (entire system — black box decomposition) |
| **Status** | In progress — Step 2 complete |

---

## Step 1: Review Inputs

This step examines all available architectural inputs — design purpose, primary functionality, quality attributes, constraints, and architectural concerns — to ensure the design effort is grounded in a complete and consistent understanding of the problem space before any design decisions are made.

### 1.1 Design Purpose

Pitstop is a **greenfield educational reference implementation** of a garage management system. Its design purpose is dual:

1. **Functional purpose**: support garage employees in their daily operations — registering customers and vehicles, planning maintenance jobs, and automating follow-up activities (notifications, invoicing, audit logging).
2. **Educational purpose**: demonstrate, in a single working system, how microservices architecture, event-driven communication, Domain-Driven Design (DDD), CQRS, and event sourcing are applied in a .NET ecosystem. This second purpose is the **primary architectural driver** and takes precedence over production-grade concerns such as scalability or high availability.

Because this is greenfield development, the initial iteration must establish the entire structural foundation from scratch. There are no existing components to refine or extend. The decomposition chosen in this iteration defines service boundaries, data ownership, and the communication topology for the lifetime of the system.

### 1.2 Primary Functionality

The six use cases below represent the complete functional scope of the system. Three are classified as **High** priority and drive the structural decomposition in this iteration; three are **Medium/Low** and are addressed in later iterations.

| ID | Title | Priority | Relevance to Iteration 1 |
|----|-------|----------|--------------------------|
| UC-01 | Register and look up customers | **High** | Defines the Customer Management bounded context and its API surface |
| UC-02 | Register vehicles and associate with owner | **High** | Defines the Vehicle Management bounded context and its API surface |
| UC-03 | Plan and track maintenance jobs | **High** | Defines the Workshop Management bounded context — the core domain |
| UC-04 | Send daily maintenance notifications | Medium | Deferred to Iteration 2 |
| UC-05 | Generate and email invoices | Medium | Deferred to Iteration 2 |
| UC-06 | Record all domain events for audit | Low | Deferred to Iteration 2 |

### 1.3 Quality Attribute Scenarios

Eleven quality attribute scenarios have been identified across four quality goals. For Iteration 1, only **QAS-D1** is a direct driver — the others will be addressed in later iterations once the structural foundation exists.

| ID | Quality Attribute | Priority | Relevance to Iteration 1 |
|----|------------------|----------|--------------------------|
| QAS-D1 | Demonstrability | **High** | **Primary driver**: `docker compose up` must start all containers within 2 minutes on a clean machine. This constrains how services are packaged and how startup dependencies are managed. |
| QAS-L1 | Learnability | High | Deferred to Iteration 3 — requires completed structure |
| QAS-L2 | Learnability | High | Deferred to Iteration 3 |
| QAS-L3 | Learnability | High | Deferred to Iteration 3 |
| QAS-A1 | Autonomy | High | Deferred to Iteration 2 — requires event-driven communication to be designed |
| QAS-A2 | Autonomy | High | Deferred to Iteration 2 |
| QAS-R1 | Resilience | High | Deferred to Iteration 2 |
| QAS-R2 | Resilience | High | Deferred to Iteration 2 |
| QAS-D2 | Demonstrability | Medium | Deferred to Iteration 3 |
| QAS-R3 | Resilience | Medium | Deferred to Iteration 3 |
| QAS-D3 | Demonstrability | Low | Deferred to Iteration 3 |

### 1.4 Constraints

All constraints are binding. The table below identifies their relevance to this iteration specifically.

| ID | Constraint | Relevance to Iteration 1 |
|----|------------|--------------------------|
| CON-01 | All services implemented in .NET / C# | **Primary driver**: directly determines the technology stack for all containers identified in this iteration. Enables shared NuGet infrastructure libraries. |
| CON-02 | Every service runs as a Linux Docker container; Docker Compose is the local orchestration tool | **Primary driver**: every container identified in this iteration must be independently containerisable. Docker Compose governs how they are started together (QAS-D1). |
| CON-03 | Single SQL Server instance; per-service schema isolation | Informational for this iteration — schema ownership is confirmed per service, but the mechanics of isolation are deferred to Iteration 2. |
| CON-04 | RabbitMQ is the sole message broker | Informational for this iteration — the broker is identified as a container, but its event flows are designed in Iteration 2. |
| CON-05 | Microservices architecture — each service independently deployable | **Primary driver**: directly mandates the decomposition style. No monolith or modular monolith is permissible. |
| CON-06 | All broker interactions via `IMessagePublisher` / `IMessageHandler` abstractions | Informational for this iteration — introduces the `Infrastructure.Messaging` shared library as a container candidate. |
| CON-07 | Open source; no proprietary runtime dependencies | Informational for this iteration. |

### 1.5 Architectural Concerns

| ID | Concern | Relevance to Iteration 1 |
|----|---------|--------------------------|
| CRN-01 | Establish overall initial system structure | **Primary goal of this iteration**: no other iteration can proceed without a decomposed structure. |
| CRN-02 | Demonstrate multiple design approaches (DDD vs. CRUD) without cross-contamination | Informational — the structure established here must provide separate, isolated service boundaries to make this possible. The detailed design patterns within each service are deferred to Iteration 2. |
| CRN-03 | Achieve per-service data autonomy within shared SQL Server | Informational for this iteration — SQL Server is identified as a container and per-service schema ownership is established. Enforcement mechanisms are deferred to Iteration 2. |
| CRN-04 | Handle time-dependent behaviour deterministically | Informational for this iteration — the Time Service is identified as a container. Its event publishing behaviour is designed in Iteration 2. |
| CRN-05 | Centralised observability without heavy infrastructure | Informational for this iteration — Seq is identified as a container. The observability design is deferred to Iteration 3. |
| CRN-06 | Manage shared infrastructure code without tight coupling | **Driver for this iteration**: the `Infrastructure.Messaging` shared library must be introduced at the structural level as a NuGet package dependency to satisfy CON-06, and its boundaries must be defined so services do not couple directly to broker implementations. |

### 1.6 Key Observations from Input Review

The following observations are drawn from examining all inputs and will directly inform the design decisions in subsequent steps:

1. **No existing architectural elements exist.** The system is greenfield. The element to be refined in Step 3 is the entire system — we begin at the highest level of abstraction (black box decomposition).

2. **Multiple converging drivers mandate microservices.** CON-05 (microservices), CON-02 (Docker containers), the educational purpose (demonstrating service decomposition), and the domain model's seven bounded contexts all independently require a microservices decomposition. No alternative style is compatible with the drivers.

3. **The domain model has already established seven bounded contexts** (Customer Management, Vehicle Management, Workshop Management, Notification, Invoice, Audit Log, Time). Service boundaries should align with these contexts to preserve aggregate integrity and avoid reintroducing cross-context coupling.

4. **Two distinct service types emerge from the domain model.** Three contexts expose synchronous REST APIs (Customer, Vehicle, Workshop Management) and are called by the WebApp. Four contexts operate as autonomous background workers (Notification, Invoice, Audit Log, Time) that consume events and have no synchronous callers. This asymmetry must be reflected in the container decomposition.

5. **Shared infrastructure code (CRN-06) must be resolved at the structural level.** The `IMessagePublisher` / `IMessageHandler` abstraction (CON-06) and cross-cutting concerns (Polly, Serilog, health checks) cannot live inside any single service. They must be packaged as a shared NuGet library, establishing a dependency that affects the build structure of all services.

6. **QAS-D1 constrains startup ordering.** Docker Compose must start all containers successfully within 2 minutes. This requires all services to handle the situation where their infrastructure dependencies (SQL Server, RabbitMQ) are not yet ready when the service starts — a design constraint that will be resolved in Iteration 2 (QAS-R1, QAS-R2) but whose architectural implication (health-check and depends-on configuration) must be anticipated in the container structure defined here.

7. **No API gateway is warranted.** The WebApp calls only three APIs (Customer, Vehicle, Workshop Management). The educational purpose favours simplicity. Adding an API gateway would introduce a layer of indirection that obscures the microservices patterns being demonstrated without adding any capability that serves the drivers of this system. This will be recorded as a design decision.

---

## Step 2: Establish Iteration Goal by Selecting Drivers

This step formally establishes what this iteration must achieve and identifies the specific drivers that will govern all design decisions made within it. Drivers not listed here remain in the backlog for future iterations.

### 2.1 Iteration Goal

> **Decompose the Pitstop system into a set of independently deployable microservices aligned with its bounded contexts, define the communication topology between those services, and establish the shared infrastructure structure, such that the entire system can be started end-to-end with a single `docker compose up` command.**

This goal is deliberately structural. Iteration 1 operates at the highest level of abstraction — the entire system as a black box. Its output is not a working feature but the architectural skeleton within which all subsequent iterations will design specific capabilities. Every decision made here constrains and shapes what is possible in Iterations 2 and 3.

### 2.2 Selected Drivers

The following drivers are selected for this iteration. All are structural or infrastructural in nature — none can be addressed by refining an individual component, because the components themselves do not yet exist.

| Driver | Type | Rationale for Selection |
|--------|------|------------------------|
| **CRN-01** — Establish overall initial system structure | Architectural Concern | The foundational concern of any greenfield system. No other design work can proceed without a decomposition to build upon. This is the entire purpose of Iteration 1. |
| **CON-05** — Microservices architecture; each service independently deployable | Constraint | Directly mandates the decomposition style and granularity. All container boundaries defined in this iteration must satisfy independent deployability. |
| **CON-01** — All services implemented in .NET / C# | Constraint | Determines the technology stack for every container. Enables the shared NuGet infrastructure library strategy required by CRN-06. Must be established at the structural level before any component-level decisions. |
| **CON-02** — Every service runs as a Linux Docker container; Docker Compose for local orchestration | Constraint | Every container identified in this iteration must be independently containerisable. Docker Compose is the delivery mechanism for QAS-D1 and must be defined as part of this iteration's output. |
| **QAS-D1** — System starts within 2 minutes via `docker compose up` | Quality Attribute Scenario | Constrains how startup ordering and infrastructure dependencies are handled. The container decomposition must be completable enough to produce a working Compose file. |
| **UC-01** — Register and look up customers | Use Case | Defines the existence and API surface of the Customer Management service. The decomposition must include a container that satisfies this use case. |
| **UC-02** — Register vehicles and associate with owner | Use Case | Defines the existence and API surface of the Vehicle Management service. The decomposition must include a container that satisfies this use case. |
| **UC-03** — Plan and track maintenance jobs | Use Case | Defines the existence and API surface of the Workshop Management service — the core domain. The decomposition must include a container that satisfies this use case and is designed to accommodate the DDD + event sourcing approach required in Iteration 2. |
| **CRN-06** — Manage shared infrastructure code without tight coupling | Architectural Concern | Must be resolved at this structural level: the `Infrastructure.Messaging` abstraction (and other cross-cutting concerns) requires a shared NuGet library, which is a build-level decision that affects the structure of all services. |

### 2.3 Drivers Deferred to Later Iterations

The following drivers are explicitly out of scope for Iteration 1. They will be addressed once the structural foundation established here provides sufficient context.

| Driver | Deferred to Iteration | Reason for Deferral |
|--------|----------------------|---------------------|
| UC-04: Send daily notifications | 2 | Requires event-driven communication to be designed first |
| UC-05: Generate and email invoices | 2 | Requires event-driven communication and the `DayHasPassed` event pattern |
| UC-06: Record all domain events for audit | 2 | Requires the event broker topology to be established |
| QAS-A1, QAS-A2: Service autonomy | 2 | Requires local read-model and event subscription patterns |
| QAS-R1, QAS-R2: Retry and resilience | 2 | Requires services and broker container to exist before retry policies can be designed |
| CON-04: RabbitMQ as sole message broker | 2 | Broker is identified as a container here; event flows and routing designed in Iteration 2 |
| CON-06: Messaging abstraction | 2 | Library structure defined here; usage patterns and interfaces designed in Iteration 2 |
| CRN-02: Multiple design approaches | 2 | Requires Workshop Management internals to be designed |
| CRN-03: Per-service data autonomy | 2 | Schema isolation mechanisms designed when event-driven patterns are established |
| CRN-04: Deterministic time behaviour | 2 | Time Service is identified as a container here; event publishing designed in Iteration 2 |
| QAS-R3: Circuit breaker fallback | 3 | Requires WebApp and API containers to exist first |
| QAS-D2: Kubernetes deployment | 3 | Builds directly on the Docker Compose structure established here |
| QAS-D3: Health check endpoints | 3 | Cross-cutting concern added after service internals are established |
| QAS-L1, QAS-L2, QAS-L3: Learnability | 3 | Can only be assessed once the full structure and documentation are complete |
| CRN-05: Centralised observability | 3 | Seq identified as a container here; structured logging design deferred to Iteration 3 |

### 2.4 Expected Outcomes of This Iteration

By the end of Iteration 1, the following artefacts must be produced:

1. **Container diagram** — showing all deployable units, their responsibilities, and their top-level communication relationships (web-to-API and presence of the broker).
2. **Container responsibility table** — detailing what each container owns and provides.
3. **Sequence diagrams for UC-01, UC-02, UC-03, and QAS-D1** — tracing the primary request flows at the container level.
4. **Design decisions** — documenting the rationale for the microservices decomposition, the no-API-gateway decision, the shared library approach, and the Docker Compose startup topology.
5. **Updated Architecture.md** — container diagram, container responsibilities, and design decisions populated.

---

*— End of Step 2. Awaiting review before proceeding to Step 3.*
