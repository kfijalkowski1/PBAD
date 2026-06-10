# Iteration 1 — Core System Structure and External Identity Integration

**ADD Process:** Attribute-Driven Design 3.0  
**Iteration Goal:** Establish the fundamental system structure and implement integration with the external Identity Provider.  
**Status:** Step 3 — In Progress

---

## Step 1: Review Inputs

The purpose of this step is to examine all inputs available before any design decisions are taken. Reviewing inputs thoroughly prevents premature design choices and surfaces conflicts or gaps that must be resolved before the iteration can proceed.

### 1.1 Design Purpose

This is a **greenfield initial design** effort. No prior system exists; the architecture is being produced from scratch. The overall design purpose is to produce a scalable, secure, and maintainable microservices-based architecture for the Event Ticket Booking System that satisfies all architectural drivers identified in the requirements documents.

This first iteration serves a dual purpose:

1. **Establish the foundational structure** of the overall system — the API Gateway, the core deployment topology, the inter-service communication patterns, and the environment management strategy that all subsequent iterations will build upon.
2. **Design the Identity and Access bounded context** in sufficient detail to support user registration, email verification, login, and password reset via the external Identity Provider.

Because this iteration lays the skeleton that all future iterations depend on, architectural decisions taken here carry the highest structural risk and must be made with particular care.

---

### 1.2 Primary Functionality

The four user stories assigned to this iteration all belong to Feature F1 (User Authentication) and are tightly coupled through their shared dependency on the external Identity Provider.

| ID | User Story | Priority | Summary |
|----|------------|----------|---------|
| US001 | User Registration | High | A new user registers an account. The system delegates identity creation to the external IdP and creates a corresponding user profile internally. |
| US002 | Email Verification | High | After registration, the user verifies their email address via a token sent by the IdP. The system updates the user's verification status. |
| US003 | User Login | High | A registered and verified user authenticates. The system delegates credential validation to the IdP and issues a JWT access token for subsequent API calls. |
| US004 | Password Reset | High | A user who has forgotten their password initiates a reset. The system delegates token generation, delivery, and password update to the IdP. After reset, all active sessions are invalidated. |

**Key functional observations:**

- All four flows pass through the API Gateway, which must be established and configured in this iteration.
- The Authentication Service acts as an orchestrator between the client, the IdP, and the User Service. Its boundaries must be clearly defined.
- The User Service is also introduced in this iteration to manage user profile data independently from the identity credentials managed by the IdP.
- Session invalidation in US004 implies that a session/token store (cache) must be available from this iteration onward.

---

### 1.3 Quality Attribute Scenarios

| ID | Scenario | Quality Attribute | Business Priority | Technical Priority | Measurable Response |
|----|----------|-----------------|-------------------|--------------------|---------------------|
| QAS004 | Authentication Security | Security | High | High | Account locked after 5 failed login attempts; IP blocked after 20 failed attempts; security team notified of suspicious activity. |
| QAS022 | Environment Consistency | Deployability | High | High | All environments use identical configuration management; environment-specific settings isolated; deployment process identical across dev/staging/prod; drift detected and reported within 1 hour. |
| QAS014 | External Service Integration | Interoperability | Medium | Medium | IdP API changes accommodated within 48 hours without service disruption; all integrations remain functional. |

**Key quality attribute observations:**

- **QAS004** introduces a direct dependency on a distributed cache (to track failed login attempt counts across stateless service instances). This cannot be deferred; it must be part of the Authentication Service design from the start.
- **QAS004** also requires a mechanism to publish security events (account locked, IP blocked) to monitoring and notification channels, establishing the need for the Message Broker from this iteration.
- **QAS022** requires that the deployment and configuration strategy be defined now. Infrastructure-as-code, environment variable management, and container orchestration configuration must be consistent and reproducible across all environments. This affects not just this iteration but the entire project baseline.
- **QAS014** requires the integration with the IdP to be isolated behind an adapter or anti-corruption layer so that changes to the IdP's API do not propagate throughout the system.

---

### 1.4 Architectural Concerns

