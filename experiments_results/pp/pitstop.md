graph TB
    subgraph Client["Client Layer"]
        WebApp["Web Application\nASP.NET Core MVC"]
    end

    subgraph APIs["API Microservices"]
        CustSvc["Customer Service\n─────────────────\nREST API\nSchema: customer"]
        VehSvc["Vehicle Service\n─────────────────\nREST API\nSchema: vehicle"]
        WSSvc["Workshop Service\n─────────────────\nREST API\nSchema: workshop\n(caches Customer + Vehicle\nread models locally)"]
    end

    subgraph BG["Background Microservices"]
        TimeSvc["Time Service\n─────────────────\nScheduler\nPublishes daily tick"]
        NotifSvc["Notification Service\n─────────────────\nBackground Worker\n(no own API)"]
        InvSvc["Invoice Service\n─────────────────\nBackground Worker\nSchema: invoice"]
        AuditSvc["Audit Log Service\n─────────────────\nBackground Worker\nSchema: auditlog"]
    end

    subgraph Infra["Infrastructure"]
        MQ[("RabbitMQ\nMessage Broker")]
        SQL[("SQL Server\nSingle Instance\nPer-service schemas")]
        SMTP["Email / SMTP"]
    end

    %% ── Synchronous REST (WebApp → APIs only) ──────────────────────────────
    WebApp -->|HTTP REST| CustSvc
    WebApp -->|HTTP REST| VehSvc
    WebApp -->|HTTP REST| WSSvc

    %% ── Events Published ───────────────────────────────────────────────────
    CustSvc -->|"CustomerRegistered"| MQ
    VehSvc  -->|"VehicleRegistered"| MQ
    WSSvc   -->|"MaintenanceJobPlanned\nMaintenanceJobFinished"| MQ
    TimeSvc -->|"DayHasPassed"| MQ

    %% ── Events Consumed ────────────────────────────────────────────────────
    MQ -->|"CustomerRegistered\nVehicleRegistered\n(build local read model)"| WSSvc
    MQ -->|"MaintenanceJobPlanned\nDayHasPassed"| NotifSvc
    MQ -->|"MaintenanceJobFinished"| InvSvc
    MQ -->|"ALL events"| AuditSvc

    %% ── Persistence ────────────────────────────────────────────────────────
    CustSvc -->|"reads / writes"| SQL
    VehSvc  -->|"reads / writes"| SQL
    WSSvc   -->|"reads / writes"| SQL
    InvSvc  -->|"reads / writes"| SQL
    AuditSvc-->|"writes"| SQL

    %% ── External I/O ───────────────────────────────────────────────────────
    NotifSvc -->|"Customer notification"| SMTP
    InvSvc   -->|"Invoice email"| SMTP
