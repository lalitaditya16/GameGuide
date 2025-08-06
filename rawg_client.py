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

    def search_games_browse(self, query="", ordering="-added", genre=None, platform=None, page_size=20):
        params = {
            "key": self.api_key,
            "search": query,
            "ordering": ordering,
            "page_size": page_size,
        }
        if genre:
            params["genres"] = genre
        if platform:
            params["platforms"] = platform

        url = f"{self.BASE_URL}/games"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])

    def search_games_analytics(self, ordering="-rating", genres=None, platforms=None, year=None, page_size=40):
        params = {
            "key": self.api_key,
            "ordering": ordering,
            "page_size": page_size,
        }
        if genres:
            params["genres"] = genres
        if platforms:
            params["platforms"] = platforms
        if year:
            params["dates"] = f"{year}-01-01,{year}-12-31"

        url = f"{self.BASE_URL}/games"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])

    def search_games_popular(self, ordering="-rating", dates=None, page_size=6):
        endpoint = f"{self.BASE_URL}/games"
        params = {
            "key": self.api_key,
            "ordering": ordering,
            "page_size": page_size,
        }
        if dates:
            params["dates"] = dates

        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        games = data.get("results", [])
        return [
            {
                "name": game.get("name"),
                "rating": game.get("rating"),
                "released": game.get("released"),
                "platforms": [p["platform"]["name"] for p in game.get("platforms", []) if p.get("platform")],
                "genres": [g["name"] for g in game.get("genres", [])],
                "background_image": game.get("background_image"),
            }
            for game in games
        ]


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

    def get_achievements_by_game_name(self, game_name, page_size=40):
        """Search for a game by name and fetch its achievements."""
    # Step 1: Search for the game
        search_results = self.search_games_browse(query=game_name, page_size=1)
        if not search_results:
            return []

        game_id = search_results[0]["id"]

    # Step 2: Fetch achievements using the game ID
        params = {
            "key": self.api_key,
            "page_size": page_size
        }
        response = requests.get(f"{self.BASE_URL}/games/{game_id}/achievements", params=params)
        response.raise_for_status()
        return response.json().get("results", [])
