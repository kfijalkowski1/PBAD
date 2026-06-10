flowchart TB
    subgraph ClientLayer["Client Layer"]
        WebBrowser["Web Browser\n(Angular SPA — CON-1)"]
        ExtClients["External API Clients"]
    end

    subgraph APILayer["API Layer"]
        APIGW["API Gateway\nRouting · JWT validation · Rate limiting"]
        subgraph Adapters["Protocol Adapters — QA-6 / CON-5"]
            REST["REST Adapter"]
            gRPC["gRPC Adapter"]
        end
    end

    subgraph CoreServices["Core Microservices"]
        AuthSvc["Auth Service\nHPS-1 · QA-5"]
        PriceWriteSvc["Price Write Service\nHPS-2  —  COMMAND side"]
        PriceQuerySvc["Price Query Service\nHPS-3  —  QUERY side"]
        HotelSvc["Hotel Service\nHPS-4"]
        RateSvc["Rate Service\nHPS-5\ncalculation rules engine"]
        UserSvc["User Service\nHPS-6"]
        PubSvc["Price Publication Service\nQA-2  —  async fanout worker"]
        MonitorSvc["Observability Service\nQA-8  —  metrics · tracing · logs"]
    end

    subgraph EventBus["Event Bus — Apache Kafka"]
        PriceChangedEvt[/"price-changed\ntopic"/]
        PricePublishedEvt[/"price-published\ntopic"/]
        AuditEvt[/"audit-events\ntopic"/]
    end

    subgraph DataLayer["Data Layer"]
        PriceDB[("Price DB\nPostgreSQL")]
        HotelDB[("Hotel DB\nPostgreSQL")]
        RateDB[("Rate DB\nPostgreSQL")]
        UserDB[("User DB\nPostgreSQL")]
        Cache[("Price Cache\nRedis\nQA-1 · QA-4")]
    end

    subgraph ExternalSystems["External Systems"]
        UIS["User Identity Service\n(cloud — CON-2)"]
        PMS["Property Management\nSystem"]
        CMS["Channel Management\nSystem"]
        CAS["Commercial Analysis\nSystem"]
        OtherSys["Other Systems"]
    end

    WebBrowser -->|HTTPS| APIGW
    ExtClients --> REST & gRPC
    REST & gRPC --> APIGW

    APIGW -->|"validate JWT"| AuthSvc
    APIGW --> PriceWriteSvc & PriceQuerySvc
    APIGW --> HotelSvc & RateSvc & UserSvc

    AuthSvc -->|"verify credentials"| UIS
    UserSvc -->|"sync permissions"| UIS

    PriceWriteSvc --> PriceDB
    PriceWriteSvc -->|"apply calculation rules"| RateSvc
    PriceWriteSvc -->|"emit event"| PriceChangedEvt

    PriceChangedEvt -->|"update cache"| PriceQuerySvc
    PriceChangedEvt --> PubSvc

    PriceQuerySvc -->|"cache-first read"| Cache
    PriceQuerySvc -->|"cache miss fallback"| PriceDB

    PubSvc -->|REST| PMS & CMS & CAS & OtherSys
    PubSvc -->|"emit event"| PricePublishedEvt

    HotelSvc --> HotelDB
    RateSvc --> RateDB
    UserSvc --> UserDB

    PriceChangedEvt & PricePublishedEvt --> AuditEvt
    AuditEvt --> MonitorSvc
    CoreServices -->|"metrics / traces"| MonitorSvc
