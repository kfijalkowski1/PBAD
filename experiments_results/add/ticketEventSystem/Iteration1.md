# Iteration 1 — Establish Overall System Structure

**Author:** Neo (Software Architect)  
**Process:** Attribute-Driven Design (ADD) 3.0  
**Date:** 2026-05-23  
**Status:** In Progress — Step 1 Complete

---

## Step 1: Review Inputs

### 1.1 Design Purpose

This is a **greenfield system**. The purpose of this first iteration is to establish the overall architectural structure of the Hotel Pricing System. No prior architecture exists; all decisions are made from scratch. The output of this iteration will be the highest-level decomposition of the system into its main deployable containers and the communication patterns between them — the foundation upon which all subsequent iterations will build.

### 1.2 Primary Functional Requirements

The following user stories are considered inputs for this iteration. Not all of them will be fully addressed here; they serve to ensure that the overall structure created in this iteration is capable of accommodating them.

| ID | Description | Priority |
|----|-------------|----------|
| HPS-1 | Log In: A user provides credentials in a login window. The system checks these credentials against a user identity service and, if successful, provides access to the system. | Medium |
| HPS-2 | Change Prices: A user selects a specific hotel and dates to make price changes to base or fixed rates. All calculated rates are updated, and changes are pushed to the Channel Management System. | High |
| HPS-3 | Query Prices: A user or external system queries prices for a given hotel through the user interface or a query API. | High |
| HPS-4 | Manage Hotels: An administrator adds, changes, or modifies hotel information, including tax rates, available rates, and room types. | High |
| HPS-5 | Manage Rates: An administrator adds, changes, or modifies rates, including defining calculation business rules. | Medium |
| HPS-6 | Manage Users: An administrator changes permissions for a given user. | Medium |

### 1.3 Quality Attribute Scenarios

| ID | Quality Attribute | Scenario | Priority |
|----|------------------|----------|----------|
| QA-1 | Performance | Base rate price changed; all rates and room types published in < 100 ms. | High |
| QA-2 | Reliability | 100% of price changes are published successfully and received by the channel management system. | High |
| QA-3 | Availability | Pricing query uptime SLA: 99.9% outside of maintenance windows. | High |
| QA-4 | Scalability | Minimum 100,000 price queries/day; capable of 1,000,000 with no more than 20% average latency increase. | High |
| QA-5 | Security | Credentials validated against the User Identity Service; users presented with only authorised functions. | High |
| QA-6 | Modifiability | New query protocol (e.g., gRPC) can be added without changes to core components. | Medium |
| QA-7 | Deployability | Application moved between non-production environments without code changes. | Medium |
| QA-8 | Monitorability | 100% of price publication performance and reliability metrics can be collected. | Medium |
| QA-9 | Testability | 100% of system elements support integration testing independently of external systems. | Medium |

### 1.4 Constraints

| ID | Constraint |
|----|------------|
| CON-1 | Users interact through a web browser on Windows, OSX, Linux, and different devices. |
| CON-2 | Users are managed through a cloud provider identity service; resources are hosted in the cloud. |
| CON-3 | Code hosted on a proprietary Git-based platform already in use. |
| CON-4 | Full release in 6 months; MVP demonstrated to stakeholders within 2 months. |
| CON-5 | Initial integration with existing systems via REST APIs; other protocols may be needed later. |
| CON-6 | Cloud-native approach favoured. |

### 1.5 Architectural Concerns

| ID | Concern |
|----|---------|
| CRN-1 | Establish an overall initial system structure. |
| CRN-2 | Leverage the team's knowledge of Java technologies and the Angular framework. |
| CRN-3 | Allocate work to members of the development team. |
| CRN-4 | Avoid introducing technical debt. |
| CRN-5 | Set up a continuous deployment infrastructure. |

---

---

## Step 2: Establish Iteration Goal by Selecting Drivers

### 2.1 Iteration Goal

The goal of this iteration is to **establish the overall structure of the Hotel Pricing System** by selecting a reference architecture and decomposing the system into its primary deployable containers. This directly addresses CRN-1 and creates the structural foundation that all subsequent iterations will refine.

### 2.2 Selected Drivers

The following drivers are selected as the primary focus of this iteration. They are the ones whose influence is most significant at the level of overall system structure — they will either determine which reference architecture is chosen or constrain what containers must exist.

| Driver | Type | Justification for Selection |
|--------|------|-----------------------------|
| **CRN-1** | Concern | Primary goal of Iteration 1: establish the overall system structure. |
| **CON-1** | Constraint | Mandates a browser-based frontend, which implies a distinct frontend container. |
| **CON-2** | Constraint | Mandates cloud hosting and a cloud identity service, which constrains both infrastructure choices and the authentication container. |
| **CON-5** | Constraint | REST as the initial integration protocol with external systems; must be reflected in how integration boundaries are drawn. |
| **CON-6** | Constraint | Cloud-native approach drives the choice of containerised, independently deployable microservices over a monolith. |
| **QA-1** | Quality Attribute | Sub-100 ms publication requires the price recalculation and write path to be a focused, low-latency service — not coupled to a slow distribution process. |
| **QA-2** | Quality Attribute | 100% delivery guarantee requires a durable, asynchronous delivery mechanism (message broker) between the write path and downstream systems. |
| **QA-3** | Quality Attribute | 99.9% query uptime requires the read path to be independently scalable and deployable from the write path. |
| **QA-4** | Quality Attribute | Up to 1,000,000 queries/day requires the query API to be horizontally scalable, which implies a dedicated, read-optimised container. |
| **QA-5** | Quality Attribute | Authentication and authorisation must be applied uniformly at a single entry point, driving the need for an API Gateway or equivalent. |
| **CRN-2** | Concern | Java (Spring Boot) for backend microservices and Angular for the frontend — influences technology decisions within the identified containers. |

### 2.3 Drivers Not Addressed in This Iteration

The following drivers are noted but will be addressed in subsequent iterations once the structural skeleton is in place.

| Driver | Reason for Deferral |
|--------|---------------------|
| HPS-1 through HPS-6 | Functional scenarios will be addressed in the component and sequence diagram iterations once containers are defined. |
| QA-6 | Modifiability for protocol extension requires component-level decisions within the query container — deferred to a later iteration. |
| QA-7 | Deployability via environment configuration is a cross-cutting concern addressed through CI/CD pipeline design (CRN-5), deferred after structure is set. |
| QA-8 | Monitorability is a cross-cutting concern; a monitoring infrastructure layer will be added once containers are stable. |
| QA-9 | Testability via external system isolation requires defining interface contracts first; deferred to the interfaces iteration. |
| CRN-3 | Work allocation follows from the container decomposition produced by this iteration — addressed at the end of this iteration. |
| CRN-4 | Avoidance of technical debt is enforced through design review at each step, not a single design decision. |
| CRN-5 | CI/CD infrastructure is addressed in a dedicated DevOps iteration after the container structure is known. |
| CON-3 | Git platform choice is an operational constraint with no structural impact on the architecture. |
| CON-4 | MVP timeline will influence the sequencing of future iterations but does not change the target architecture structure. |

---

_Step 2 complete. Awaiting review before proceeding to Step 3._
