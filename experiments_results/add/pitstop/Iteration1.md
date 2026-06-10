# Iteration 1 — Overall System Structure and Supporting Bounded Contexts

**Architect:** Neo  
**Process:** Attribute-Driven Design (ADD 3.0)  
**Iteration goal:** Establish the foundational microservices structure, containerization strategy, and the two supporting bounded contexts (Customer Management and Vehicle Management).

---

## Step 1: Review Inputs

### 1.1 Design Purpose

Pitstop is a **reference implementation** whose primary purpose is educational: it must demonstrate microservices architecture, event-driven design, DDD, CQRS, and event sourcing to .NET developers, conference audiences, and workshop participants. Architectural decisions must therefore prioritize **clarity**, **learnability**, and **demonstrability** alongside the functional correctness of the garage management domain.

This has a direct impact on design choices: patterns must be made explicitly visible (e.g., separate services for each bounded context, explicit event schemas, deliberate use of CRUD vs. DDD to contrast approaches), and operational complexity should be minimized where it does not add educational value.

### 1.2 Primary Functionality for This Iteration

The following user stories are in scope for Iteration 1:

| ID | User Story | Description |
|----|------------|-------------|
| US-1 | Register Customer | A garage employee registers a new customer (name, telephone, email). |
| US-2 | Look Up Customer | A garage employee retrieves a customer by ID or lists all customers. |
| US-3 | Register Vehicle | A garage employee registers a vehicle (license number, brand, type) and associates it with an existing customer. |
| US-4 | Look Up Vehicle | A garage employee retrieves a vehicle by license number or lists all vehicles. |

These four user stories are fully supported by the two supporting bounded contexts (Customer Management and Vehicle Management) identified in `DomainModel.md`. Both contexts use a simple CRUD design, which is appropriate for their supporting role and intentionally contrasts with the DDD + Event Sourcing approach used for Workshop Management in Iteration 2.

In addition to the four user stories, this iteration must establish the **overall system structure** that all subsequent iterations will build upon: the microservices decomposition, the communication topology, the containerization strategy, and the shared infrastructure components (RabbitMQ, SQL Server, Seq, MailDev).

### 1.3 Quality Attribute Scenarios

| ID | Quality Attribute | Scenario | Priority |
|----|-------------------|----------|----------|
| QAS-O1 | Operability | Running `docker compose up` starts all services and infrastructure. The system is accessible at `http://localhost:7005` within 2 minutes. | High |
| QAS-L1 | Learnability | A .NET developer can understand the overall architecture and the role of each service within 30 minutes by reading the documentation and browsing the code. | High |

**Analysis:**
- QAS-O1 drives the need for a well-defined Docker Compose configuration, health checks on all services, and retry policies for infrastructure dependencies (SQL Server, RabbitMQ) that may not be ready immediately.
- QAS-L1 drives the need for a clean, one-service-per-bounded-context decomposition with consistent code structure, clear naming conventions, and a shared messaging abstraction that hides broker-specific complexity.

### 1.4 Architectural Concerns

| ID | Concern | Description |
|----|---------|-------------|
| CRN-1 | Overall system structure | Establish the microservices decomposition, define service boundaries aligned with the DDD bounded contexts from `DomainModel.md`, define the inter-service communication pattern, and establish the deployment topology for all services. |

**Analysis:** CRN-1 is the dominant concern of this iteration. Without a stable structural foundation, subsequent iterations cannot proceed. The domain model already defines the service boundaries; this iteration must translate them into a concrete container topology.

### 1.5 Constraints

| ID | Constraint | Architectural Impact |
|----|------------|----------------------|
| CON-1 | .NET / C# | All service implementations use ASP.NET Core Web API for HTTP services and .NET hosted services for background workers. Shared infrastructure code is distributed as a NuGet package (`Infrastructure.Messaging`). |
| CON-2 | Docker / Docker Compose | All containers must be defined in a `docker-compose.yml`. Services must include `HEALTHCHECK` instructions and depend on health-checked infrastructure containers. |
| CON-3 | SQL Server | All services use SQL Server as their database engine. Each service owns a logically separate database schema on the shared SQL Server instance. Entity Framework Core (code-first migrations) is used for CRUD services. |
| CON-4 | RabbitMQ | RabbitMQ is the message broker. All inter-service async communication goes through `IMessagePublisher` / `IMessageHandler` interfaces defined in `Infrastructure.Messaging`, decoupling services from the concrete broker. |

**Analysis:** The constraints are mutually consistent and non-conflicting. CON-2 directly supports QAS-O1. CON-1 enables the NuGet-based sharing of the messaging abstraction demanded by CON-4. CON-3 intentionally avoids polyglot persistence complexity for educational clarity (the cost is a single point of failure at the database engine level, accepted as a known trade-off).

