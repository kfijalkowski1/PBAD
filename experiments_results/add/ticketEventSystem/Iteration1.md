# Iteration 1 — Establish Overall System Structure and Deployment Model

**ADD Process:** Attribute-Driven Design 3.0  
**Iteration Goal:** Establish the overall system structure and deployment model for the Hotel Pricing System.  
**Status:** Step 1 — Complete. Awaiting review.

---

## Step 1: Review Inputs

The purpose of this step is to thoroughly examine all inputs available before any design decision is taken. Reviewing inputs prevents premature design choices, surfaces conflicts or gaps that must be resolved before the iteration can proceed, and ensures that the design work is grounded in the correct understanding of the system's requirements.

---

### 1.1 Design Purpose

This is a **greenfield initial design** effort for the replacement of AD&D Hotels' existing Hotel Pricing System. No prior architecture exists for the new system; the architecture is being produced from scratch using Attribute-Driven Design.

The overall design purpose is to produce a **scalable, reliable, highly available, and maintainable microservices-based architecture** for the Hotel Pricing System that satisfies all architectural drivers identified in `ArchitecturalDrivers.md`. The system must replace an existing pricing platform that is suffering from reliability, performance, and maintainability issues, and it must be delivered within a 6-month timeline with an MVP in 2 months (CON-4).

This first iteration serves a dual purpose:

1. **Establish the foundational structure** of the overall system — the deployment topology, cloud hosting model, inter-service communication patterns, container orchestration approach, continuous deployment infrastructure, and environment management strategy that all subsequent iterations will build upon.
2. **Confirm the overall container architecture** derived from the domain model, establishing which microservices exist, what their deployment boundaries are, and how they are organised in a cloud-native runtime.

Because this iteration lays the skeleton on which all future iterations depend, the decisions taken here carry the highest structural risk. They must be made carefully and documented as reusable standards for the entire project.

---

### 1.2 Primary Functionality

The drivers for this iteration are structural and infrastructure-oriented. No user story is assigned as a primary functional driver for Iteration 1. However, the following observations are relevant:

- The domain model in `DomainModel.md` has identified **six bounded contexts** (Price Management, Hotel Management, Rate Management, User Authorization, Price Query, Channel Distribution), each mapping to one or more microservices. This iteration confirms and locks in those service boundaries as the target container architecture.
- The container skeleton established in `Architecture.md` (section 5) lists the microservices, databases, message broker, and monitoring infrastructure. This iteration validates and refines that skeleton by assigning deployment responsibilities and environment management rules.
- No functional user stories are implemented in this iteration. The outputs are structural: deployment topology, CI/CD pipeline, cloud configuration, and environment management guidelines that all future iterations depend upon.

---

### 1.3 Quality Attribute Scenarios

Only the quality attribute scenarios that are **directly applicable** to the structural and deployment goals of this iteration are reviewed here.

| ID | Quality Attribute | Scenario | Priority | Relevance to Iteration 1 |
|----|-----------------|----------|----------|--------------------------|
| QA-7 | Deployability | The application is moved between non-production environments as part of the development process. No changes in the code are needed. | Medium | **Primary.** This scenario directly defines the requirement for environment-independent configuration. The system must achieve this through externalised configuration (e.g., environment variables, config maps) so that the same container image is deployed unchanged across Development, Integration, Staging, and Production. The entire environment management strategy is motivated by this scenario. |
| QA-3 | Availability | Pricing queries uptime SLA must be 99.9% outside of maintenance windows. | High | **Indirect.** The cloud-native deployment model and the container orchestration platform chosen in this iteration must support the infrastructure capabilities (auto-restart, health checks, rolling updates) that will be needed to satisfy QA-3 in Iteration 3. The deployment model must not preclude them. |
| QA-4 | Scalability | The system must handle up to 1,000,000 price queries/day without degrading average latency by more than 20%. | High | **Indirect.** The orchestration platform and deployment model must support horizontal scaling of individual microservices. The choice of managed cloud services (databases, message broker) must be compatible with the scaling requirements addressed in later iterations. |
| QA-8 | Monitorability | 100% of performance and reliability measures must be collectible. | Medium | **Indirect.** The deployment platform must support centralised logging, metrics collection, and distributed tracing infrastructure. This iteration introduces the Monitoring & Observability container; its provisioning is part of the foundational structure. |
| QA-9 | Testability | 100% of the system and its elements should support integration testing independently of external systems. | Medium | **Indirect.** The CI/CD pipeline established in this iteration must include an Integration environment where external systems (Cloud Identity Service, CMS, PMS, CAS) are substituted by mocks or stubs, satisfying QA-9 at the pipeline level. |

