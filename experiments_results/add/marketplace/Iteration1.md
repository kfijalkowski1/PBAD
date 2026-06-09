# Iteration 1 — ADD Design Record

**Method:** Attribute-Driven Design (ADD 3.0)
**Goal:** Establish the top-level microservices decomposition of the marketplace system — the overall structure, containers, and their communication topology.
**Architecture element being designed:** The entire system (greenfield, first decomposition pass)

---

## Step 1 — Review Inputs

This step consolidates all inputs available before design decisions are made. It produces the baseline against which design choices will be justified in subsequent steps.

---

### 1.1 Design Purpose

The purpose of this iteration is to produce the **first architectural cut** of the marketplace system. The system is being designed **from scratch** (greenfield). The target architecture is explicitly **microservices-based**, with asynchronous event-driven communication as the primary integration mechanism.

The output of this iteration is a set of top-level architectural decisions that establish:
- Which microservices exist and what their bounded contexts are.
- How microservices communicate (synchronous vs. asynchronous).
- Which data stores are owned by each microservice.
- How the all-or-nothing checkout saga is structured.
- How replication correctness semantics are enforced.

---

### 1.2 Primary Functional Requirements

The following use cases / functional requirements are the primary inputs. They are drawn from the Architectural Drivers specification.

| ID | Functional Requirement | Priority |
|---|---|---|
| FR-01 | Each microservice communicates with others through **asynchronous events** for cross-service functionalities. | High |
| FR-02 | Each microservice has **direct access only to its own data**; external access to another microservice's data is only possible through predefined interfaces or event subscriptions. | High |
| FR-03 | Business transactions must comply with **all-or-nothing atomicity** semantics. | High |
| FR-04 | Product updates (price change, delete) must support three replication correctness semantics: eventual, object-level causal, and cross-object causal (seller-scoped read-your-writes). | High |
| FR-05 | Cross-microservice referential integrity: Stock must always reference an existing product in Product. Two policies available: Available System (eventual) and Consistent System (synchronous). | High |
| FR-06 | A cart belonging to a customer session must not be checked out more than once. | High |
| FR-07 | The reserved quantity of a product must never exceed its available quantity. | High |
| FR-08 | The system must track successful and failed payments and deliveries per customer through counter increments. | Medium |
| FR-09 | Updates on each individual product's price or version must be **linearized**. | High |
| FR-10 | Concurrent Update Delivery transactions must execute in **isolation**. | High |

---

### 1.3 Quality Attribute Scenarios

Quality attribute scenarios are derived from the non-functional requirements. Each scenario is expressed using the standard stimulus–response format.

| ID | Quality Attribute | Scenario | Priority |
|---|---|---|---|
| QA-01 | **Reliability / Atomicity** | A customer submits a checkout. The payment succeeds but the stock reservation fails. The system must roll back the payment and cancel the order, leaving all microservices in a consistent pre-checkout state, within a bounded time window. | High |
| QA-02 | **Data Consistency** | A workload requires joining product catalog data with cart data. Because data is partitioned across microservices, the system must return a consistent view without requiring synchronous cross-service queries at read time. | High |
| QA-03 | **Replication Correctness** | A seller updates the price of product P twice in quick succession (v1 → v2). The cart microservice must eventually reflect price v2 for product P, and must never reflect v2 before v1 for the same product. | High |
| QA-04 | **Data Integrity** | A product is deleted from the Product microservice. The Inventory microservice must eventually prevent new reservations for that product. The system must not allow permanent dangling references. | High |
| QA-05 | **Event Ordering** | Two concurrent delivery status update requests arrive for the same Delivery record. Exactly one must succeed; the other must be rejected or retried without corrupting the delivery state. | High |
| QA-06 | **Scalability** | Under peak load (e.g., a flash sale), the Inventory microservice must handle a high volume of concurrent reservation requests without overselling. | Medium |
| QA-07 | **Availability** | If the Payment microservice is temporarily unavailable, the checkout saga must be able to suspend and resume without data loss. | Medium |

