def load_keywords(path):
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line and not line.startswith("#")]

def build_query(keyword, replies_only=False):
    # Exclude reposts; retain original posts, replies, and quote posts.
    # Do not add lang:id so mixed Indonesian-English posts are not excluded solely
    # by X's language classifier. Relevance/language review happens downstream.
    safe = keyword.replace("\\", "\\\\")
    if replies_only:
        return f'({safe}) filter:replies -is:retweet'
    return f'({safe}) -is:retweet'
