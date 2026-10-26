import time
import asyncio
from datetime import datetime, timezone
import requests
from twikit import Client

def tweet_to_dict(tweet):
    legacy = getattr(tweet, "_legacy", {}) or {}
    user = getattr(tweet, "user", None)
    return {
        "id": str(getattr(tweet, "id", "")),
        "text": getattr(tweet, "text", "") or legacy.get("full_text", ""),
        "created_at": str(getattr(tweet, "created_at", "") or legacy.get("created_at", "")),
        "lang": getattr(tweet, "lang", "") or legacy.get("lang", ""),
        "author_id": str(getattr(user, "id", "") if user else legacy.get("user_id_str", "")),
        "author_screen_name": getattr(user, "screen_name", "") if user else "",
        "author_name": getattr(user, "name", "") if user else "",
        "conversation_id": str(getattr(tweet, "conversation_id", "") or legacy.get("conversation_id_str", "")),
        "in_reply_to_status_id": str(getattr(tweet, "in_reply_to", "") or legacy.get("in_reply_to_status_id_str", "") or ""),
        "in_reply_to_screen_name": str(legacy.get("in_reply_to_screen_name", "") or ""),
        "is_quote_status": bool(getattr(tweet, "is_quote_status", False) or legacy.get("is_quote_status", False)),
        "reply_count": int(getattr(tweet, "reply_count", 0) or legacy.get("reply_count", 0) or 0),
        "retweet_count": int(getattr(tweet, "retweet_count", 0) or legacy.get("retweet_count", 0) or 0),
        "favorite_count": int(getattr(tweet, "favorite_count", 0) or legacy.get("favorite_count", 0) or 0),
        "view_count": getattr(tweet, "view_count", None),
        "raw_legacy": legacy,
    }

class XCookieClient:
    """Client pengumpul data X menggunakan session cookie (auth_token & ct0)."""

    def __init__(self, auth_token: str, ct0: str, language: str = "id-ID"):
        self.auth_token = auth_token
        self.ct0 = ct0
        self.client = Client(language=language)
        self.client.set_cookies({
            "auth_token": auth_token,
            "ct0": ct0,
        })

    async def search_page(self, query: str, product: str = "Latest", count: int = 20, cursor: str = None):
        return await self.client.search_tweet(query=query, product=product, count=count, cursor=cursor)

    async def collect_tweets(self, query: str, target_count: int = 50, product: str = "Latest", delay: float = 2.0, on_batch=None):
        collected_tweets = []
        seen_ids = set()

        batch_size = min(20, target_count)
        try:
            batch = await self.client.search_tweet(query=query, product=product, count=batch_size)
        except Exception as e:
            raise RuntimeError(f"Gagal melakukan pencarian di X: {e}")

        while batch:
            new_in_batch = []
            for t in batch:
                if t.id not in seen_ids:
                    seen_ids.add(t.id)
                    new_in_batch.append(t)
                    collected_tweets.append(t)
                    if len(collected_tweets) >= target_count:
                        break

            if on_batch:
                on_batch(new_in_batch, len(collected_tweets))

            if len(collected_tweets) >= target_count:
                break

            await asyncio.sleep(delay)
            try:
                batch = await batch.next()
            except Exception as e:
                print(f"[!] Selesai atau pagination berhenti: {e}")
                break

        return collected_tweets

class XApiClient:
    """Client resmi X API v2 (untuk pengguna token resmi bearer)."""

    def __init__(self, bearer_token, endpoint, timeout=30):
        self.endpoint = endpoint
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "CatcallingSentimentAcademicResearch/1.0",
        })

    def search_page(self, query, start_time, end_time, next_token=None, max_results=100):
        params = {
            "query": query,
            "start_time": start_time,
            "end_time": end_time,
            "max_results": max_results,
            "tweet.fields": "id,text,created_at,lang,conversation_id,referenced_tweets,public_metrics,author_id",
        }
        if next_token:
            params["next_token"] = next_token

        response = self.session.get(self.endpoint, params=params, timeout=self.timeout)
        if response.status_code == 429:
            reset = response.headers.get("x-rate-limit-reset")
            raise RuntimeError(
                "X API mengembalikan 429 (rate limit). Hentikan proses dan ikuti "
                f"waktu reset resmi. x-rate-limit-reset={reset or 'tidak tersedia'}"
            )
        if response.status_code in (401, 403):
            raise RuntimeError(
                f"Akses API ditolak ({response.status_code}). Periksa token, hak akses "
                "full-archive, dan endpoint pada dashboard developer X."
            )
        response.raise_for_status()
        return response.json()
