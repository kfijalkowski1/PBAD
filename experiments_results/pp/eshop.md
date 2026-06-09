C4Container
    title E-Shop — C4 Container Diagram

    Person(customer, "Customer", "Browses products, manages basket, places orders")

    System_Boundary(eshop, "E-Shop System") {

        Container(web_mvc, "Web MVC App", "ASP.NET Core MVC", "Server-rendered frontend for traditional browsers")
        Container(spa, "SPA", "React / Angular", "Single Page Application for modern browsers")
        Container(mobile, "Mobile Apps", "iOS / Android", "Native mobile clients")

        Container(api_gw, "API Gateway", "Ocelot / YARP", "Single entry point: routes requests, validates JWT, rate limits")

        Container(identity_svc, "Identity Service", "ASP.NET Core", "Register account, sign in, sign out; issues and refreshes JWT tokens")
        Container(catalog_svc, "Catalog Service", "ASP.NET Core", "List catalog items, filter by type and brand")
        Container(basket_svc, "Basket Service", "ASP.NET Core", "Add, edit and remove items in the shopping basket")
        Container(ordering_svc, "Ordering Service", "ASP.NET Core", "Process checkout, store and retrieve order history")
        Container(notification_svc, "Notification Service", "ASP.NET Core", "Send order confirmation emails and push notifications")

        Container(broker, "Message Broker", "RabbitMQ / Azure Service Bus", "Async pub/sub event bus decoupling services")

        ContainerDb(identity_db, "Identity DB", "SQL Server", "User credentials and profiles")
        ContainerDb(catalog_db, "Catalog DB", "SQL Server", "Product catalog data")
        ContainerDb(catalog_cache, "Catalog Cache", "Redis", "Read-through cache for catalog queries")
        ContainerDb(basket_cache, "Basket Cache", "Redis", "Ephemeral basket session state")
        ContainerDb(order_db, "Order DB", "SQL Server", "Order records and history")
    }

    Rel(customer, web_mvc, "Uses", "HTTPS")
    Rel(customer, spa, "Uses", "HTTPS")
    Rel(customer, mobile, "Uses", "HTTPS")

    Rel(web_mvc, api_gw, "Calls", "REST / HTTPS")
    Rel(spa, api_gw, "Calls", "REST / HTTPS")
    Rel(mobile, api_gw, "Calls", "REST / HTTPS")

    Rel(api_gw, identity_svc, "Routes to", "REST / HTTPS")
    Rel(api_gw, catalog_svc, "Routes to", "REST / HTTPS")
    Rel(api_gw, basket_svc, "Routes to", "REST / HTTPS")
    Rel(api_gw, ordering_svc, "Routes to", "REST / HTTPS")

    Rel(basket_svc, broker, "Publishes CheckoutStarted", "AMQP")
    Rel(ordering_svc, broker, "Publishes OrderPlaced", "AMQP")
    Rel(broker, notification_svc, "Delivers events", "AMQP")

    Rel(identity_svc, identity_db, "Reads / writes", "SQL")
    Rel(catalog_svc, catalog_db, "Reads / writes", "SQL")
    Rel(catalog_svc, catalog_cache, "Caches reads", "Redis")
    Rel(basket_svc, basket_cache, "Reads / writes", "Redis")
    Rel(ordering_svc, order_db, "Reads / writes", "SQL")