**Quality attribute scenarios not applicable to this iteration:** QA-1 (Performance — price publication), QA-2 (Reliability — price delivery), QA-5 (Security — authentication and authorization), QA-6 (Modifiability — new protocol endpoint). These are deferred to the iterations that design the respective functional capabilities.

---

### 1.4 Architectural Concerns

| ID | Concern | Priority | Relevance to Iteration 1 |
|----|---------|----------|--------------------------|
| CRN-1 | Establish an overall initial system structure. | — | **Primary.** The explicit goal of this iteration. The container diagram in `Architecture.md` provides the starting point; this iteration refines it into a deployable, cloud-native model with confirmed service boundaries. |
| CRN-2 | Leverage the team's knowledge about Java technologies and the Angular framework. | — | **Direct.** The technology choices for microservices (Java/Spring Boot) and the frontend (Angular SPA) must be confirmed and documented in this iteration, as they will inform team allocation (CRN-3) and build tooling in the CI/CD pipeline (CRN-5). |
| CRN-3 | Allocate work to members of the development team. | — | **Direct.** One of the outputs of this iteration is a clear service boundary map. This map enables work allocation: each microservice (bounded context) can be owned by a sub-team independently. The service boundaries must be stable enough after this iteration for parallel development to begin. |
| CRN-4 | Avoid introducing technical debt. | — | **Indirect.** The cloud-native patterns, CI/CD pipeline, and testing strategy established here must be done correctly from the start. Technical shortcuts in infrastructure setup (e.g., hardcoded configuration, manual deployments) create debt that accumulates rapidly. This concern reinforces the quality standards for the iteration outputs. |
| CRN-5 | Set up a continuous deployment infrastructure. | — | **Primary.** The CI/CD pipeline must be designed and its structure documented in this iteration. The pipeline covers all four environments (Development, Integration, Staging, Production) and includes build, test, image push, and deployment stages, as described in `ArchitecturalDrivers.md`. |

---

### 1.5 Constraints

All constraints are relevant to this iteration, as they collectively define the non-negotiable boundaries within which the foundational architecture must be established.

| ID | Constraint | Implication for Iteration 1 |
|----|-----------|------------------------------|
| CON-1 | Users must interact through a web browser on Windows, OSX, Linux, and different devices. | The Web Application (Angular SPA) must be confirmed as a container in the architecture. Its deployment as a statically served, browser-based application (CDN or web server) must be addressed. CORS policies between the frontend and the API Gateway must be established. |
| CON-2 | Manage users through cloud provider identity service and host resources in the cloud. | Two implications: (1) The cloud identity service integration must be reflected in the container diagram — the User Authorization Service delegates authentication to an external cloud identity service. (2) All infrastructure (microservices, databases, message broker, monitoring) must be hosted on a cloud provider. This iteration must identify the cloud hosting model (e.g., managed Kubernetes, PaaS services). |
| CON-3 | Code must be hosted on a proprietary Git-based platform already in use by the company. | The CI/CD pipeline (CRN-5) must integrate with the existing Git platform. Pipeline definitions (e.g., pipeline-as-code files) must live in the same repositories. |
| CON-4 | MVP in 2 months; full release in 6 months. | The overall system structure and CI/CD pipeline must be operational from the end of Iteration 1, enabling Iteration 2 (core pricing — the MVP scope) to proceed without structural rework. This constraint imposes urgency on the outputs of this iteration. |
| CON-5 | The system must interact with existing systems through REST APIs initially, with potential for other protocols later. | The Channel Distribution Service and the API Gateway must be designed with adapter isolation so that protocols can be swapped or added. This is a structural principle established now; the implementation is addressed in later iterations. |
| CON-6 | A cloud-native approach should be favored. | Containers (Docker), container orchestration (Kubernetes or equivalent), managed cloud services (databases, message broker, monitoring), infrastructure-as-code, and declarative configuration are all implied. This iteration defines the cloud-native deployment model and must document it as the architectural baseline. |

