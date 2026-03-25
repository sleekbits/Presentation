from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.download import router as download_router
from .routes.fill import router as fill_router
from .routes.parse import router as parse_router
from .routes.sample import router as sample_router
from .routes.upload import router as upload_router
from .services.job_store import job_store


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    job_store.cleanup_expired()


app = FastAPI(title="PPTX Autofill API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(sample_router)
app.include_router(parse_router)
app.include_router(fill_router)
app.include_router(download_router)


@app.get("/health")
def health() -> dict[str, str]:
    job_store.cleanup_expired()
    return {"status": "ok"}
