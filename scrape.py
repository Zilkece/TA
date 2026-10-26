#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script utama untuk scraping komentar dan tweet topik catcalling di X.
Dapat langsung dijalankan dengan command:
    python scrape.py
atau dengan opsi khusus:
    python scrape.py --limit 50
    python scrape.py --limit 50 --replies-only
    python scrape.py --query "pelecehan verbal" --limit 100
"""

import sys
from pathlib import Path

# Tambahkan direktori root ke sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.catcalling_x.run_collection import main

if __name__ == "__main__":
    main()