---

### 1.6 Input Review Summary and Key Observations

Having reviewed all inputs, the following observations are recorded before proceeding to Step 2. These directly inform driver selection and design choices in subsequent steps.

| # | Observation | Impact |
|---|-------------|--------|
| 1 | **The domain model already defines the service boundary map.** The six bounded contexts from `DomainModel.md` translate directly into six microservices plus the API Gateway, Message Broker, and infrastructure services. This iteration confirms those boundaries and assigns deployment ownership — no new services are invented. | High — the bounded context decomposition is the primary input for the container architecture. |
| 2 | **QA-7 (Deployability) mandates externalised configuration as a design principle.** The requirement that the same artifact moves between environments without code changes is a strict constraint on how configuration is managed. Environment-specific values (connection strings, service endpoints, credentials) must be injected at deployment time via environment variables or a configuration service — never baked into the image. | High — this principle must be established as a mandatory standard in the CI/CD pipeline and documented as a design decision. |
| 3 | **CON-4 (MVP in 2 months) creates a hard dependency on this iteration.** Iterations 1 and 2 together must deliver the MVP. This means the system structure, cloud infrastructure, and CI/CD pipeline established in Iteration 1 must be functional and ready for Iteration 2 to build upon without structural rework. | High — the outputs of this iteration are on the critical path to the MVP. Any ambiguity or incompleteness here delays Iteration 2. |
| 4 | **CON-2 requires cloud hosting for all resources.** The entire infrastructure stack — microservices, databases, message broker, monitoring — must run on a cloud provider. This rules out on-premises hosting and mandates cloud-native managed services wherever possible. The cloud provider must be selected or confirmed as part of this iteration. | High — every container in the container diagram must have a confirmed cloud deployment target. |
| 5 | **CRN-3 (Work allocation) is enabled by confirming service boundaries.** Once the microservice map is stable after this iteration, sub-teams can be assigned to individual services (Price Management, Hotel Management, Rate Management, User Authorization, Price Query, Channel Distribution) and develop them in parallel. The service boundaries must not change substantially after this iteration without architectural review. | High — stable service boundaries are the prerequisite for parallel development. |
| 6 | **CRN-5 (CI/CD infrastructure) introduces a cross-cutting design scope.** The CI/CD pipeline is not a microservice; it is the delivery mechanism for every container in the system. It must cover all four environments (Development, Integration, Staging, Production) and enforce quality gates (build, unit test, integration test, deployment). Designing the pipeline is a distinct design activity with its own outputs. | High — the pipeline must be documented as an architectural element, not treated as an implementation detail. |
| 7 | **The Monitoring & Observability container is foundational, not optional.** QA-8 (Monitorability) requires 100% measure collectibility. This cannot be retrofitted after all services are built; the monitoring infrastructure (metrics collection, centralised logging, distributed tracing) must be provisioned from the start so that each service can emit telemetry as it is developed. | Medium — the monitoring container must be provisioned in Iteration 1, even though QA-8 is addressed in detail in Iteration 6. |
| 8 | **Technology choices (Java/Spring Boot, Angular) must be confirmed here.** CRN-2 (team expertise) and CRN-3 (work allocation) together require that the technology stack be documented as part of the foundational structure. Build pipelines, Docker base images, and development tooling all depend on this confirmation. | Medium — technology confirmation is an output of this iteration; changes after this point carry significant rework cost. |

---

*Step 1 complete.*

---

## Step 2: Establish Iteration Goal by Selecting Drivers

The purpose of this step is to confirm the iteration goal and select the specific drivers — from the full set reviewed in Step 1 — that will be directly addressed by design work in this iteration. Drivers are ranked by their architectural significance: the degree to which they constrain structural decisions, introduce technical risk, or affect elements that other drivers and other iterations depend upon.

---

### 2.1 Confirmed Iteration Goal