| ID | Concern | Category | Priority | Relevance to Iteration 1 |
|----|---------|----------|----------|--------------------------|
| C002.1.1 | Third-party service failure handling | Integration | High | The IdP is a critical external dependency. Authentication flows must degrade gracefully if the IdP is unavailable. |
| C002.2.1 | API versioning strategy | Integration | High | All APIs exposed through the API Gateway must adopt a versioning scheme from the outset. Must be decided in this iteration. |
| C003.1.1 | Encryption standards | Security | High | Data in transit must use TLS 1.2+. Sensitive data at rest (user profile data) must be encrypted. Key management strategy must be defined. |
| C003.1.2 | Key management | Security | High | Encryption keys and secrets (JWT signing keys, API credentials for IdP) must be managed using a secrets management solution. Must not be stored in source code or environment variables in plain text. |
| C003.2.1 | RBAC implementation | Security | High | User roles (ATTENDEE, ORGANIZER, ADMIN) must be established from the first iteration. JWT tokens must carry role claims. The API Gateway must enforce coarse-grained authorisation; services enforce fine-grained authorisation. |
| C003.2.4 | Session management | Security | High | JWT tokens must have defined expiry. Refresh token rotation must be implemented. On password reset (US004), all tokens for the user must be invalidated. |
| C003.3.1 | GDPR compliance | Compliance | High | Personal data (name, email, phone) must be collected only with consent. Users must be able to request deletion. Data processing purposes must be documented. Consent mechanism must be present at registration. |
| C003.3.2 | Data residency | Compliance | High | User personal data must be stored in a jurisdiction compliant with applicable data protection regulations. The deployment region for the User Database must be specified. |

**Key concern observations:**

- **C002.1.1** and **QAS014** together make a strong case for implementing a resilience pattern (circuit breaker or retry with backoff) in the Authentication Service's IdP adapter from day one.
- **C003.1.2** (Key management) implies a secrets management infrastructure (e.g., a vault solution) must be provisioned as part of the foundational system structure in this iteration.
- **C003.2.1** (RBAC) and **C003.2.4** (Session management) together define the JWT token structure: the token must carry role claims and a user identifier, and the system must be able to invalidate tokens by placing them on a deny-list in the distributed cache.
- **C003.3.1** (GDPR) requires that a consent flag be part of the user registration flow and that a data deletion capability be planned for the User Service even if not fully implemented in this iteration.
- **C003.3.2** (Data residency) is a deployment constraint that must be reflected in the infrastructure configuration established under QAS022.

---

### 1.5 Constraints

The following constraints from Architecture.md section 3.4 are directly applicable to or establish the boundaries for this iteration.

| ID | Constraint | Implication for Iteration 1 |
|----|-----------|------------------------------|
| CON001 | The system must be accessible via web browsers on desktop/mobile and via native iOS/Android apps. | The API Gateway must be configured to serve both web and mobile clients from this iteration. CORS policies must be set. |
| CON002 | The architecture must be based on microservices; monolithic deployment is not permitted. | Even in this first iteration, the Authentication Service and User Service must be independently deployable units. |
| CON003 | User authentication must be delegated to an external IdP. The system must not store raw passwords. | The Authentication Service must never handle or persist credential material. It communicates with the IdP only via its official API. |
| CON005 | The system must comply with GDPR for all personal data. | User profile data collected at registration (name, email) falls under GDPR. Consent collection and the right to erasure must be addressed in the User Service design. |
| CON006 | All APIs must be versioned and exposed through an API Gateway. | The API Gateway is a mandatory component from iteration 1. All service endpoints must be prefixed with a version identifier (e.g., `/api/v1/`). |
| CON008 | All public APIs must enforce authentication via JWT tokens issued by the Identity Provider. | The API Gateway must validate JWT signatures on every authenticated request. The Authentication Service establishes the JWT structure used by all other services. |

---

### 1.6 Input Review Summary and Key Observations

Having reviewed all inputs, the following observations are recorded before proceeding to Step 2. These inform driver selection and design choices in subsequent steps.

