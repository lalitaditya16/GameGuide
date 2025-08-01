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
        # Load API key from argument or Streamlit secrets
        self.api_key = api_key or st.secrets["RAWG_API_KEY"]

        # Use default config values if not provided
        self.base_url = base_url or config.base_url
        self.user_agent = user_agent or "RAWGStreamlitApp/1.0"

        # Prepare a session with default headers and parameters
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self.session.params = {"key": self.api_key}  # ✅ Always include API key in every request

        # Add simple rate-limiting support
        self.last_request_time = 0
        self.min_request_interval = 0.1  # seconds

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

            # ✅ Validate result structure to prevent issues
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
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        self._wait_for_rate_limit()

        url = urljoin(self.base_url, endpoint)
        params = params or {}
        params["key"] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=config.api_timeout)
            self.last_request_time = time.time()

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 404:
                return {}
            else:
                response.raise_for_status()
        except requests.exceptions.Timeout:
            raise RAWGAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise RAWGAPIError("Connection error")
        except requests.exceptions.RequestException as e:
            raise RAWGAPIError(str(e))

    # ───────────── Cached Methods with Spinner ───────────── #
    def _with_spinner(self, msg, fn, *args, **kwargs):
        with st.spinner(msg):
            return fn(*args, **kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_games(_self, **kwargs): return _self._with_spinner("Fetching games...", _self._make_request, API_ENDPOINTS["games"], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_details(_self, game_id): return _self._with_spinner("Fetching game details...", _self._make_request, API_ENDPOINTS["game_detail"].format(id=game_id))

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_screenshots(_self, game_id): return _self._with_spinner("Fetching screenshots...", _self._make_request, API_ENDPOINTS["game_screenshots"].format(id=game_id))

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_movies(_self, game_id): return _self._with_spinner("Fetching game movies...", _self._make_request, API_ENDPOINTS["game_movies"].format(id=game_id))

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_achievements(_self, game_id): return _self._with_spinner("Fetching achievements...", _self._make_request, API_ENDPOINTS["game_achievements"].format(id=game_id))

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_stores(_self, game_id): return _self._with_spinner("Fetching stores...", _self._make_request, API_ENDPOINTS["game_stores"].format(id=game_id))

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_series(_self, game_id): return _self._with_spinner("Fetching series...", _self._make_request, API_ENDPOINTS["game_series"].format(id=game_id))

    @st.cache_data(ttl=config.cache_ttl)
    def get_developers(_self, **kwargs): return _self._with_spinner("Fetching developers...", _self._make_request, API_ENDPOINTS["developers"], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_developer_details(_self, developer_id): return _self._with_spinner("Fetching developer details...", _self._make_request, API_ENDPOINTS["developer_detail"].format(id=developer_id))

    @st.cache_data(ttl=config.cache_ttl)
    def get_publishers(_self, **kwargs): return _self._with_spinner("Fetching publishers...", _self._make_request, API_ENDPOINTS["publishers"], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_publisher_details(_self, publisher_id): return _self._with_spinner("Fetching publisher details...", _self._make_request, API_ENDPOINTS["publisher_detail"].format(id=publisher_id))

    @st.cache_data(ttl=config.cache_ttl)
    def get_platforms(_self, **kwargs): return _self._with_spinner("Fetching platforms...", _self._make_request, API_ENDPOINTS["platforms"], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_platform_details(_self, platform_id): return _self._with_spinner("Fetching platform details...", _self._make_request, API_ENDPOINTS["platform_detail"].format(id=platform_id))

    @st.cache_data(ttl=config.cache_ttl)
    def get_genres(_self, **kwargs): return _self._with_spinner("Fetching genres...", _self._make_request, API_ENDPOINTS["genres"], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_genre_details(_self, genre_id): return _self._with_spinner("Fetching genre details...", _self._make_request, API_ENDPOINTS["genre_detail"].format(id=genre_id))

    @st.cache_data(ttl=config.cache_ttl)
    def get_tags(_self, **kwargs): return _self._with_spinner("Fetching tags...", _self._make_request, API_ENDPOINTS["tags"], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_creators(_self, **kwargs): return _self._with_spinner("Fetching creators...", _self._make_request, API_ENDPOINTS["creators"], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_creator_details(_self, creator_id): return _self._with_spinner("Fetching creator details...", _self._make_request, API_ENDPOINTS["creator_detail"].format(id=creator_id))

    @st.cache_data(ttl=config.cache_ttl)
    def get_creator_roles(_self, **kwargs): return _self._with_spinner("Fetching creator roles...", _self._make_request, API_ENDPOINTS["creator_roles"], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_stores(_self, **kwargs): return _self._with_spinner("Fetching stores list...", _self._make_request, API_ENDPOINTS["stores"], kwargs)

    # ──────────────── Utility wrappers (non-cached) ────────────────
    def search_games(_self, query: str, **kwargs): return _self.get_games(search=query, **kwargs)

    def get_popular_games(_self, time_period: str = "month", **kwargs):
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
        return _self.get_games(dates=date_range, ordering="-rating", **kwargs)

    def get_trending_games(_self, **kwargs): return _self.get_games(ordering="-added", page_size=kwargs.get("page_size", 20), **kwargs)

    # ──────────────── Cleanup ────────────────
    def close(self):
        if self.session:
            self.session.close()
            logger.info("RAWG client session closed")

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.close()