> **Establish the foundational system structure of the Hotel Pricing System — confirming the microservice container map derived from the domain model, defining the cloud-native deployment model, and designing the continuous deployment infrastructure — so that all subsequent iterations can develop and deploy individual microservices independently without structural rework.**

This goal has three inseparable parts:

1. **Container architecture confirmation.** The six bounded contexts from `DomainModel.md` are translated into a confirmed, deployment-ready set of microservice containers, with hosting responsibilities, communication patterns, and database ownership explicitly assigned. No future iteration should need to revise this structural map.

2. **Cloud-native deployment model.** The platform for running those containers (container orchestration, managed cloud services, network topology) must be selected and documented. Every subsequent iteration deploys to this platform, so it must support the quality attributes already identified — particularly QA-3 (availability), QA-4 (scalability), and QA-7 (deployability without code changes).

3. **Continuous deployment infrastructure.** The CI/CD pipeline, its stages, and its environment promotion strategy must be designed. The four-environment model (Development, Integration, Staging, Production) described in `ArchitecturalDrivers.md` must be realized in the pipeline structure. This is the mechanism by which QA-7 is satisfied at the pipeline level.

---

### 2.2 Driver Selection and Tiering

Drivers are classified into three tiers based on their architectural significance for this iteration. Tier 1 drivers have the greatest structural influence; getting them wrong requires costly rework across multiple services and iterations.

#### Tier 1 — Primary Architectural Drivers

These drivers directly shape the structural decisions of this iteration. Every design concept chosen in Step 4 must satisfy all Tier 1 drivers.

| Driver | Type | Rationale for Tier 1 |
|--------|------|----------------------|
| **CRN-1** — Establish overall initial system structure | Concern | The explicit goal of this iteration. Defines the container map that all future iterations build upon. The highest-priority output of the iteration. |
| **CON-6** — Cloud-native approach | Constraint | Non-negotiable. Mandates containerisation, cloud orchestration, and managed cloud services. All deployment decisions must conform to cloud-native principles. |
| **CON-2** — Cloud hosting and identity service | Constraint | Dual implication: (1) all infrastructure must run on a cloud provider; (2) user management and authentication must delegate to the cloud provider's identity service. Both shape the container topology and the User Authorization Service design. |
| **CRN-5** — Continuous deployment infrastructure | Concern | The CI/CD pipeline is on the critical path to the MVP (CON-4). Without it, no other iteration can deliver and validate its outputs across environments. It must be designed in this iteration. |
| **QA-7** — Deployability | QAS | The only quality attribute scenario directly targeted in this iteration. Its measurable requirement — no code changes when moving between environments — mandates a specific configuration externalisation strategy that must be defined now and enforced for every container in every future iteration. |

#### Tier 2 — Key Supporting Drivers

These drivers are directly satisfied by implementing the Tier 1 decisions correctly. They impose specific requirements on *how* the Tier 1 elements are designed.

| Driver | Type | Rationale for Tier 2 |
|--------|------|----------------------|
| **CRN-2** — Leverage Java and Angular expertise | Concern | Technology choices (Java/Spring Boot for microservices, Angular for the frontend) must be confirmed in this iteration because they determine the build tooling, Docker base images, and CI pipeline configuration. All subsequent iterations assume these choices. |
| **CRN-3** — Allocate work to development team | Concern | Once the container map is stable, work can be assigned: each microservice (bounded context) is owned by a sub-team. Stable boundaries are the prerequisite for parallel development starting from Iteration 2. |
| **CON-3** — Proprietary Git-based platform | Constraint | The CI/CD pipeline must integrate with the company's existing Git platform. Pipeline-as-code files must be stored in the same repositories as the service source code. This shapes the pipeline tooling choices. |
| **CON-4** — MVP in 2 months, full release in 6 months | Constraint | Iterations 1 and 2 together deliver the MVP. This iteration must be completed so that Iteration 2 can begin immediately. The deployment infrastructure must be production-ready from the start — no throwaway scaffolding. |

#### Tier 3 — Indirectly Addressed Concerns

These drivers are not the primary focus of this iteration but impose constraints on design choices made here. Decisions taken in this iteration must not preclude their satisfaction in later iterations.

