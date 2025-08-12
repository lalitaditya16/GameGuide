import requests
from difflib import get_close_matches

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

    



    def search_best_match(self, game_name, page_size=10):
        data = self._get("/games", {"search": game_name, "page_size": page_size})
        results = data.get("results", [])

        if not results:
            return None

        # First, try exact match (case-insensitive)
        for game in results:
            if game["name"].lower() == game_name.lower():
                return game

        # Fuzzy match using difflib
        names = [game["name"] for game in results]
        close_matches = get_close_matches(game_name, names, n=1, cutoff=0.6)

        if close_matches:
            best_match_name = close_matches[0]
            for game in results:
                if game["name"] == best_match_name:
                    return game

        # Fallback: return first result
        return results[0]
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

    def get_game_id_by_name(self, game_name):
        endpoint = "/games"
        params = {"search": game_name}
        data = self._get(endpoint, params)
        results = data.get("results", [])
        if results:
            return results[0]["id"]
        return None

    def get_achievements_by_game_id(self, game_id):
        achievements = []
        page = 1
        while True:
            data = self._get(f"/games/{game_id}/achievements", params={"page": page})
            achievements.extend(data.get("results", []))

            # Check if there are more pages
            if data.get("next"):
                page += 1
            else:
                break

        return achievements
    def get_games_with_steam_ids(self, year, page_size=20):
        endpoint = "/games"
        params = {
            "dates": f"{year}-01-01,{year}-12-31",
            "ordering": "-added",
            "page_size": page_size
        }
        games = self._get(endpoint, params).get("results", [])
        games_with_steam_ids = []

        for game in games:
            steam_id = None
        # Safely check for stores
            if "stores" in game and isinstance(game["stores"], list):
                for store in game["stores"]:
                    if store.get("store", {}).get("slug") == "steam":
                        url = store.get("url")
                        if url and "store.steampowered.com/app/" in url:
                            steam_id = url.split("/app/")[1].split("/")[0]
                            break

            games_with_steam_ids.append({
                "id": game.get("id"),
                "name": game.get("name"),
                "steam_id": steam_id
            })

        return games_with_steam_ids