### 1.6 Consistency Review

| Check | Result |
|-------|--------|
| User stories traceable to domain model bounded contexts? | ✅ US-1/US-2 → `Customer` aggregate in Customer Management context. US-3/US-4 → `Vehicle` aggregate in Vehicle Management context. Both identified in `DomainModel.md`. |
| Quality attribute scenarios compatible with constraints? | ✅ QAS-O1 is enabled by CON-2 (Docker Compose). QAS-L1 is supported by CON-1 (single .NET stack, familiar to target audience). |
| Concerns consistent with iteration scope? | ✅ CRN-1 (overall structure) is the necessary precondition for Iterations 2 and 3. Addressing it first is correct sequencing. |
| Any conflicting requirements? | ✅ None identified. The intentional simplifications (CRUD for supporting contexts, single SQL Server instance) are documented and accepted. |
| Drivers not addressed in this iteration? | ✅ US-5 to US-9, QAS-R1 to QAS-R4, QAS-L2, QAS-L3, QAS-O2, QAS-O3, CRN-2 to CRN-5 are deferred to Iterations 2 and 3 as planned. |

**Conclusion:** All inputs are consistent, complete, and well-understood. Iteration 1 can proceed.

---

*— END OF STEP 1 — Confirmed. Proceeding to Step 2.*

---

## Step 2: Establish Iteration Goal by Selecting Drivers

### 2.1 Iteration Goal Statement

> **Establish the foundational microservices structure of the Pitstop system.** This iteration produces a deployable skeleton that includes the complete container topology, the two supporting bounded contexts (Customer Management and Vehicle Management) with their HTTP APIs, databases, and event publishing, the shared messaging abstraction library, and the infrastructure components (RabbitMQ, SQL Server, Seq, MailDev). All subsequent iterations will build on top of this foundation without requiring structural changes to what is designed here.

### 2.2 Driver Selection and Prioritization

The following drivers are addressed in this iteration. They are ordered by their influence on the structural decisions that must be made.

| Priority | Driver | Type | Rationale for Inclusion |
|----------|--------|------|--------------------------|
| 1 | **CRN-1** — Establish overall system structure | Concern | The dominant concern of this iteration. All other decisions (service count, communication topology, deployment model) depend on resolving this first. |
| 2 | **CON-2** — Docker / Docker Compose | Constraint | Determines the deployment unit (container) and the local orchestration mechanism. Directly shapes how services are structured and how infrastructure dependencies are declared. Also directly satisfies QAS-O1. |
| 3 | **CON-4** — RabbitMQ as message broker | Constraint | Determines the inter-service communication backbone. Must be established early because all services — including the two CRUD services in this iteration — must publish domain events through it. |
| 4 | **CON-3** — SQL Server as database platform | Constraint | Determines the persistence technology for all services. Entity Framework Core code-first migrations are chosen for the CRUD services in this iteration. |
| 5 | **CON-1** — .NET / C# | Constraint | Determines the technology stack for all services and shared libraries. Enables NuGet-based sharing of the `Infrastructure.Messaging` abstraction. |
| 6 | **US-1** — Register Customer | User Story | Core functional driver for Customer Management API. Requires `RegisterCustomer` command handling and `CustomerRegistered` event publication. |
| 7 | **US-2** — Look Up Customer | User Story | Core functional driver for Customer Management API (read path). Requires list and by-ID query endpoints. |
| 8 | **US-3** — Register Vehicle | User Story | Core functional driver for Vehicle Management API. Requires `RegisterVehicle` command and `VehicleRegistered` event. |
| 9 | **US-4** — Look Up Vehicle | User Story | Core functional driver for Vehicle Management API (read path). |
| 10 | **QAS-O1** — Docker Compose startup ≤ 2 min | Quality Attribute | Requires health checks on all containers and retry policies (Polly) for infrastructure dependencies. Shapes container configuration. |
| 11 | **QAS-L1** — Architecture understandable in 30 min | Quality Attribute | Requires consistent code structure across services, explicit naming conventions, and a shared abstraction that makes the system's communication patterns immediately visible. |

### 2.3 Drivers Deferred to Later Iterations

The following drivers are explicitly **out of scope** for Iteration 1 and deferred:

| Driver | Deferred to | Reason |
|--------|-------------|--------|
| US-5, US-6, US-7 | Iteration 2 | Depend on Workshop Management core domain (DDD + Event Sourcing), which requires the structural foundation from this iteration. |
| QAS-R1, QAS-R2, QAS-R3 | Iteration 2 | Resilience patterns (exponential backoff, autonomous operation) are most relevant in the context of the Workshop Management service. |
| QAS-L3 | Iteration 2 | Event sourcing implementation is out of scope for this iteration. |
| US-8, US-9, QAS-R4, QAS-L2, QAS-O3 | Iteration 3 | Depend on Notification, Invoice, and Time services, which depend on Workshop Management from Iteration 2. |
| CRN-2, CRN-3 | Iteration 2 | The event-driven communication pattern and the database-per-service enforcement are first exercised fully in Workshop Management. |
| CRN-4, CRN-5 | Iteration 3 | Centralized logging (Seq) and Kubernetes manifests are cross-cutting concerns added after the core structure is stable. |

