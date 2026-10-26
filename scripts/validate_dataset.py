from pathlib import Path
import pandas as pd

path = Path("data/processed/posts.csv")
if not path.exists():
    raise SystemExit("File data/processed/posts.csv belum tersedia. Jalankan kolektor terlebih dahulu.")

df = pd.read_csv(path, dtype={"post_id": "string"})
print("Jumlah baris:", len(df))
print("ID kosong:", int(df["post_id"].isna().sum()))
print("Duplikasi ID:", int(df["post_id"].duplicated().sum()))
print("Teks kosong:", int(df["text_raw"].fillna("").str.strip().eq("").sum()))
print("\nJenis konten:\n", df["content_type"].value_counts(dropna=False))
print("\nBahasa dari API:\n", df["lang_source"].value_counts(dropna=False).head(20))
print("\nRentang waktu:\n", df["created_at_utc"].min(), "->", df["created_at_utc"].max())
