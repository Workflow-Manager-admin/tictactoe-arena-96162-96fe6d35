"""
Game and leaderboard endpoints. Handles creating/joining games, moves, listing games,
game state retrieval, and the scoreboard, using Supabase as DB backend.
"""

import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from dotenv import load_dotenv
from supabase import create_client, Client
from .auth import verify_token
from .models import (
    GameCreateRequest, GameJoinRequest, MoveRequest,
    GameState, GameHistoryItem, LeaderboardEntry, User
)
from .logic import (
    initial_board, make_move, check_winner, is_draw, ai_pick, X, O_TOKEN
)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter(tags=["game"])


def get_board_from_db(game_row):
    """Parse board string to nested list."""
    import json
    board = json.loads(game_row["board"])
    return board


def save_board_to_str(board):
    import json
    return json.dumps(board)


# PUBLIC_INTERFACE
@router.post("/game/create", summary="Create new Tic Tac Toe game", response_model=GameState)
async def create_game(
    req: GameCreateRequest,
    current_user: User = Depends(verify_token),
):
    """
    Creates a new Tic Tac Toe game (vs AI or waiting for other player).
    """
    import json

    if req.vs_ai:
        player1 = current_user.username or current_user.email
        player2 = "AI"
        players = [player1, player2]
        next_move = player1
    else:
        player1 = current_user.username or current_user.email
        players = [player1, None]
        next_move = player1

    board = initial_board()
    created = datetime.utcnow()
    entry = {
        "board": save_board_to_str(board),
        "players": json.dumps(players),
        "next_to_move": next_move,
        "winner": None,
        "is_draw": False,
        "moves": json.dumps([]),
        "created_at": created.isoformat(),
        "finished_at": None,
        "status": "waiting" if not req.vs_ai else "active",
        "vs_ai": req.vs_ai,
    }
    result = supabase.table("games").insert(entry).execute()
    game_id = result.data[0]["id"]

    return GameState(
        game_id=game_id,
        board=board,
        players=players,
        next_to_move=next_move,
        winner=None,
        is_draw=False,
        last_move=None,
        created_at=created,
        finished_at=None,
        moves=[],
    )


# PUBLIC_INTERFACE
@router.post("/game/join", summary="Join existing multiplayer game", response_model=GameState)
async def join_game(
    req: GameJoinRequest,
    current_user: User = Depends(verify_token)
):
    """
    Joins an available waiting game (not vs AI).
    """
    import json

    # Fetch game
    resp = supabase.table("games").select("*").eq("id", req.game_id).single().execute()
    if not resp.data:
        raise HTTPException(404, "Game not found")
    game = resp.data
    players = json.loads(game["players"])
    if players[0] == req.username:
        raise HTTPException(400, "Cannot join your own game")

    if players[1] is not None:
        raise HTTPException(400, "Game already full")

    players[1] = req.username
    supabase.table("games").update({"players": json.dumps(players), "status": "active"}).eq("id", req.game_id).execute()

    return GameState(
        game_id=game["id"],
        board=json.loads(game["board"]),
        players=players,
        next_to_move=game["next_to_move"],
        winner=game["winner"],
        is_draw=game["is_draw"],
        last_move=None,
        created_at=datetime.fromisoformat(game["created_at"]),
        finished_at=game["finished_at"],
        moves=json.loads(game["moves"])
    )