| # | Observation | Impact |
|---|-------------|--------|
| 1 | **Foundational infrastructure must be established.** The API Gateway, distributed cache, message broker, and secrets management infrastructure are all introduced or implied in this iteration. Deferring them would block all subsequent iterations. | High — these components must be part of the iteration 1 design scope even though they are not explicitly called out in the iteration goal. |
| 2 | **The IdP integration is the critical path.** All four user stories depend on the external IdP. The IdP adapter design (including failure handling per C002.1.1 and versioning per QAS014) is the most technically risky element of this iteration. | High — failure handling and adapter isolation must be explicitly designed. |
| 3 | **JWT token lifecycle drives the cache design.** QAS004 (brute force protection), C003.2.4 (session management), and US004 (password reset with session invalidation) all require a distributed cache capable of storing token deny-lists and login attempt counters. | High — the cache must be provisioned and its usage patterns defined in this iteration. |
| 4 | **RBAC must be fully defined now.** The role model (ATTENDEE, ORGANIZER, ADMIN) feeds into the JWT token structure, the API Gateway authorisation policies, and every service's permission enforcement. Changing the role model later would be expensive. | High — role definitions and claim structure must be finalised in this iteration. |
| 5 | **GDPR concerns must be designed in, not bolted on.** C003.3.1 and C003.3.2 affect the user registration flow (consent) and the User Service data model (deletion capability, data residency). | Medium — a consent flag must be part of the registration flow; a data deletion endpoint must be planned even if deferred in implementation. |
| 6 | **QAS022 (Environment Consistency) is a cross-cutting concern.** Its scope extends beyond the IAM bounded context to the entire deployment infrastructure. Its design outputs in this iteration will serve as the template for all future iterations. | High — the environment configuration strategy must be documented and applied to all containers introduced in iteration 1. |

---

*Step 1 complete.*

---

## Step 2: Establish Iteration Goal by Selecting Drivers

The purpose of this step is to confirm the iteration goal and select the specific drivers — from the full list reviewed in Step 1 — that will be directly addressed by the design work in this iteration. Drivers are ranked by their architectural significance: the degree to which they constrain structural decisions, introduce technical risk, or affect elements that other drivers depend upon.

---

### 2.1 Confirmed Iteration Goal

> **Establish the foundational system structure of the Event Ticket Booking System and design the Identity and Access (IAM) bounded context to support user registration, email verification, login, and password reset via the external Identity Provider.**

This goal has two inseparable parts:

1. **Foundational structure:** The API Gateway, distributed cache, message broker, and secrets management infrastructure must all be defined in this iteration. They are prerequisite dependencies for this iteration's functional drivers and for every subsequent iteration. They were not explicitly listed in the Iteration Plan but were surfaced as mandatory in Step 1.

2. **IAM bounded context design:** The Authentication Service and User Service must be designed in sufficient detail to satisfy US001–US004, QAS004, and the security and compliance concerns, including the JWT token structure and RBAC model that every other service in the system will consume.

---

### 2.2 Selected Drivers

Drivers are classified into three tiers based on their architectural significance for this iteration.

#### Tier 1 — Primary Architectural Drivers

These drivers have the greatest influence on structural decisions. Getting them wrong would require rework that crosses multiple services and iterations.

| Driver | Type | Rationale for Tier 1 |
|--------|------|----------------------|
| **CON002** — Microservices architecture | Constraint | Mandates independently deployable services. Shapes every structural decision in this and all future iterations. |
| **CON003** — External IdP, no raw passwords | Constraint | Defines the entire authentication architecture. All four user stories are shaped by this constraint. |
| **CON006** — Versioned APIs via API Gateway | Constraint | The API Gateway is introduced in this iteration and is the single entry point for all future work. Its routing, versioning, and security configuration must be correct from the start. |
| **CON008** — JWT-based authentication for all APIs | Constraint | Establishes the token model. The JWT claim structure (subject, roles, expiry) decided here will be consumed by every microservice in every future iteration. |
| **QAS004** — Authentication Security | QAS | Introduces the brute-force protection mechanism and requires both the distributed cache (attempt counters, token deny-lists) and the message broker (security event publishing). These are foundational infrastructure components. |
| **C003.2.1** — RBAC implementation | Concern | The role model (ATTENDEE, ORGANIZER, ADMIN) and how roles are embedded in JWT claims must be finalised now. All future service-level authorisation logic depends on this decision. |
| **C003.2.4** — Session management | Concern | Defines JWT access token TTL, refresh token rotation strategy, and the token invalidation mechanism (deny-list in cache). Required by US003 and US004. |

#### Tier 2 — Key Functional Drivers

These drivers define the concrete behaviour the system must exhibit after this iteration. They are implemented using the structural foundations set by Tier 1.

