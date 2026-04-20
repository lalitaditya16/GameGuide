"""
IGDB API client — free via Twitch Developer account.
Get credentials at: https://dev.twitch.tv/console/apps
Add to .env: IGDB_CLIENT_ID, IGDB_CLIENT_SECRET
"""

import time
import requests
from typing import Dict, List, Optional, Any


class IGDBClient:
    AUTH_URL = "https://id.twitch.tv/oauth2/token"
    BASE_URL  = "https://api.igdb.com/v4"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id     = client_id
        self.client_secret = client_secret
        self._token        = None
        self._token_expiry = 0.0

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    def _get_token(self) -> Optional[str]:
        if not self.client_id or not self.client_secret:
            return None
        if self._token and time.time() < self._token_expiry - 60:
            return self._token
        try:
            resp = requests.post(
                self.AUTH_URL,
                params={
                    'client_id':     self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type':    'client_credentials',
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            self._token        = data['access_token']
            self._token_expiry = time.time() + data['expires_in']
            return self._token
        except Exception:
            return None

    def is_available(self) -> bool:
        return bool(self._get_token())

    # ------------------------------------------------------------------
    # Internal POST helper
    # ------------------------------------------------------------------
    def _post(self, endpoint: str, body: str) -> List[Dict]:
        token = self._get_token()
        if not token:
            return []
        try:
            resp = requests.post(
                f"{self.BASE_URL}/{endpoint}",
                headers={
                    'Client-ID':     self.client_id,
                    'Authorization': f'Bearer {token}',
                    'Content-Type':  'text/plain',
                },
                data=body,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------
    def search_game(self, name: str) -> Optional[Dict]:
        results = self._post('games', f'''
            search "{name}";
            fields id, name, summary, storyline, rating,
                   first_release_date, genres.name, platforms.name,
                   cover.url, artworks.url, videos.video_id, videos.name,
                   websites.url, websites.category;
            limit 1;
        ''')
        return results[0] if results else None

    def get_game_summary(self, name: str) -> Dict[str, Any]:
        """Return a clean dict of game info suitable for display."""
        game = self.search_game(name)
        if not game:
            return {}
        return {
            'id':        game.get('id'),
            'name':      game.get('name', ''),
            'summary':   game.get('summary', ''),
            'storyline': game.get('storyline', ''),
            'rating':    round(game['rating'] / 10, 1) if game.get('rating') else None,
            'genres':    [g['name'] for g in game.get('genres', []) if isinstance(g, dict)],
            'platforms': [p['name'] for p in game.get('platforms', []) if isinstance(p, dict)],
            'videos':    game.get('videos', []),
            'cover':     (game.get('cover') or {}).get('url', '').replace('t_thumb', 't_cover_big'),
        }

    def get_trailer_id(self, name: str) -> Optional[str]:
        """Return a YouTube video_id for the first IGDB trailer, or None."""
        game = self.search_game(name)
        if not game:
            return None
        videos = game.get('videos', [])
        if videos and isinstance(videos[0], dict):
            return videos[0].get('video_id')
        return None

    def get_artworks(self, igdb_game_id: int, limit: int = 4) -> List[str]:
        results = self._post('artworks', f'''
            where game = {igdb_game_id};
            fields url;
            limit {limit};
        ''')
        return [
            r['url'].replace('t_thumb', 't_1080p')
            for r in results if r.get('url')
        ]