---

### 1.4 Constraints

| ID | Constraint | Source |
|---|---|---|
| CON-01 | The architecture **must be microservices-based**. Each microservice encapsulates its own data store. | Architectural mandate |
| CON-02 | Microservices must communicate **asynchronously** via events as the primary integration mechanism. | FR-01 |
| CON-03 | No microservice may directly access another microservice's data store. | FR-02 |
| CON-04 | The system must support the seven bounded contexts identified in the domain model: Product Catalog, Inventory, Cart, Order, Payment, Delivery, Customer. | DomainModel.md |
| CON-05 | All-or-nothing atomicity must be achieved **without** a distributed two-phase commit protocol (incompatible with the async communication mandate). | FR-03, FR-01 |

---

### 1.5 Architectural Concerns

| ID | Concern | Description |
|---|---|---|
| CRN-01 | **Distributed atomicity** | The asynchronous and non-blocking nature of events and the lack of a shared data store make classical distributed transactions (2PC/XA) infeasible. A saga-based compensation pattern is required. |
| CRN-02 | **Event ordering and idempotency** | Events can arrive out of order, late, or duplicated. Consumers must handle all three cases correctly without corrupting aggregate state. |
| CRN-03 | **Replication lag** | Cached or replicated data in downstream microservices (e.g., product price in Cart) may be stale. The design must define acceptable staleness bounds per scenario. |
| CRN-04 | **Cross-microservice data queries** | Some read workloads (e.g., order summary with product details) require data from multiple microservices. A cross-service query strategy (e.g., API composition or CQRS read models) must be defined. |
| CRN-05 | **Referential integrity enforcement** | Without a shared database, FK constraints cannot be enforced by the database layer. The design must enforce integrity at the application level via events and compensating logic. |

---

### 1.6 Summary of Inputs

| Category | Count | Notes |
|---|---|---|
| Functional Requirements | 10 | FR-01 through FR-10 |
| Quality Attribute Scenarios | 7 | QA-01 through QA-07 |
| Constraints | 5 | CON-01 through CON-05 |
| Architectural Concerns | 5 | CRN-01 through CRN-05 |
| Bounded Contexts (from DomainModel.md) | 7 | Product Catalog, Inventory, Cart, Order, Payment, Delivery, Customer |

---

*— Step 1 complete.*

---

## Step 2 — Establish Iteration Goal by Selecting Drivers

This step identifies which drivers from Step 1 are the **primary focus** of this iteration. Drivers not selected are deferred to later iterations. The iteration goal shapes every design decision made in Steps 3–6.

---

### 2.1 Iteration Goal

> **Establish the top-level structural decomposition of the marketplace system into microservices, define their communication topology, and address the highest-priority architectural risks that affect the system as a whole.**

This is a **greenfield, first-pass iteration**. The element being decomposed is the system itself — no sub-element has been designed yet. The primary output is a set of containers (microservices, data stores, message broker) and the patterns that govern how they interact.

---

### 2.2 Selected Drivers for This Iteration

The following drivers are selected because they have the widest structural impact: they constrain or shape the decomposition itself, the communication model, or the data ownership model. Drivers that affect the internals of a single microservice but not the overall topology are deferred.

#### Constraints (all selected — non-negotiable boundaries)

| ID | Constraint | Reason for Selection |
|---|---|---|
| CON-01 | Architecture must be microservices-based; each service owns its data store. | Defines the primary decomposition unit. |
| CON-02 | Microservices communicate asynchronously via events as the primary integration mechanism. | Defines the communication topology. |
| CON-03 | No microservice may directly access another microservice's data store. | Rules out shared-database patterns entirely. |
| CON-04 | System must support the seven bounded contexts from the domain model. | Maps directly to the set of microservices to be instantiated. |
| CON-05 | All-or-nothing atomicity without 2PC. | Eliminates synchronous distributed transactions; forces saga pattern. |

