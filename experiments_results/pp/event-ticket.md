graph TB
    classDef client  fill:#2E79B5,stroke:#1a5a8a,color:#fff
    classDef gateway fill:#C06028,stroke:#8a4018,color:#fff
    classDef service fill:#1F8A65,stroke:#145c43,color:#fff
    classDef infra   fill:#7B64B8,stroke:#5a469a,color:#fff
    classDef db      fill:#4a4a4a,stroke:#2a2a2a,color:#ddd
    classDef ext     fill:#8888A8,stroke:#606080,color:#fff

    subgraph CLIENT["Client Layer"]
        Web["Web App"]:::client
        Mobile["Mobile App"]:::client
    end

    GW["API Gateway"]:::gateway

    subgraph SERVICES["Microservices"]
        Auth["Auth\nService"]:::service
        User["User\nService"]:::service
        Event["Event\nService"]:::service
        Search["Search\nService"]:::service
        Inv["Inventory\nService"]:::service
        Order["Order\nService"]:::service
        Pay["Payment\nService"]:::service
        Ticket["Ticket\nService"]:::service
        Deliver["Delivery\nService"]:::service
        Notif["Notification\nService"]:::service
    end

    Cache[("Redis Cache")]:::infra
    MQ[["Message Queue (Kafka)"]]:::infra

    subgraph DATA["Data Stores  —  one DB per service"]
        UDB[("User DB")]:::db
        EDB[("Event DB")]:::db
        IDB[("Inventory DB")]:::db
        ODB[("Order DB")]:::db
        PDB[("Payment DB")]:::db
        TDB[("Ticket DB")]:::db
        DDB[("Delivery DB")]:::db
        SIdx[("Search Index")]:::db
    end

    subgraph EXT["External Services"]
        IdP["Identity\nProvider"]:::ext
        PGW["Payment\nGateway"]:::ext
        Email["Email\nService"]:::ext
        Push["Mobile Push\nService"]:::ext
        Venue["Venue Mgmt\nSystem"]:::ext
    end

    %% ── Clients → Gateway ──────────────────────────────
    Web    --> GW
    Mobile --> GW

    %% ── Gateway → Services (REST/HTTP) ─────────────────
    GW --> Auth & User & Event & Inv & Order & Pay & Ticket & Deliver & Search & Notif

    %% ── Auth Domain ────────────────────────────────────
    Auth --> IdP
    Auth --> User
    Auth --> Cache

    %% ── User Domain ────────────────────────────────────
    User --> UDB
    User --> Cache

    %% ── Event Domain ───────────────────────────────────
    Event --> EDB
    Event --> Cache
    Event --> Venue
    Event --> Search

    %% ── Inventory Domain ───────────────────────────────
    Inv --> IDB
    Inv --> Cache
    Inv --> Event
    Inv --> MQ

    %% ── Order Domain ───────────────────────────────────
    Order --> ODB
    Order --> Inv
    Order --> Pay
    Order --> MQ

    %% ── Payment Domain ─────────────────────────────────
    Pay --> PDB
    Pay --> Cache
    Pay --> PGW
    Pay --> MQ

    %% ── Ticket Domain ──────────────────────────────────
    Ticket --> TDB
    Ticket --> Cache
    Ticket --> MQ

    %% ── Delivery Domain ────────────────────────────────
    Deliver --> DDB
    Deliver --> Cache
    Deliver --> Email
    Deliver --> Push
    Deliver --> MQ

    %% ── Search Domain ──────────────────────────────────
    Search --> SIdx

    %% ── Notification Domain ────────────────────────────
    Notif --> Email
    Notif --> Push

    %% ── Async events (dashed = MQ consumer) ────────────
    MQ -.->|PaymentProcessed| Ticket
    MQ -.->|TicketGenerated|   Deliver
    MQ -.->|DeliveryCompleted| Notif
    MQ -.->|InventoryUpdated|  Search
    MQ -.->|OrderFailed|       Inv