| Driver | Type | Key Constraint on This Iteration |
|--------|------|----------------------------------|
| **QA-3** — Availability (99.9% query uptime) | QAS | The orchestration platform must support auto-healing (pod/instance restart), health checks, and rolling deployments. These capabilities must be available in the platform chosen now. |
| **QA-4** — Scalability (up to 1M queries/day) | QAS | The platform must support horizontal autoscaling of individual microservices independently. A platform that only scales the whole system uniformly is insufficient. |
| **QA-8** — Monitorability | QAS | The Monitoring & Observability infrastructure must be provisioned in this iteration. Services built in subsequent iterations must be able to emit metrics and logs from day one. |
| **QA-9** — Testability | QAS | The CI/CD pipeline must include an Integration environment where external systems (Cloud Identity Service, CMS, PMS, CAS) are replaced by test doubles. This must be a design output of the pipeline specification. |
| **CON-5** — REST initially, other protocols later | Constraint | The API Gateway and Channel Distribution Service designs must use the adapter pattern so that protocol choices are not hardcoded. The principle must be established now; implementation is deferred. |
| **CRN-4** — Avoid technical debt | Concern | All infrastructure setup in this iteration — pipeline, configuration management, monitoring — must be done properly, not as throwaway scaffolding. The standards established here become the baseline for the whole project. |

---

### 2.3 Drivers Not Selected for This Iteration

The following drivers from the full requirements set were reviewed but are **deferred** to later iterations. They are outside the scope of design work in Iteration 1.

| Driver | Deferred To | Reason |
|--------|-------------|--------|
| HPS-2 (Change Prices), QA-1, QA-2 | Iteration 2 | Core pricing functionality; depends on the infrastructure established here. |
| HPS-3 (Query Prices), QA-3, QA-4 | Iteration 3 | Query and scalability design; depends on containers established here. |
| HPS-4 (Manage Hotels), HPS-5 (Manage Rates) | Iteration 4 | Hotel and rate management; independent bounded contexts. |
| HPS-1 (Log In), HPS-6 (Manage Users), QA-5 | Iteration 5 | Security and user management; the identity service integration confirmed here is a prerequisite, but the detailed authentication/authorization design is deferred. |
| QA-6, QA-8, QA-9, CRN-4 | Iteration 6 | Modifiability, monitoring detail, testability detail, and technical debt review. Foundations are laid here but detailed design is deferred. |

---

### 2.4 Refined Iteration Goal

Having selected and tiered the drivers, the iteration goal is refined as follows:

> **Design the foundational system structure of the Hotel Pricing System by: (1) confirming and documenting the complete microservice container map derived from the domain model, with cloud hosting assignments, database ownership, and communication patterns; (2) defining the cloud-native deployment model — container orchestration, managed infrastructure services, and network topology — that satisfies QA-7 (environment-independent deployment), and supports future satisfaction of QA-3, QA-4, and QA-8; and (3) specifying the four-stage CI/CD pipeline that enables environment promotion without code changes across Development, Integration, Staging, and Production.**

The expected outputs of this iteration are:

- A confirmed and annotated container diagram in `Architecture.md` with cloud hosting assignments, technology labels, and communication patterns made explicit.
- A CI/CD pipeline specification (stages, environment strategy, quality gates) recorded in this document.
- Design decisions recorded in `Architecture.md` section 9 for all Tier 1 choices: cloud platform, orchestration, configuration management, and pipeline tooling.
- A technology confirmation record (Java/Spring Boot, Angular) as the project-wide technology baseline.

---

*Step 2 complete.*

---

## Step 3: Choose One or More Elements of the System to Refine

The purpose of this step is to decide which elements of the current architecture will be designed in detail during this iteration. "Refining an element" means taking an element that currently exists only as a name and a brief description and producing enough design detail — assignments, communication paths, configuration rules, or component decompositions — to make it actionable for developers and the next iteration.

The selection is strictly bounded by the Tier 1 and Tier 2 drivers from Step 2. Only elements that must be resolved now to satisfy those drivers — and to unblock subsequent iterations — are selected.

---

### 3.1 Current State of the Architecture

