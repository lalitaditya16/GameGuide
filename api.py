"""
GameGuide REST API — FastAPI wrapper around the RAWG game search
and Groq LLM recommendation engine.

Endpoints
---------
GET  /health            liveness check
POST /recommend         LLM-powered game recommendations
GET  /games/search      RAWG game search with optional filters
GET  /games/popular     top-rated games
POST /games/analyze     per-game LLM analysis
"""

import os
import logging
from typing import Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GameGuide API",
    description="REST interface for the GameGuide LLM recommendation engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RAWG_API_KEY = os.getenv("RAWG_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
RAWG_BASE    = "https://api.rawg.io/api"
GROQ_MODEL   = "llama-3.3-70b-versatile"


# ── LLM setup ────────────────────────────────────────────────────────────────

def _get_llm() -> ChatGroq:
    if not GROQ_API_KEY:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured")
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0.7,
        max_tokens=1024,
    )


# ── RAWG helpers ─────────────────────────────────────────────────────────────

def _rawg_get(endpoint: str, params: dict) -> dict:
    params["key"] = RAWG_API_KEY
    resp = requests.get(f"{RAWG_BASE}{endpoint}", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _search_games(
    query: str = "",
    genre: Optional[str] = None,
    platform: Optional[str] = None,
    ordering: str = "-rating",
    page_size: int = 10,
) -> list:
    params: dict = {"search": query, "ordering": ordering, "page_size": page_size}
    if genre:
        params["genres"] = genre
    if platform:
        params["platforms"] = platform
    return _rawg_get("/games", params).get("results", [])


def _slim(game: dict) -> dict:
    return {
        "id":               game.get("id"),
        "name":             game.get("name"),
        "rating":           game.get("rating"),
        "released":         game.get("released"),
        "genres":           [g["name"] for g in game.get("genres") or []],
        "platforms":        [p["platform"]["name"] for p in game.get("platforms") or []],
        "background_image": game.get("background_image"),
    }


# ── Request / response models ─────────────────────────────────────────────────

class RecommendRequest(BaseModel):
    query:    str            = Field(..., description="What kind of game are you looking for?")
    genre:    Optional[str]  = Field(None, description="RAWG genre slug, e.g. 'action', 'rpg'")
    platform: Optional[str]  = Field(None, description="RAWG platform id, e.g. '4' for PC")
    top_k:    int            = Field(5, ge=1, le=20)


class AnalyzeRequest(BaseModel):
    game_name: str = Field(..., description="Game title to analyze")


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Meta"])
def health():
    return {"status": "ok", "model": GROQ_MODEL, "rawg": bool(RAWG_API_KEY)}


@app.post("/recommend", tags=["Recommendations"])
def recommend(req: RecommendRequest):
    games = _search_games(
        query=req.query,
        genre=req.genre,
        platform=req.platform,
        page_size=req.top_k,
    )
    if not games:
        raise HTTPException(status_code=404, detail="No games matched the given filters")

    slim_games = [_slim(g) for g in games]

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a game recommendation assistant. Given the user's preference and a list "
            "of candidate games, recommend the best matches with a brief explanation for each.",
        ),
        (
            "human",
            "User preference: {query}\n\nCandidate games:\n{games}\n\n"
            "Give a concise recommendation (2-3 sentences per game, max 3 games).",
        ),
    ])
    chain = prompt | _get_llm() | StrOutputParser()
    recommendation = chain.invoke({"query": req.query, "games": str(slim_games)})

    return {"query": req.query, "recommendation": recommendation, "games": slim_games}


@app.get("/games/search", tags=["Games"])
def search_games(
    q:        str            = Query(..., description="Search term"),
    genre:    Optional[str]  = Query(None),
    platform: Optional[str]  = Query(None),
    limit:    int            = Query(10, ge=1, le=40),
):
    games = _search_games(query=q, genre=genre, platform=platform, page_size=limit)
    return {"results": [_slim(g) for g in games], "count": len(games)}


@app.get("/games/popular", tags=["Games"])
def popular_games(limit: int = Query(10, ge=1, le=40)):
    games = _search_games(ordering="-rating", page_size=limit)
    return {"results": [_slim(g) for g in games], "count": len(games)}


@app.post("/games/analyze", tags=["Recommendations"])
def analyze_game(req: AnalyzeRequest):
    results = _search_games(query=req.game_name, page_size=5)
    if not results:
        raise HTTPException(status_code=404, detail=f"Game '{req.game_name}' not found")

    game = results[0]
    slim = _slim(game)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a game analyst. Provide a concise analysis covering: what kind of player "
            "will enjoy this game, its main strengths, and 2-3 similar game recommendations.",
        ),
        ("human", "Analyze this game: {game_data}"),
    ])
    chain = prompt | _get_llm() | StrOutputParser()
    analysis = chain.invoke({"game_data": str(slim)})

    return {"game": slim, "analysis": analysis}
