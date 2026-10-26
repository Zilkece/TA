from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]

def load_settings():
    load_dotenv(ROOT / ".env")
    path = ROOT / "config" / "settings.yaml"
    settings = yaml.safe_load(path.read_text(encoding="utf-8"))
    
    auth_token = os.getenv("X_AUTH_TOKEN", "").strip()
    ct0 = os.getenv("X_CT0", "").strip()
    bearer_token = os.getenv("X_BEARER_TOKEN", "").strip()
    
    if not (auth_token and ct0) and not bearer_token:
        raise RuntimeError(
            "Kredensial X belum diisi di .env! "
            "Pastikan X_AUTH_TOKEN dan X_CT0 sudah diisi di file .env."
        )
        
    settings["_root"] = ROOT
    settings["_auth_token"] = auth_token
    settings["_ct0"] = ct0
    settings["_bearer_token"] = bearer_token
    return settings
