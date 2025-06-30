from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .game import router as game_router

openapi_tags = [
    {"name": "auth", "description": "Authentication and user management"},
    {"name": "game", "description": "Game creation, move, join, listing"},
    {"name": "leaderboard", "description": "Leaderboard, scoreboard, stats"},
]

app = FastAPI(
    title="Tic Tac Toe Arena API",
    description="FastAPI backend for multiplayer & AI Tic Tac Toe with Supabase integration.",
    version="1.0.0",
    openapi_tags=openapi_tags
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(game_router)


@app.get("/")
def health_check():
    """Simple health check."""
    return {"message": "Healthy"}
