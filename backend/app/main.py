from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai, auth, comments, notifications, prompts, users
from app.core.config import settings

app = FastAPI(title="PromptGram API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(prompts.router)
app.include_router(ai.router)
app.include_router(comments.router)
app.include_router(notifications.router)

# cookie를 쓰지 않으므로 credentials 불필요 (refresh는 localStorage + request body)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}