At the start of this iteration, `Architecture.md` contains the following:

| Section | Status |
|---------|--------|
| Context diagram (C4 Level 1) | Complete — external actors and systems identified. |
| Domain model (DDD) | Complete — six bounded contexts, aggregates, domain events, and cross-context integration defined. |
| Container diagram (C4 Level 2) | **Skeleton only.** Containers are named and responsibility tables are present, but no cloud hosting assignments, technology labels, communication style annotations (sync/async), database ownership rules, or deployment topology are specified. The diagram does not yet reflect the four-environment model or cloud-native operational concerns. |
| Component diagrams (C4 Level 3) | **All empty.** No container has been decomposed into internal components. |
| Sequence diagrams | **All empty placeholders.** No behaviour has been described. |
| Design decisions | **Empty table.** No decisions have been recorded. |

The domain model and the container skeleton are the two structural assets that this iteration builds upon. The container skeleton is the primary target for refinement.

---

### 3.2 Elements Selected for Refinement

Three elements are selected for refinement in this iteration. Each is described with its current state, the design questions that must be resolved, and the expected output.

---

#### Element 1: Container Architecture — Iteration 1 Confirmation and Annotation (C4 Level 2)

**Current state:** The container diagram in `Architecture.md` section 5 lists fourteen containers across six microservices, six databases, a message broker, and a monitoring system. It includes a basic Mermaid diagram and a responsibility table. However, the following are absent:

- Technology labels (which language/framework runs in each container).
- Cloud hosting assignment (which containers are custom-built vs managed cloud services).
- Communication style per edge (synchronous REST vs asynchronous event via message broker).
- Database ownership rules (which service owns which store — this is a microservices architectural invariant).
- Network topology (which containers are internet-facing, which are internal-only).

**What will be refined:**

- Confirm the complete set of containers for the target architecture and verify consistency with the six bounded contexts in the domain model.
- Assign a technology label to every container (e.g., Java 21/Spring Boot 3, Angular 17, PostgreSQL, Redis, Apache Kafka).
- Classify each container as either a **custom-built service** (developed by the team) or a **managed cloud service** (provisioned from the cloud provider).
- Annotate all communication edges with their style: synchronous (REST over HTTPS) or asynchronous (event via message broker).
- Enforce the **database-per-service** rule: each microservice owns exactly one store, and no store is shared between services.
- Distinguish **internet-facing** containers (Web Application, API Gateway) from **internal** containers (all microservices, databases, message broker).

**Design questions to resolve:**

1. Which containers are managed cloud services vs custom microservices? (e.g., Is the message broker a managed service such as Amazon MSK or a self-hosted Kafka deployment?)
2. What relational database engine is used across all service stores? (Consistency reduces operational overhead.)
3. Is the Price Read Store a relational database, a cache, or both? (The domain model identifies it as a cache/read DB; the technology choice must be confirmed.)
4. Does the Monitoring & Observability container represent a managed cloud-native service or a self-hosted stack?
5. Is the Web Application served from a CDN, a dedicated web server, or directly from the API Gateway?

**Expected output:** Updated container diagram in `Architecture.md` section 5 with technology labels, communication style annotations, and hosting classification. Updated container responsibility table.

---

#### Element 2: Deployment Environment Model (QA-7 Realisation)

**Current state:** The four-environment model (Development, Integration, Staging, Production) is described in `ArchitecturalDrivers.md` in prose. It does not yet appear anywhere in the architecture documentation as a designed element. The mechanism by which QA-7 ("no code changes between environments") is satisfied is completely unspecified.

**What will be refined:**

- Define the four environments and their purpose, infrastructure scope, and external system connectivity.
- Specify the **configuration externalisation strategy**: the mechanism by which environment-specific values (database URLs, API keys, service endpoints) are injected at deployment time without modifying the container image.
- Define which external systems are **live** vs **mocked** in each environment (relevant to QA-9 testability).
- Specify the **artifact promotion model**: the same container image tag is promoted from environment to environment; no rebuild occurs between environments.

**Design questions to resolve:**

