import requests
import streamlit as st

class SteamClient:
    BASE_URL = "https://api.steampowered.com"

    def __init__(self):
        # Load the Steam API key from Streamlit secrets
        self.api_key = st.secrets["STEAM_API_KEY"]

    def get_most_played_games(self, count=10):
        """
        Fetches the most played games on Steam currently.
        Returns a list with game name, appid, and current player count.
        """
        url = f"{self.BASE_URL}/ISteamChartsService/GetMostPlayedGames/v1/"
        params = {"key": self.api_key}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        games = data.get("response", {}).get("ranks", [])
        return games[:count] if games else []

    def get_game_details(self, appid):
        """
        Fetches store details for a game by appid.
        """
        store_url = f"https://store.steampowered.com/api/appdetails"
        params = {"appids": appid}
        response = requests.get(store_url, params=params)
        response.raise_for_status()
        data = response.json()

        if str(appid) in data and data[str(appid)]["success"]:
            return data[str(appid)]["data"]
        return None