| Driver | Type | Rationale for Tier 2 |
|--------|------|----------------------|
| **US001** — User Registration | User Story | First user-facing flow; establishes the registration contract between client, Authentication Service, IdP, and User Service. |
| **US002** — Email Verification | User Story | Immediately follows US001; must be designed together with it. Introduces the token validation pattern through the IdP. |
| **US003** — User Login | User Story | Most complex flow; establishes the JWT issuance path, cache lookup for brute-force counters, and user profile retrieval. |
| **US004** — Password Reset | User Story | Introduces the session invalidation sub-flow (token deny-listing in the distributed cache). Requires coordinated state change across Authentication Service and User Service. |
| **QAS022** — Environment Consistency | QAS | Cross-cutting deployability requirement. The containerisation and configuration management strategy defined here becomes the template for all containers across all iterations. |
| **QAS014** — External Service Integration | QAS | Shapes the design of the IdP adapter. Drives the decision to isolate the IdP integration behind an anti-corruption layer with resilience patterns. |

#### Tier 3 — Supporting Concerns

These concerns must be satisfied but their design follows naturally once Tier 1 and Tier 2 decisions are in place. They impose specific requirements on how Tier 1 and Tier 2 elements are implemented.

| Driver | Type | Key Design Requirement |
|--------|------|------------------------|
| **C002.1.1** — Third-party service failure handling | Concern | The IdP adapter must implement a circuit breaker or retry-with-backoff pattern. The system must return a graceful error (503) when the IdP is unavailable rather than hanging or crashing. |
| **C002.2.1** — API versioning strategy | Concern | A URI versioning scheme (`/api/v1/`) must be adopted at the API Gateway from this iteration. The strategy (URI vs header) must be decided and documented as a design decision. |
| **C003.1.1** — Encryption standards | Concern | All external communication uses TLS 1.2+. User profile data at rest must be encrypted. The standard (AES-256) must be documented. |
| **C003.1.2** — Key management | Concern | JWT signing keys and IdP API credentials must be stored in a secrets manager, not in environment variable files or source code. The secrets management component is introduced as foundational infrastructure. |
| **C003.3.1** — GDPR compliance | Concern | A consent flag must be included in the user registration payload. The User Service data model must include a `consentGiven` field and a `deletionRequestedAt` field to support the right to erasure. |
| **C003.3.2** — Data residency | Concern | The User Database must be deployed in a jurisdiction compliant with applicable data protection law. This must be reflected in the infrastructure configuration defined under QAS022. |

---

### 2.3 Drivers Not Selected for This Iteration

The following drivers from the full requirements set were reviewed but are **deferred** to later iterations. They are not within scope for the design work in iteration 1.

| Driver | Reason for Deferral |
|--------|---------------------|
| QAS001, QAS006, QAS007, QAS008 | Relate to inventory, order, and payment flows addressed in iterations 3 and 4. |
| QAS002, QAS005 | Relate to event management and search, addressed in iteration 2. |
| QAS003, QAS013 | Relate to payment processing, addressed in iteration 4. |
| QAS015, QAS021, QAS023–QAS025 | Availability, zero-downtime deployment, and feature flag management — cross-cutting operational concerns that build on the foundational infrastructure defined here but are not primary design targets for iteration 1. |
| C001.x | Data lifecycle management concerns applicable once data is flowing through the system in later iterations. |
| C004.1.x, C004.2.x, C004.3.x | Observability, disaster recovery, and capacity planning; addressed as the system matures across iterations. |
| US005–US023 | Belong to iterations 2, 3, and 4. |

---

### 2.4 Iteration Goal Refined

Having selected and tiered the drivers, the iteration goal is refined as follows:

> **Design the foundational system structure of the Event Ticket Booking System — including the API Gateway, distributed cache, message broker, and secrets management infrastructure — and design the IAM bounded context (Authentication Service and User Service) to support user registration, email verification, login, and password reset via the external Identity Provider, with JWT-based authentication, RBAC, session management, brute-force protection, and GDPR-compliant user profile management.**

The outputs of this iteration are:
- A component diagram for the Authentication Service and User Service.
- Sequence diagrams for US001, US002, US003, US004, QAS004, QAS014, and QAS022.
- A JWT claim structure specification.
- An RBAC model and policy definition.
- Design decisions recorded for all Tier 1 choices.
- Updated container diagram in Architecture.md reflecting the infrastructure components introduced.

---

*Step 2 complete.*

---

## Step 3: Choose One or More Elements of the System to Refine