1. Which configuration externalisation mechanism is used? (Options: environment variables only, a secrets manager for sensitive values combined with environment variables for non-sensitive values, or a dedicated configuration service.)
2. How are test doubles for external systems (Cloud Identity Service, CMS, PMS, CAS) provisioned in the Integration environment? (Container-based mocks in the same cluster, or dedicated stub services?)
3. Is there a feature flag mechanism in scope for this iteration, or is it deferred?

**Expected output:** A Deployment Environment Model section in this document (`Iteration1.md`) describing the four environments, their infrastructure, connectivity, and the configuration injection strategy that satisfies QA-7.

---

#### Element 3: CI/CD Pipeline Specification (CRN-5 Realisation)

**Current state:** The CI/CD pipeline does not yet appear anywhere in the architecture documentation. CRN-5 requires it to be designed in this iteration. The pipeline is the mechanism that enforces the artifact promotion model, runs quality gates, and enables parallel team development (CRN-3).

**What will be refined:**

- Define the **pipeline stages** (source, build, test, image push, deployment) and their trigger conditions.
- Define **quality gates** at each stage: what must pass before promotion to the next environment.
- Specify the **branching strategy** (e.g., trunk-based development, feature branches) that integrates with the pipeline.
- Specify the **pipeline-as-code** approach: pipeline definitions live in the same repository as service code, consistent with CON-3 (company Git platform).
- Identify the pipeline tool (integrated with the company's proprietary Git platform).

**Design questions to resolve:**

1. Does the company's Git platform include a built-in CI/CD system (e.g., GitLab CI, Bitbucket Pipelines, Jenkins), or is a separate tool needed?
2. Is a single mono-repository or a per-service repository strategy used? (This affects how the pipeline is triggered and how shared pipeline templates are distributed.)
3. Are container images stored in a cloud-provider container registry or a self-hosted one?

**Expected output:** A CI/CD Pipeline Specification section in this document (`Iteration1.md`) describing the stages, quality gates, branching strategy, and tooling; a pipeline stage diagram; design decisions recorded for the three pipeline choices above.

---

### 3.3 Elements Explicitly Not Refined in This Iteration

The following containers and architectural elements are **introduced** as part of the confirmed container map but are **not** decomposed at component level (C4 Level 3). Their internal design is deferred to the iteration that addresses their functional drivers.

| Container | Reason for Deferral |
|-----------|---------------------|
| Price Management Service | Internal design is driven by HPS-2, QA-1, QA-2 — Iteration 2. |
| Hotel Management Service | Internal design is driven by HPS-4 — Iteration 4. |
| Rate Management Service | Internal design is driven by HPS-5 — Iteration 4. |
| User Authorization Service | Internal design is driven by HPS-1, HPS-6, QA-5 — Iteration 5. |
| Price Query Service | Internal design is driven by HPS-3, QA-3, QA-4 — Iteration 3. |
| Channel Distribution Service | Internal design is driven by CON-5, QA-6 — Iteration 6. |
| All databases (Price Write, Price Read, Hotel, Rate, Authorization) | Schema design is deferred to the iteration that designs the owning service. |
| Message Broker | Provisioned as a managed service; topic schema design is deferred to the iteration that defines each event. |
| Monitoring & Observability | Provisioned as a managed stack; detailed dashboard and alerting design is deferred to Iteration 6 (QA-8). |

---

### 3.4 Refinement Summary

| Element | C4 Level | Refinement Type | Primary Drivers | Expected Output Location |
|---------|----------|-----------------|-----------------|--------------------------|
| Container architecture — confirmation and annotation | Level 2 | Update existing container diagram with technology labels, communication styles, hosting classification, DB ownership rules | CRN-1, CON-6, CON-2 | `Architecture.md` — section 5 |
| Deployment environment model | Cross-cutting | New design element: four-environment definition + configuration externalisation strategy | QA-7, CON-4 | `Iteration1.md` — new section |
| CI/CD pipeline specification | Cross-cutting | New design element: stages, quality gates, branching strategy, tooling | CRN-5, CON-3, CON-4 | `Iteration1.md` — new section |

---

*Step 3 complete. Awaiting review before proceeding to Step 4: Choose One or More Design Concepts that Satisfy the Selected Drivers.*
