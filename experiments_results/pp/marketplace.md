graph TD
    classDef actor fill:#f4e2d8,stroke:#c0785a,color:#000
    classDef svc fill:#dce8f5,stroke:#4a7fb5,color:#000
    classDef db fill:#e8f5e9,stroke:#388e3c,color:#000
    classDef topic fill:#fff8e1,stroke:#e65100,color:#000
    classDef gw fill:#ede7f6,stroke:#673ab7,color:#000

    Seller([Seller]):::actor
    Customer([Customer]):::actor
    GW[API Gateway]:::gw

    subgraph microservices["Microservices"]
        PS["Product Service\n─────────────\n• CRUD products & prices\n• Linearised updates · S5\n• Transactional Outbox"]:::svc
        SS["Stock Service\n─────────────\n• Manage inventory\n• Reserve / release stock\n• No overselling · S3\n• Referential integrity · S1"]:::svc
        CS["Cart Service\n─────────────\n• Manage cart items\n• Local product cache\n• Causality-aware replication · 4.3\n• Idempotent checkout · S2"]:::svc
        OS["Order Service  ★\n— Saga Orchestrator —\n─────────────\n• Checkout saga lifecycle\n• All-or-nothing atomicity · 4.2\n• Compensating transactions"]:::svc
        PMS["Payment Service\n─────────────\n• Charge / refund\n• Track payment stats · S4"]:::svc
        DS["Delivery Service\n─────────────\n• Dispatch / cancel\n• Isolated concurrent txns · S6\n• Track delivery stats · S4"]:::svc
        CUS["Customer Service\n─────────────\n• Accounts & sessions\n• Aggregate stats"]:::svc
    end

    subgraph datastores["Private Data Stores  (Database-per-Service)"]
        PDB[(Product DB)]:::db
        SDB[(Stock DB)]:::db
        CDB[("Cart DB\n+ Product Cache")]:::db
        ODB[(Order DB)]:::db
        PMDB[(Payment DB)]:::db
        DDB[(Delivery DB)]:::db
        CUDB[(Customer DB)]:::db
    end

    subgraph broker["Kafka — Async Message Broker"]
        T_prod{{"product-events\nProductCreated · PriceUpdated · ProductDeleted"}}:::topic
        T_cart{{"cart-events\nCartCheckedOut"}}:::topic
        T_saga{{"saga-commands\nReserveStock · ProcessPayment · Dispatch\n+ compensating variants"}}:::topic
        T_stock{{"stock-events\nStockReserved · StockReservationFailed"}}:::topic
        T_pay{{"payment-events\nPaymentSucceeded · PaymentFailed"}}:::topic
        T_del{{"delivery-events\nDeliveryCompleted · DeliveryFailed"}}:::topic
    end

    %% ── Entry points ──────────────────────────────────────────────
    Seller & Customer --> GW
    GW --> PS & SS & CS & OS & CUS

    %% ── Private DB bindings ───────────────────────────────────────
    PS --- PDB
    SS --- SDB
    CS --- CDB
    OS --- ODB
    PMS --- PMDB
    DS --- DDB
    CUS --- CUDB

    %% ── Product propagation (4.3 replication correctness) ─────────
    PS -- "① publish via Outbox" --> T_prod
    T_prod -- "S1 · enforce referential integrity" --> SS
    T_prod -- "4.3-i/ii/iii · causality-aware cache\nper-seller sequence numbers" --> CS

    %% ── Checkout saga start ───────────────────────────────────────
    CS -- "S2 · idempotency key" --> T_cart
    T_cart -- "start checkout saga" --> OS

    %% ── Saga orchestration commands (4.2) ────────────────────────
    OS -- "② ReserveStock\n   ReleaseStock (compensate)" --> T_saga
    OS -- "② ProcessPayment\n   Refund (compensate)" --> T_saga
    OS -- "② DispatchDelivery\n   CancelDelivery (compensate)" --> T_saga

    T_saga --> SS & PMS & DS

    %% ── Saga reply events ─────────────────────────────────────────
    SS -- "S3 · optimistic lock check" --> T_stock
    T_stock --> OS

    PMS -- "S4 · track stats" --> T_pay
    T_pay --> OS

    DS -- "S4 S6 · isolated execution" --> T_del
    T_del --> OS
    T_del -- "increment payment/delivery counters · S4" --> CUS