The purpose of this step is to decide which elements of the current architecture will be designed in detail during this iteration. For a greenfield system, "refining an element" means decomposing a container (C4 level 2) into its internal components (C4 level 3) and specifying the responsibilities, interfaces, and relationships of those components.

The selection is driven by the Tier 1 and Tier 2 drivers identified in Step 2 and by the principle of refining only what is needed to address the current iteration's goal.

---

### 3.1 Current State of the Architecture

At the start of this iteration, the architecture document contains:

- A **context diagram** (C4 level 1) — complete.
- A **domain model** with eight bounded contexts — complete.
- A **container diagram** (C4 level 2) skeleton — containers are named and their responsibilities described, but the diagram reflects the full future system. The containers relevant to this iteration have not yet been confirmed as correct or detailed.
- **Component diagrams** (C4 level 3) — all empty; none have been designed yet.
- **Sequence diagrams** — all empty placeholders.
- **Design decisions** — table present but empty.

The elements that exist at container level and are relevant to this iteration are:

| Container | Iteration 1 relevance |
|-----------|----------------------|
| API Gateway | Entry point for all flows; must be configured for JWT validation, routing, versioning, and rate limiting. |
| Authentication Service | Orchestrates all four user stories; most complex service in this iteration. |
| User Service | Manages user profile data; supports registration, email verification, and GDPR compliance. |
| Distributed Cache | Required by QAS004 (attempt counters, token deny-list) and US004 (session invalidation). |
| Message Broker | Required by QAS004 (publishing security events: account locked, IP blocked). |
| Secrets Manager | Required by C003.1.2 (key management for JWT signing keys and IdP credentials). |
| User Database | Persistent store for user profiles. |

The following containers are **not** touched in this iteration and are left unchanged:

Event Service, Inventory Service, Order Service, Payment Service, Ticket Service, Notification Service, Search Service, and all databases except the User Database.

---

### 3.2 Elements Selected for Refinement

Four elements are selected for refinement in this iteration. Each is described with its current state, the design questions that must be resolved, and the expected output of the refinement.

---

#### Element 1: Overall System Structure (Container View — Iteration 1 Subset)

**Current state:** The container diagram in Architecture.md covers the full future system. It does not yet distinguish which containers are introduced in which iteration, and some iteration-1-specific configuration details (JWT validation at the gateway, CORS, versioning scheme) are not yet present.

**What will be refined:**
- Confirm and document the exact set of containers introduced in iteration 1.
- Specify the communication paths between them (synchronous REST vs asynchronous via message broker).
- Annotate the API Gateway with its iteration-1-specific responsibilities (JWT validation, URI versioning, CORS, rate limiting).

