import requests
import time
import logging
from typing import Dict, Any, Union
from datetime import datetime, timedelta
from urllib.parse import urljoin
from functools import wraps

import streamlit as st
from config import config, API_ENDPOINTS, ERROR_MESSAGES

# ───────────────────────── Set up logging ─────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────── Exceptions ───────────────────
class RAWGAPIError(Exception):
    pass


class RateLimitError(RAWGAPIError):
    pass


# ──────── Retry decorator ────────
def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, RAWGAPIError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay * (2 ** attempt))
                    else:
                        logger.error(f"All {max_retries} attempts failed.")
            raise last_exception
        return wrapper
    return decorator


# ───────────── RAWG API Client ─────────────
class RAWGClient:
    def __init__(self, api_key: str = None, base_url: str = None, user_agent: str = None):
        self.api_key = api_key or st.secrets["RAWG_API_KEY"]
        self.base_url = base_url or config.base_url
        self.user_agent = user_agent or "RAWGStreamlitApp/1.0"

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self.session.params = {"key": self.api_key}

        self.last_request_time = 0
        self.min_request_interval = 0.1

        logger.info(f"RAWGClient initialized at {self.base_url}")

    def _throttle(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _get(self, endpoint: str, params: dict = None):
        self._throttle()
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and "results" in data:
                return data
            else:
                logger.warning(f"Unexpected data structure from {url}: {data}")
                return {"results": []}
        except requests.RequestException as e:
            logger.error(f"Request to RAWG API failed: {e}")
            return {"results": []}

    def _wait_for_rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)

    @retry_on_failure(max_retries=config.max_retries, delay=config.retry_delay)
    def _make_request(self, endpoint: str, params: dict = None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
    
    # Always include the API key in the request params
        full_params = {"key": self.api_key}
        if params:
            full_params.update(params)

    # Respect rate limits
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)

        try:
            response = self.session.get(url, params=full_params)
            self.last_request_time = time.time()

            logger.debug(f"Request URL: {response.url}")
            logger.debug(f"Response Status: {response.status_code}")
            logger.debug(f"Response Content: {response.text}")

            if response.status_code != 200:
                logger.warning(f"RAWG API error: {response.status_code} - {response.text}")
                return {"results": []}

            data = response.json()
            if "results" not in data:
                logger.warning("RAWG API returned unexpected format.")
                return {"results": []}

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"RAWG API request failed: {e}")
            return {"results": []}


    def _with_spinner(self, msg, fn, *args, **kwargs):
        with st.spinner(msg):
            return fn(*args, **kwargs)

    def _cache_api_call(self, key, fn):
        @st.cache_data(ttl=config.cache_ttl)
        def cached(*args, **kwargs):
            return fn(*args, **kwargs)
        return cached

    def __getattr__(self, name):
        # auto-cache any public method that starts with 'get_'
        if name.startswith("get_"):
            return self._cache_api_call(name, getattr(self.__class__, name).__get__(self))
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")

    def get_games(self, **kwargs): return self._with_spinner("Fetching games...", self._make_request, API_ENDPOINTS["games"], kwargs)
    def get_game_details(self, game_id): return self._with_spinner("Fetching game details...", self._make_request, API_ENDPOINTS["game_detail"].format(id=game_id))
    def get_game_screenshots(self, game_id): return self._with_spinner("Fetching screenshots...", self._make_request, API_ENDPOINTS["game_screenshots"].format(id=game_id))
    def get_game_movies(self, game_id): return self._with_spinner("Fetching game movies...", self._make_request, API_ENDPOINTS["game_movies"].format(id=game_id))
    def get_game_achievements(self, game_id): return self._with_spinner("Fetching achievements...", self._make_request, API_ENDPOINTS["game_achievements"].format(id=game_id))
    def get_game_stores(self, game_id): return self._with_spinner("Fetching stores...", self._make_request, API_ENDPOINTS["game_stores"].format(id=game_id))
    def get_game_series(self, game_id): return self._with_spinner("Fetching series...", self._make_request, API_ENDPOINTS["game_series"].format(id=game_id))
    def get_developers(self, **kwargs): return self._with_spinner("Fetching developers...", self._make_request, API_ENDPOINTS["developers"], kwargs)
    def get_developer_details(self, developer_id): return self._with_spinner("Fetching developer details...", self._make_request, API_ENDPOINTS["developer_detail"].format(id=developer_id))
    def get_publishers(self, **kwargs): return self._with_spinner("Fetching publishers...", self._make_request, API_ENDPOINTS["publishers"], kwargs)
    def get_publisher_details(self, publisher_id): return self._with_spinner("Fetching publisher details...", self._make_request, API_ENDPOINTS["publisher_detail"].format(id=publisher_id))
    def get_platforms(self, **kwargs): return self._with_spinner("Fetching platforms...", self._make_request, API_ENDPOINTS["platforms"], kwargs)
    def get_platform_details(self, platform_id): return self._with_spinner("Fetching platform details...", self._make_request, API_ENDPOINTS["platform_detail"].format(id=platform_id))
    def get_genres(self, **kwargs): return self._with_spinner("Fetching genres...", self._make_request, API_ENDPOINTS["genres"], kwargs)
    def get_genre_details(self, genre_id): return self._with_spinner("Fetching genre details...", self._make_request, API_ENDPOINTS["genre_detail"].format(id=genre_id))
    def get_tags(self, **kwargs): return self._with_spinner("Fetching tags...", self._make_request, API_ENDPOINTS["tags"], kwargs)
    def get_creators(self, **kwargs): return self._with_spinner("Fetching creators...", self._make_request, API_ENDPOINTS["creators"], kwargs)
    def get_creator_details(self, creator_id): return self._with_spinner("Fetching creator details...", self._make_request, API_ENDPOINTS["creator_detail"].format(id=creator_id))
    def get_creator_roles(self, **kwargs): return self._with_spinner("Fetching creator roles...", self._make_request, API_ENDPOINTS["creator_roles"], kwargs)
    def get_stores(self, **kwargs): return self._with_spinner("Fetching stores list...", self._make_request, API_ENDPOINTS["stores"], kwargs)

    def search_games(self, query: str, **kwargs): return self.get_games(search=query, **kwargs)

    def get_popular_games(self, time_period: str = "month", **kwargs):
        now = datetime.now()
        if time_period == "week":
            start_date = now - timedelta(weeks=1)
        elif time_period == "month":
            start_date = now - timedelta(days=30)
        elif time_period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(weeks=1)
        date_range = f"{start_date:%Y-%m-%d},{now:%Y-%m-%d}"
        return self.get_games(dates=date_range, ordering="-rating", **kwargs)

    def get_trending_games(self, **kwargs): return self.get_games(ordering="-added", page_size=kwargs.get("page_size", 20), **kwargs)

    def close(self):
        if self.session:
            self.session.close()
            logger.info("RAWG client session closed")

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.close()