#### Functional Requirements (selected — cross-cutting scope)

| ID | Functional Requirement | Reason for Selection |
|---|---|---|
| FR-01 | Async event-based inter-service communication. | Core integration style; affects every microservice boundary. |
| FR-02 | Data encapsulation per microservice. | Governs data store allocation. |
| FR-03 | All-or-nothing atomicity for business transactions. | Forces the saga pattern and its orchestration topology. |
| FR-04 | Three replication correctness semantics for product updates. | Forces a versioned event design and partitioning strategy. |
| FR-05 | Cross-microservice referential integrity (S#1). | Forces an event-driven guard in Inventory consuming Product events. |
| FR-06 | No duplicate checkouts (S#2). | Forces a terminal state machine in Cart and an idempotency guard in Order. |
| FR-07 | No overselling (S#3). | Forces an atomic reservation operation inside Inventory's data store. |

#### Quality Attribute Scenarios (selected — highest priority, widest structural impact)

| ID | Quality Attribute Scenario | Reason for Selection |
|---|---|---|
| QA-01 | Checkout atomicity: payment succeeds, reservation fails → full rollback. | Directly drives the saga structure and compensation topology. |
| QA-03 | Replication correctness: seller price updates arrive at Cart in causal order. | Drives event versioning and message broker partitioning strategy. |
| QA-04 | Referential integrity: deleted product eventually blocked in Inventory. | Drives the event subscription model between Product and Inventory. |
| QA-05 | Delivery isolation: concurrent updates → exactly one succeeds. | Drives the need for optimistic locking inside the Delivery data store. |

#### Architectural Concerns (selected — systemic risks)

| ID | Concern | Reason for Selection |
|---|---|---|
| CRN-01 | Distributed atomicity without 2PC. | Must be mitigated at the topology level through saga pattern selection. |
| CRN-02 | Event ordering and idempotency. | Must be mitigated at the message broker and consumer design level. |
| CRN-03 | Replication lag in cached data. | Must be addressed by the event versioning and filtering strategy. |

---

### 2.3 Deferred Drivers

The following drivers are acknowledged but deferred to a later iteration, as they affect the internal design of individual microservices rather than the overall topology.

| ID | Driver | Reason for Deferral |
|---|---|---|
| FR-08 | Customer statistics counter increments (S#4). | Internal to Customer microservice; does not affect overall topology. |
| FR-09 | Linearized product updates (S#5). | Enforced inside Product's data store via optimistic locking; internal concern. |
| FR-10 | Delivery transaction isolation (S#6). | Enforced inside Delivery's data store; internal concern. |
| QA-02 | Cross-service data joins for read workloads. | Requires a CQRS / API Composition decision; deferred to a read-model iteration. |
| QA-06 | Inventory scalability under peak load. | Capacity and scaling design deferred to a performance iteration. |
| QA-07 | Checkout saga resilience when Payment is unavailable. | Durability and retry strategy deferred to a reliability iteration. |
| CRN-04 | Cross-microservice query strategy. | Deferred with QA-02. |
| CRN-05 | Application-level referential integrity. | Partially addressed by FR-05 / QA-04 in this iteration; full treatment deferred. |

---

### 2.4 Iteration Goal Summary

| Category | Selected | Deferred |
|---|---|---|
| Constraints | 5 / 5 | 0 |
| Functional Requirements | 7 / 10 | 3 |
| Quality Attribute Scenarios | 4 / 7 | 3 |
| Architectural Concerns | 3 / 5 | 2 |

The design decisions produced in Steps 3–6 must satisfy all selected drivers. Any decision that conflicts with a selected driver, or that fails to address a selected QA scenario, is considered a design deficiency to be resolved before closing this iteration.

---

*— Step 2 complete. Awaiting review before proceeding to Step 3 (Choose One or More Elements of the System to Decompose).*
