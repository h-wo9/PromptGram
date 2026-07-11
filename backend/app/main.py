from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, prompts, users
from app.core.config import settings

app = FastAPI(title="PromptGram API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(prompts.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}
