
from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes.user import router as user_router
from routes.tickettype import router as tickettype_router
from routes.events import router as events_router
from routes.booking import router as booking_router
from routes.payment import router as payment_router
from routes.report import router as report_router
from routes.assistant import router as assistant_router
from mcp_func.mcp_tools_.event_search_mcp_tool import router as mcp_event_search
from database.database import engine, Base
from scheduler import start_scheduler, stop_scheduler

import database.models

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(events_router)
app.include_router(tickettype_router)
app.include_router(booking_router)
app.include_router(payment_router)
app.include_router(report_router)
app.include_router(assistant_router)
app.include_router(mcp_event_search)


@app.get("/health")
def health_check():
    return {"status": "ok"}
