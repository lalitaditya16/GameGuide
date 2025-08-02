import requests

class RAWGClient:
    BASE_URL = "https://api.rawg.io/api"
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.rawg.io/api"

    def _get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        if params is None:
            params = {}
        params["key"] = self.api_key
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    
    def search_games(self, query="", genres=None, ordering=None, page_size=10, year=None):
        url = f"{self.BASE_URL}/games"
        params = {
            "key": self.api_key,
            "search": query,
            "page_size": page_size,
        }
        if genres:
            params["genres"] = genres
        if ordering:
            params["ordering"] = ordering
        if year:
            params["dates"] = f"{year}-01-01,{year}-12-31"

        print("[DEBUG] Final API Params:", params)  # ← use this to debug if needed

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])


    def get_game_details(self, game_id):
        return self._get(f"/games/{game_id}")

    def get_genres(self):
        return self._get("/genres").get("results", [])

    def get_platforms(self):
        return self._get("/platforms").get("results", [])

    def get_developers(self):
        return self._get("/developers").get("results", [])

    def get_publishers(self):
        return self._get("/publishers").get("results", [])

    def get_game_screenshots(self, game_id):
        return self._get(f"/games/{game_id}/screenshots").get("results", [])
