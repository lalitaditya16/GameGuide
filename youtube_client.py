"""
YouTube Data API v3 client — free tier, 10 000 quota units/day.
Each search costs 100 units = up to 100 guide searches/day.
Get your key at: https://console.cloud.google.com/ → Enable YouTube Data API v3
Add to .env: YOUTUBE_API_KEY
"""

import requests
from typing import List, Dict


class YouTubeClient:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def is_available(self) -> bool:
        return bool(self.api_key)

    def search_game_guides(
        self,
        game_name: str,
        guide_type: str = "walkthrough",
        max_results: int = 5,
    ) -> List[Dict]:
        """Return a list of YouTube video dicts for the given game + guide type."""
        if not self.api_key:
            return []
        query = f"{game_name} {guide_type}"
        try:
            resp = requests.get(
                f"{self.BASE_URL}/search",
                params={
                    'key':               self.api_key,
                    'q':                 query,
                    'type':              'video',
                    'part':              'snippet',
                    'maxResults':        max_results,
                    'relevanceLanguage': 'en',
                    'videoCategoryId':   '20',  # Gaming
                    'order':             'relevance',
                },
                timeout=10,
            )
            resp.raise_for_status()
            items = resp.json().get('items', [])
            return [
                {
                    'video_id':  item['id']['videoId'],
                    'title':     item['snippet']['title'],
                    'channel':   item['snippet']['channelTitle'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'published': item['snippet']['publishedAt'][:10],
                    'embed_url': f"https://www.youtube.com/embed/{item['id']['videoId']}",
                }
                for item in items
            ]
        except Exception:
            return []

    @staticmethod
    def get_fallback_url(game_name: str, guide_type: str = "walkthrough") -> str:
        """Return a YouTube search URL when no API key is configured."""
        query = f"{game_name} {guide_type}".replace(' ', '+')
        return f"https://www.youtube.com/results?search_query={query}"
