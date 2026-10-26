# Catcalling X Sentiment — Data Collection Starter

Starter project for collecting public X posts relevant to catcalling for an academic sentiment-analysis project.

## Date range
Default: `2025-01-01` through the current date at runtime. The requested range is about 22 months as of 2026-10-26, not one year.

## Access method and important limitation
This starter uses the **official X API v2 full-archive search endpoint**. It does **not** use `X_AUTH_TOKEN` / `X_CT0` session cookies. X's published Terms and developer guidance prohibit automated scraping outside its published interfaces, including browser automation. Use the official API and only if your account/project has access to full-archive search. The full archive endpoint is not available on every access tier. Also verify whether your intended machine-learning/sentiment-analysis use is permitted under the current X Developer Agreement/Policy and obtain any required authorization before collecting or modeling data.

Set `X_BEARER_TOKEN` in `.env` using a token issued for your X developer project. Never commit credentials.

## What this starter does
- searches keyword matches from 2025-01-01 to runtime date;
- paginates API results and checkpoints each monthly query;
- stores JSONL raw API responses and CSV normalized rows;
- extracts content type (`original_post`, `reply`, `quote`, `quote_reply`);
- deduplicates by post ID;
- records collection time and query provenance;
- stops rather than trying to bypass access/rate limits.

## Important coverage caveats
- Search results are not a census of every post on X.
- Search by keyword finds replies/quotes that match the query; it does not automatically retrieve every reply to a relevant parent post if the reply itself does not contain a keyword.
- If the study requires all replies in relevant conversations, add a separately authorized API workflow based on conversation IDs, after checking the current endpoint/query capabilities and project tier.
- Mixed Indonesian-English posts may not always be tagged `id`; this starter does not restrict the API query to `lang:id`. Review language and relevance after collection. The starter records source language metadata but does not automatically certify that every row is Indonesian.
- Only fields returned by the API are saved; unavailable fields remain empty.

## Cara Menjalankan Scraper

1. Pastikan dependensi telah terinstall:
   ```bash
   pip install -r requirements.txt
   ```
2. Pastikan file `.env` sudah terisi dengan kredensial sesi Anda:
   ```env
   X_AUTH_TOKEN="your_auth_token"
   X_CT0="your_ct0"
   ```
3. Jalankan command scraping:
   - **Scrape default (50 tweet/komentar topik catcalling):**
     ```bash
     python scrape.py
     ```
   - **Tentukan jumlah data (misal 50, 100, dll):**
     ```bash
     python scrape.py --limit 50
     ```
   - **Khusus mengambil komentar/balasan saja:**
     ```bash
     python scrape.py --limit 50 --replies-only
     ```
   - **Menggunakan kata kunci custom:**
     ```bash
     python scrape.py --query "pelecehan verbal" --limit 50
     ```
   - **Validasi dataset yang telah terkumpul:**
     ```bash
     python scripts/validate_dataset.py
     ```

4. Output otomatis tersimpan di:
   - Data bersih (CSV): `data/processed/posts.csv`
   - Data mentah (JSONL): `data/raw/posts_raw.jsonl`

## Data ethics
Keep only fields needed for the research. Limit access to raw data, avoid publishing usernames or raw text unnecessarily, follow campus ethics guidance and the X Developer Agreement/Policy, and document query dates, API tier, missing intervals, and exclusions.
