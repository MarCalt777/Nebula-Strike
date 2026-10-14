import hashlib
import secrets
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from api.db import get_connection

app = FastAPI()

class UserIn(BaseModel):
    name: str
    password: str

class ScoreIn(BaseModel):
    score: int

def hash_password(password):
    data = password.encode()
    return hashlib.sha256(data).hexdigest()

@app.post("/register", status_code=201)
def register(user: UserIn):
    with get_connection() as conn:
        exists = conn.execute(
            "SELECT 1 FROM players WHERE name = ?",
            (user.name,)
        ).fetchone()
        if exists:
            raise HTTPException(400, "Vārds jau aizņemts")
        conn.execute(
            "INSERT INTO players (name, password_hash) VALUES (?, ?)",
            (user.name, hash_password(user.password))
        )
    return {"name": user.name}

@app.post("/login")
def login(user: UserIn):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT password_hash FROM players WHERE name = ?",
            (user.name,)
        ).fetchone()
        if row is None or row[0] != hash_password(user.password):
            raise HTTPException(401, "Nepareizs vārds vai parole")
        token = secrets.token_hex(16)
        conn.execute(
            "UPDATE players SET token = ? WHERE name = ?",
            (token, user.name)
        )
    return {"token": token}

@app.post("/scores", status_code=201)
def add_score(item: ScoreIn, token: str = Header()):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT name FROM players WHERE token = ?",
            (token,)
        ).fetchone()
        if row is None:
            raise HTTPException(401, "Nav pieteicies")
        conn.execute(
            "INSERT INTO scores (player, score) VALUES (?, ?)",
            (row[0], item.score)
        )
    return {"player": row[0], "score": item.score}

@app.get("/scores/top")
def top():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT player, score FROM scores ORDER BY score DESC LIMIT 10"
        ).fetchall()
    return [{"player": p, "score": s} for p, s in rows]

@app.get("/players/{name}/stats")
def player_stats(name: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*), MAX(score) FROM scores WHERE player = ?",
            (name,)
        ).fetchone()
    if row is None or row[0] == 0:
        raise HTTPException(404, "Spēlētājs nav atrasts vai nav spēļu")
    return {"player": name, "games_played": row[0], "best_score": row[1]}