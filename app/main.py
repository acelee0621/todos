from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.users import routes
from app.routers import lists_routes, todos_route, notification
from app.utils.migrations import run_migrations



# Set up logging configuration
setup_logging()

# Optional: Run migrations on startup
run_migrations()


app = FastAPI(title=settings.app_name, version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(routes.router)  # Users Router
app.include_router(lists_routes.router)
app.include_router(todos_route.router)
app.include_router(notification.router)


@app.get("/health")
async def health_check(response: Response):
    response.status_code = 200
    return {"status": "ok 👍 "}
