"""
Models and typing definitions for Tic Tac Toe backend (FastAPI).
Includes Pydantic models for requests/responses and core database schema objects.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# PUBLIC_INTERFACE
class User(BaseModel):
    """User data model as stored in Supabase/users."""
    id: str
    email: str
    username: Optional[str]
    created_at: Optional[datetime]


# PUBLIC_INTERFACE
class UserSignupRequest(BaseModel):
    """Sign-up request."""
    email: str
    password: str
    username: Optional[str] = None


# PUBLIC_INTERFACE
class UserAuthResponse(BaseModel):
    """Response containing token or error for authentication/signup."""
    id: Optional[str]
    email: Optional[str]
    username: Optional[str]
    access_token: Optional[str]
    error: Optional[str]


# PUBLIC_INTERFACE
class UserLoginRequest(BaseModel):
    """Login request with email and password."""
    email: str
    password: str


# PUBLIC_INTERFACE
class GameCreateRequest(BaseModel):
    """Request to create a new game (optionally vs AI)."""
    vs_ai: bool = Field(..., description="Whether this is a user vs. AI game")
    ai_level: Optional[int] = Field(1, description="Difficulty (unused for now)")
    username: Optional[str] = Field(None, description="Username of requesting player")


# PUBLIC_INTERFACE
class GameJoinRequest(BaseModel):
    """Request to join existing multiplayer game."""
    game_id: str
    username: str


# PUBLIC_INTERFACE
class MoveRequest(BaseModel):
    """A move attempt in ongoing game by user or AI."""
    game_id: str
    player: str
    row: int
    col: int


# PUBLIC_INTERFACE
class GameState(BaseModel):
    """Returns the board state and turn info."""
    game_id: str
    board: List[List[str]]
    players: List[Optional[str]]
    next_to_move: Optional[str]
    winner: Optional[str]
    is_draw: bool
    last_move: Optional[MoveRequest]
    created_at: datetime
    finished_at: Optional[datetime]
    moves: List[MoveRequest]


# PUBLIC_INTERFACE
class GameHistoryItem(BaseModel):
    """Past/completed game summary for listing."""
    game_id: str
    board: List[List[str]]
    players: List[Optional[str]]
    winner: Optional[str]
    finished_at: Optional[datetime]
    is_draw: bool


# PUBLIC_INTERFACE
class LeaderboardEntry(BaseModel):
    """For scoreboard endpoint."""
    username: str
    wins: int
    losses: int
    draws: int
    games_played: int