### 2.4 Definition of Done for Iteration 1

This iteration is complete when:
- [ ] The complete container topology (all services and infrastructure) is defined and documented in the container diagram.
- [ ] Customer Management API supports `RegisterCustomer` (POST) and retrieval (GET by ID, GET all) with event publication.
- [ ] Vehicle Management API supports `RegisterVehicle` (POST) and retrieval (GET by license number, GET all) with event publication.
- [ ] The `Infrastructure.Messaging` shared library defines `IMessagePublisher` / `IMessageHandler` interfaces with a RabbitMQ implementation.
- [ ] All services and infrastructure run via `docker compose up` with health checks.
- [ ] Architecture.md is updated with the container diagram and populated sequence diagrams for US-1 to US-4 and QAS-O1.
- [ ] Design decisions for this iteration are recorded in Architecture.md.

---

*— END OF STEP 2 — Confirmed. Proceeding to Step 3.*

---

## Step 3: Choose One or More Elements of the System to Refine

### 3.1 Starting Point

At the beginning of Iteration 1, the system exists only as a black box (the C4 Level 1 context diagram in Architecture.md). The internal structure — the containers — has not yet been designed. There are no elements below the system boundary to select from. The element to refine is therefore the **system itself**: we will decompose it from a context-level black box into its constituent containers (C4 Level 2).

### 3.2 Elements Selected for Refinement

The following elements are selected for refinement in this iteration:

| # | Element | Current State | Refinement Action |
|---|---------|---------------|-------------------|
| 1 | **Pitstop System (entire system boundary)** | Black box from the context diagram | Decompose into individual containers aligned with the DDD bounded contexts from `DomainModel.md`. |
| 2 | **Customer Management bounded context** | Identified in `DomainModel.md` as a supporting domain (CRUD) | Instantiate as a concrete ASP.NET Core Web API container with its own SQL Server database. |
| 3 | **Vehicle Management bounded context** | Identified in `DomainModel.md` as a supporting domain (CRUD) | Instantiate as a concrete ASP.NET Core Web API container with its own SQL Server database. |
| 4 | **Infrastructure.Messaging shared library** | Referenced in domain model and constraints but not yet designed | Define the `IMessagePublisher` / `IMessageHandler` abstraction and its RabbitMQ implementation. |
| 5 | **Web Application** | Mentioned in context but not yet decomposed | Instantiate as an ASP.NET Core MVC container that orchestrates user-facing interactions and calls the backend APIs. |
| 6 | **Shared infrastructure containers** | Listed in Architecture.md container table but not yet defined | Define RabbitMQ, SQL Server, Seq, and MailDev containers as infrastructure dependencies of the system. |

### 3.3 Elements Deliberately Excluded from This Iteration

The following containers identified in the Architecture.md container diagram are **not refined** in this iteration. They appear in the container diagram as placeholders to show the complete topology, but their internal design is deferred.

| Element | Deferred to | Reason |
|---------|-------------|--------|
| Workshop Management API | Iteration 2 | Core domain; requires DDD + Event Sourcing design that depends on the structural foundation from this iteration. |
| Workshop Management Event Handler | Iteration 2 | Depends on Workshop Management API design. |
| Notification Service | Iteration 3 | Depends on Workshop Management events and Time Service. |
| Invoice Service | Iteration 3 | Depends on Workshop Management events and Time Service. |
| Time Service | Iteration 3 | Enabler for Notification and Invoice services. |
| Auditlog Service | Iteration 3 | Pure event consumer; designed after all event producers are defined. |

### 3.4 Refinement Scope Justification

Decomposing the entire system boundary in Iteration 1 is necessary because:

1. **CRN-1** explicitly requires establishing the overall structure. An incomplete topology would leave architectural unknowns that would delay Iterations 2 and 3.
2. **QAS-O1** (docker compose up within 2 minutes) requires *all* containers — including those not yet designed internally — to be declared in the Docker Compose file with correct networking, health checks, and startup ordering.
3. **QAS-L1** (understandable in 30 minutes) requires the full container map to be visible from the start. A developer reading the repository on day one should see all services, even if some are stubs.
4. The domain model already provides the decomposition logic (one service per bounded context), so the number of containers is not a design decision to be made here — it is a consequence of applying DDD to the known domain.

---

*— END OF STEP 3 — Awaiting review and confirmation to proceed to Step 4.*