**Design questions to resolve:**
- Which communication between Auth Service and User Service is synchronous (registration profile creation) vs asynchronous (event publishing)?
- Should the Auth Service and User Service share the User Database (schema-level separation) or use separate databases?
- How does the API Gateway validate JWT tokens — locally (using the IdP's public key cached from a JWKS endpoint) or by calling the Auth Service on every request?

**Expected output:** Updated container diagram in Architecture.md (iteration 1 scope annotated); container responsibility table updated.

---

#### Element 2: Authentication Service (Component Decomposition)

**Current state:** The Authentication Service exists as a named container with a brief responsibility description. Its internal design is entirely undefined.

**What will be refined:**
Decompose the Authentication Service into its internal components. Based on the drivers, the following components are anticipated (to be confirmed in Step 4):

| Anticipated Component | Driving Concern |
|-----------------------|----------------|
| AuthController | Exposes REST endpoints for US001–US004 |
| IdPAdapter | Wraps all calls to the external IdP; isolates the system from IdP API changes (QAS014) |
| CircuitBreaker / ResiliencePolicy | Wraps IdP calls to handle IdP unavailability (C002.1.1) |
| BruteForceGuard | Tracks and enforces login attempt limits using the distributed cache (QAS004) |
| TokenService | Manages JWT issuance, validation, and deny-listing for token invalidation (C003.2.4) |
| SecurityEventPublisher | Publishes AccountLocked and FailedLoginAttempt events to the message broker (QAS004) |

**Design questions to resolve:**
- Should the circuit breaker be a component inside the Auth Service or a cross-cutting infrastructure pattern (sidecar/proxy)?
- How is the token deny-list structured in the cache (key: token JTI, value: expiry timestamp)?
- Should JWT tokens be issued by the Auth Service itself (signing with a private key) or fetched from the IdP? The answer affects key management.

**Expected output:** Component diagram for the Authentication Service in Architecture.md section 6; component responsibility table.

---

#### Element 3: User Service (Component Decomposition)

**Current state:** The User Service exists as a named container. Its internal design is undefined.

**What will be refined:**
Decompose the User Service into its internal components. Based on the drivers, the following components are anticipated:

| Anticipated Component | Driving Concern |
|-----------------------|----------------|
| UserController | Exposes REST endpoints for profile retrieval and management |
| UserProfileRepository | Persistence layer for user profile data; wraps the User Database |
| GDPRComplianceHandler | Manages consent recording, data deletion requests, and data subject access (C003.3.1) |
| UserEventConsumer | Subscribes to domain events from the message broker (e.g., UserRegistered) |

**Design questions to resolve:**
- Does the User Service own the user's role assignments, or does the Auth Service hold roles as part of the identity? (Affects JWT claim population.)
- How is the `consentGiven` field enforced at registration — does the User Service reject profile creation if consent is absent, or is that validated at the API Gateway?
- What is the data deletion strategy: hard delete or soft delete with a `deletedAt` timestamp? (Impacts GDPR compliance and audit logging.)

**Expected output:** Component diagram for the User Service in Architecture.md section 6; component responsibility table.

---

#### Element 4: API Gateway (Configuration Specification)

**Current state:** The API Gateway container is defined with a brief responsibility summary. No routing rules, JWT validation strategy, versioning scheme, or rate limiting policy have been specified.

**What will be refined:**
The API Gateway does not have an internal component decomposition (it is a managed infrastructure component, not a custom service), but its **configuration responsibilities** must be specified as part of the architecture:

| Configuration Concern | Driving Concern |
|-----------------------|----------------|
| URI versioning scheme (`/api/v1/`) | C002.2.1, CON006 |
| JWT signature validation (JWKS endpoint caching) | CON008 |
| CORS policy (allowed origins for web and mobile clients) | CON001 |
| Rate limiting per client IP | QAS004 |
| Request routing rules (path → service mapping) | CON006 |
| TLS termination | C003.1.1 |

**Design questions to resolve:**
- URI versioning vs header-based versioning: which approach?
- Should the gateway perform JWT validation directly (using the IdP's JWKS public key) or delegate to the Auth Service? The former is faster and reduces inter-service coupling; the latter allows centralised deny-list checking.
- How are rate limits configured: per IP, per user, per endpoint, or a combination?

**Expected output:** API Gateway configuration specification added to Architecture.md section 6 (as a configuration note within the component diagrams section); design decisions recorded for versioning strategy and JWT validation approach.

---

### 3.3 Elements Explicitly Not Refined in This Iteration

The following containers are introduced as infrastructure in this iteration but are **not** decomposed at component level, as they are provisioned managed services whose internal design is not within scope:

| Container | Treatment in This Iteration |
|-----------|----------------------------|
| Distributed Cache | Provisioned as a managed Redis-compatible service. Usage patterns defined (attempt counters, token deny-list). No component decomposition. |
| Message Broker | Provisioned as a managed message broker. Topic/queue names and message schemas defined for security events. No component decomposition. |
| Secrets Manager | Provisioned as a managed secrets management service. Secret naming conventions and access policies defined. No component decomposition. |
| User Database | Provisioned as a managed relational database. Schema defined through the domain model (User, UserProfile entities). No component decomposition. |

---

### 3.4 Refinement Summary

| Element | C4 Level | Refinement Type | Iteration Output |
|---------|----------|-----------------|-----------------|
| Overall system structure (iteration 1 subset) | Level 2 (Container) | Update and annotate existing container diagram | Updated container diagram in Architecture.md |
| Authentication Service | Level 3 (Component) | Full component decomposition | Component diagram + responsibility table in Architecture.md §6 |
| User Service | Level 3 (Component) | Full component decomposition | Component diagram + responsibility table in Architecture.md §6 |
| API Gateway | Level 2 / Config | Configuration specification | Configuration note in Architecture.md §6 |

---

*Step 3 complete. Awaiting review before proceeding to Step 4: Choose one or more design concepts that satisfy the selected drivers.*
