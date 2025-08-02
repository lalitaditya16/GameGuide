import requests

class RAWGClient:
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

    def search_games(self, search="", genres=None, platforms=None, ordering=None, page_size=10):
        params = {
            "search": search,
            "page_size": page_size
        }
        if genres:
            params["genres"] = genres
        if platforms:
            params["platforms"] = platforms
        if ordering:
            params["ordering"] = ordering

        return self._get("/games", params).get("results", [])

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
