import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pandas as pd

try:
    from zoneinfo import ZoneInfo
    JAKARTA_TZ = ZoneInfo("Asia/Jakarta")
except Exception:
    JAKARTA_TZ = timezone(timedelta(hours=7))

def append_jsonl(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def load_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    return rows

def normalize_post(post, query="", collected_at=""):
    # If it's a twikit Tweet object, extract dict representation
    if hasattr(post, "_legacy") or hasattr(post, "user"):
        legacy = getattr(post, "_legacy", {}) or {}
        user = getattr(post, "user", None)
        post = {
            "id": str(getattr(post, "id", "")),
            "text": getattr(post, "text", "") or legacy.get("full_text", ""),
            "created_at": str(getattr(post, "created_at", "") or legacy.get("created_at", "")),
            "lang": getattr(post, "lang", "") or legacy.get("lang", ""),
            "author_id": str(getattr(user, "id", "") if user else legacy.get("user_id_str", "")),
            "author_screen_name": getattr(user, "screen_name", "") if user else "",
            "author_name": getattr(user, "name", "") if user else "",
            "conversation_id": str(getattr(post, "conversation_id", "") or legacy.get("conversation_id_str", "")),
            "in_reply_to_status_id": str(getattr(post, "in_reply_to", "") or legacy.get("in_reply_to_status_id_str", "") or ""),
            "is_quote_status": bool(getattr(post, "is_quote_status", False) or legacy.get("is_quote_status", False)),
            "reply_count": int(getattr(post, "reply_count", 0) or legacy.get("reply_count", 0) or 0),
            "retweet_count": int(getattr(post, "retweet_count", 0) or legacy.get("retweet_count", 0) or 0),
            "favorite_count": int(getattr(post, "favorite_count", 0) or legacy.get("favorite_count", 0) or 0),
            "view_count": getattr(post, "view_count", None),
        }

    post_id = str(post.get("id", post.get("post_id", "")))
    raw_text = post.get("text", post.get("text_raw", post.get("full_text", "")))

    # Parse and format created_at into UTC and WIB
    created_at_raw = post.get("created_at", post.get("created_at_utc", ""))
    created_at_utc = ""
    created_at_wib = ""
    if created_at_raw:
        try:
            # Handle Twitter format: Mon Oct 26 12:09:10 +0000 2026
            dt = datetime.strptime(str(created_at_raw), "%a %b %d %H:%M:%S %z %Y")
            created_at_utc = dt.astimezone(timezone.utc).isoformat()
            created_at_wib = dt.astimezone(JAKARTA_TZ).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception:
            try:
                # Handle ISO format: 2026-10-26T12:09:10.000Z
                dt = datetime.fromisoformat(str(created_at_raw).replace("Z", "+00:00"))
                created_at_utc = dt.astimezone(timezone.utc).isoformat()
                created_at_wib = dt.astimezone(JAKARTA_TZ).strftime("%Y-%m-%d %H:%M:%S WIB")
            except Exception:
                created_at_utc = str(created_at_raw)

    # Determine content_type: reply, quote, quote_reply, original_post
    in_reply_to = post.get("in_reply_to_status_id") or post.get("in_reply_to")
    refs = post.get("referenced_tweets") or []
    if isinstance(refs, list):
        types = {ref.get("type") for ref in refs if isinstance(ref, dict)}
        is_reply = any(t == "replied_to" for t in types) or bool(in_reply_to)
        is_quote = any(t == "quoted" for t in types) or bool(post.get("is_quote_status"))
    else:
        is_reply = bool(in_reply_to)
        is_quote = bool(post.get("is_quote_status"))

    if is_reply and is_quote:
        content_type = "quote_reply"
    elif is_reply:
        content_type = "reply"
    elif is_quote:
        content_type = "quote"
    else:
        content_type = "original_post"

    metrics = post.get("public_metrics")
    if isinstance(metrics, dict):
        reply_count = metrics.get("reply_count", 0)
        retweet_count = metrics.get("retweet_count", 0)
        favorite_count = metrics.get("like_count", 0)
    else:
        reply_count = post.get("reply_count", 0)
        retweet_count = post.get("retweet_count", 0)
        favorite_count = post.get("favorite_count", 0)

    return {
        "post_id": post_id,
        "created_at_utc": created_at_utc,
        "created_at_wib": created_at_wib,
        "username": post.get("author_screen_name", ""),
        "author_name": post.get("author_name", ""),
        "author_id": str(post.get("author_id", "")),
        "text_raw": raw_text,
        "content_type": content_type,
        "lang_source": post.get("lang", post.get("lang_source", "")),
        "reply_count": reply_count,
        "retweet_count": retweet_count,
        "favorite_count": favorite_count,
        "in_reply_to_status_id": str(in_reply_to or ""),
        "conversation_id": str(post.get("conversation_id", "")),
        "keyword_query": query,
        "collected_at_utc": collected_at,
    }

def export_csv(rows, path, merge_existing=True):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows and not path.exists():
        print("Belum ada data untuk diekspor.")
        return

    new_df = pd.DataFrame(rows)
    if path.exists() and merge_existing:
        try:
            existing_df = pd.read_csv(path, dtype={"post_id": "string"})
            df = pd.concat([existing_df, new_df], ignore_index=True)
        except Exception:
            df = new_df
    else:
        df = new_df

    if "post_id" in df:
        df = df[df["post_id"].astype(str).str.len() > 0]
        df = df.drop_duplicates(subset=["post_id"], keep="first")

    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Dataset tersimpan: {path} | Total baris unik: {len(df)}")
