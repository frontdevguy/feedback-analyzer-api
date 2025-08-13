from fastapi.middleware.cors import CORSMiddleware


def setup_routes(app, config):
    from . import health, auth, topic, dashboard

    # Setup CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(topic.router, prefix="/topic", tags=["topic"])
    app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

    auth.router.config = config