# PUBLIC_INTERFACE
@router.post("/game/move", summary="Play/make a move in a game", response_model=GameState)
async def play_move(
    req: MoveRequest,
    current_user: User = Depends(verify_token)
):
    """
    Handles a player's move, updates game state, checks for win/draw, makes AI move if AI game.
    """
    import json

    # Fetch game
    resp = supabase.table("games").select("*").eq("id", req.game_id).single().execute()
    if not resp.data:
        raise HTTPException(404, "Game not found")
    game = resp.data

    # Check turn
    players = json.loads(game["players"])
    if req.player not in players:
        raise HTTPException(403, "Not a player in this game")
    idx = players.index(req.player)
    mark = X if idx == 0 else O_TOKEN

    board = json.loads(game["board"])
    moves = json.loads(game["moves"])
    if game["winner"] or game["is_draw"]:
        raise HTTPException(
            400,
            "Game is already over (winner: {}, draw: {})".format(
                game["winner"], game["is_draw"]
            ),
        )

    # Validate move
    if board[req.row][req.col] != "":
        raise HTTPException(400, "Cell not empty")
    if game["next_to_move"] != req.player:
        raise HTTPException(400, f"Not your turn. Next to move: {game['next_to_move']}")

    board = make_move(board, req.row, req.col, mark)
    moves.append(
        {
            "game_id": req.game_id,
            "player": req.player,
            "row": req.row,
            "col": req.col,
        }
    )
    winner = check_winner(board)
    draw = is_draw(board)
    finished_at = (
        datetime.utcnow().isoformat()
        if (winner or draw)
        else None
    )
    next_player = None

    if not (winner or draw):
        # Switch turn to other player (including AI)
        next_idx = (idx + 1) % 2
        next_player = players[next_idx]

    # AI move if needed
    if not winner and not draw and players[1] == "AI" and next_player == "AI":
        ai_row, ai_col = ai_pick(board)
        board = make_move(board, ai_row, ai_col, O_TOKEN)
        moves.append(
            {
                "game_id": req.game_id,
                "player": "AI",
                "row": ai_row,
                "col": ai_col,
            }
        )
        winner = check_winner(board)
        draw = is_draw(board)
        finished_at = (
            datetime.utcnow().isoformat()
            if (winner or draw)
            else None
        )
        next_player = players[0] if not (winner or draw) else None

    update_fields = {
        "board": save_board_to_str(board),
        "moves": json.dumps(moves),
        "winner": winner,
        "is_draw": draw,
        "next_to_move": next_player,
        "finished_at": finished_at,
        "status": (
            "finished" if winner or draw else "active"
        ),
    }

    supabase.table("games").update(update_fields).eq("id", req.game_id).execute()

    return GameState(
        game_id=req.game_id,
        board=board,
        players=players,
        next_to_move=next_player,
        winner=winner,
        is_draw=draw,
        last_move=req,
        created_at=datetime.fromisoformat(game["created_at"]),
        finished_at=finished_at,
        moves=moves,
    )


# PUBLIC_INTERFACE
@router.get("/game/{game_id}", summary="Get game state by ID", response_model=GameState)
async def get_game(game_id: str, current_user: User = Depends(verify_token)):
    """Fetches full state for current or past game."""
    import json

    resp = supabase.table("games").select("*").eq("id", game_id).single().execute()
    if not resp.data:
        raise HTTPException(404, "Game not found")
    game = resp.data

    return GameState(
        game_id=game["id"],
        board=json.loads(game["board"]),
        players=json.loads(game["players"]),
        next_to_move=game["next_to_move"],
        winner=game["winner"],
        is_draw=game["is_draw"],
        last_move=None,
        created_at=datetime.fromisoformat(game["created_at"]),
        finished_at=game["finished_at"],
        moves=json.loads(game["moves"]),
    )


# PUBLIC_INTERFACE
@router.get("/games", summary="List my games", response_model=list[GameHistoryItem])
async def list_my_games(current_user: User = Depends(verify_token)):
    """Return all games that the user was involved in."""
    import json

    name = current_user.username or current_user.email
    q1 = supabase.table("games").select("*").ilike("players", f"%{name}%").execute()
    res = []
    for game in q1.data:
        players = json.loads(game["players"])
        res.append(
            GameHistoryItem(
                game_id=game["id"],
                board=json.loads(game["board"]),
                players=players,
                winner=game["winner"],
                finished_at=game["finished_at"],
                is_draw=game["is_draw"],
            )
        )
    return res


# PUBLIC_INTERFACE
@router.get("/leaderboard", summary="Scoreboard for most wins", response_model=list[LeaderboardEntry])
async def leaderboard():
    """
    Aggregates win/loss/draw stats by username for leaderboard.
    """
    import json
    raw_games = (
        supabase.table("games")
        .select("*")
        .not_("status", "eq", "waiting")
        .execute()
    )
    stats = {}
    for game in raw_games.data:
        players = json.loads(game["players"])
        winner = game.get("winner")
        is_drawn = bool(game.get("is_draw"))
        for i, user in enumerate(players):
            if user is None or user == "AI":
                continue
            if user not in stats:
                stats[user] = {"wins": 0, "losses": 0, "draws": 0, "games_played": 0}
            stats[user]["games_played"] += 1
            if is_drawn:
                stats[user]["draws"] += 1
            elif winner == ("X" if i == 0 else O_TOKEN):
                stats[user]["wins"] += 1
            elif winner is not None:
                stats[user]["losses"] += 1
    out = [
        LeaderboardEntry(username=k, **v)
        for k, v in stats.items()
    ]
    out.sort(
        key=lambda e: (
            -e.wins,
            e.draws,
            -e.losses,
        )
    )
    return out
