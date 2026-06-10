graph TB
    subgraph Clients["Client Layer"]
        WebSPA["Web SPA\n(React / Angular)"]
        WebTrad["Web Traditional\n(Server-rendered MVC)"]
        Mobile["Mobile Apps\n(React Native)"]
    end

    subgraph Ingress["Ingress Layer"]
        LB["Load Balancer"]
        APIGW["API Gateway\n(Auth · Rate-limit · Route)"]
    end

    subgraph Services["Core Services"]
        Identity["Identity Service\n(Register · Sign-in · Sign-out)"]
        Catalog["Catalog Service\n(List · Filter by type/brand)"]
        Basket["Basket Service\n(Add · Edit · Remove)"]
        Order["Order Service\n(Checkout · Order history)"]
    end

    subgraph Messaging["Async Messaging"]
        MQ[("Message Broker\nRabbitMQ / Azure Service Bus")]
    end

    subgraph Async["Async Services"]
        Payment["Payment Service"]
        Notif["Notification Service"]
    end

    subgraph Data["Data Layer (per-service)"]
        IdentityDB[("Identity DB\nPostgreSQL")]
        CatalogDB[("Catalog DB\nPostgreSQL + Read Replica")]
        BasketCache[("Basket Cache\nRedis")]
        OrderDB[("Order DB\nPostgreSQL")]
        PaymentDB[("Payment DB\nPostgreSQL")]
    end

    subgraph Observability["Observability"]
        Prom["Prometheus + Grafana"]
        ELK["ELK Stack"]
    end

    WebSPA & WebTrad & Mobile --> LB --> APIGW
    APIGW --> Identity & Catalog & Basket & Order
    Basket & Order --> MQ
    MQ --> Payment & Notif
    Identity --> IdentityDB
    Catalog --> CatalogDB
    Basket --> BasketCache
    Order --> OrderDB
    Payment --> PaymentDB
    Services --> Prom & ELK
