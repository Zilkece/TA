# Planning Script Scraping X
## Tugas Akhir: Analisis Sentimen Respons Masyarakat terhadap Fenomena Catcalling di Platform X

**Versi dokumen:** 1.1  
**Tanggal penyusunan:** 26 Oktober 2026  
**Bahasa data:** Bahasa Indonesia  
**Rentang waktu target:** 1 Januari 2025 sampai tanggal pengambilan data (sekitar 22 bulan per 26 Oktober 2026)  
**Platform:** X

---

## 1. Tujuan

Membangun pipeline Python yang mengumpulkan, membersihkan, dan menyimpan teks publik berbahasa Indonesia di X yang berkaitan dengan fenomena *catcalling*. Data akan digunakan sebagai korpus penelitian analisis sentimen, bukan untuk mengidentifikasi individu.

Pipeline dirancang agar:
- kode terpisah berdasarkan tanggung jawab (*clean code*);
- pengumpulan data dapat dilanjutkan tanpa mengulang seluruh proses;
- data mentah tetap disimpan untuk audit dan pemrosesan ulang;
- duplikasi dapat dideteksi;
- sumber dan waktu pengambilan data tercatat;
- kredensial tidak ditulis langsung di dalam kode.

## 2. Ruang Lingkup Data

### 2.1 Rentang waktu

- Mulai: `2026-01-01 00:00:00`
- Akhir: waktu pengambilan data (inklusif sesuai batas kueri yang digunakan).
- Zona waktu perlu ditetapkan secara konsisten. Rekomendasi: simpan waktu asli dari X dalam UTC jika tersedia, lalu buat kolom waktu Indonesia (`Asia/Jakarta`) untuk analisis.

**Catatan:** Tanggal pembuatan konten harus dibedakan dari tanggal scraping. Konten lama yang baru ditemukan saat scraping tetap masuk berdasarkan tanggal pembuatannya.

### 2.2 Kata kunci awal

Kata kunci perlu diuji dalam pencarian awal untuk melihat relevansi dan volume. Kandidat awal:

- `catcalling`
- `"cat calling"`
- `pelecehan verbal`
- `siulan` + konteks pelecehan
- `digoda di jalan`
- `pelecehan di jalan`
- `komentar seksual`

Kata kunci selain `catcalling` berpotensi menghasilkan konten yang tidak relevan. Simpan kata kunci pencarian pada konfigurasi terpisah dan lakukan penyaringan relevansi setelah pengumpulan.

Contoh kueri konseptual (sintaks final bergantung pada metode/endpoint yang dipakai):

```text
catcalling lang:id since:2026-01-01 until:YYYY-MM-DD
"cat calling" lang:id since:2026-01-01 until:YYYY-MM-DD
```

Jangan menganggap operator `lang:id` selalu sempurna. Deteksi bahasa otomatis juga dapat keliru untuk teks pendek, slang, atau campuran bahasa.

### 2.3 Jenis konten

Pisahkan jenis konten berikut pada kolom `content_type`:

| Jenis | Definisi operasional | Dipakai untuk analisis sentimen? |
|---|---|---|
| `original_post` | Postingan asli yang ditemukan melalui kata kunci | Ya, jika teks relevan |
| `reply` | Balasan terhadap postingan yang relevan | Ya |
| `quote` | Postingan yang mengutip postingan lain dan menambahkan teks | Ya |
| `repost` | Membagikan ulang postingan tanpa teks tambahan | Umumnya tidak untuk sentimen teks; dapat dicatat sebagai metadata |

**Keputusan awal yang direkomendasikan:** analisis sentimen dilakukan pada teks postingan asli, balasan, dan *quote posts*. *Repost* tanpa teks tambahan tidak memiliki teks opini baru, sehingga disimpan sebagai metadata keterlibatan saja atau dikeluarkan dari korpus sentimen. Jangan menggandakan teks postingan asli untuk setiap repost karena dapat mendistorsi distribusi sentimen.

### 2.4 Batasan akses

Gunakan hanya konten yang dapat diakses secara sah melalui metode dan akun yang memang berhak digunakan. Jangan mencoba melewati pembatasan akses, CAPTCHA, kontrol keamanan, atau batas laju. Metode berbasis cookie sesi dapat berubah sewaktu-waktu dan mungkin tidak didukung secara resmi; evaluasi kepatuhan terhadap ketentuan X dan persetujuan etik kampus sebelum menjalankannya.

---

## 3. Metode Autentikasi dan Pengelolaan Kredensial

Rencana awal menyebut `X_AUTH_TOKEN` dan `X_CT0`, tetapi implementasi starter yang menyertai dokumen menggunakan **API resmi X** dengan `X_BEARER_TOKEN`. Panduan X yang dipublikasikan melarang scraping dan otomasi situs di luar API resmi; karena itu, jangan gunakan cookie sesi untuk mengotomasi situs. Akses arsip penuh diperlukan untuk periode Januari 2025 hingga sekarang dan tidak tersedia pada semua tingkat akses. Pastikan akun/proyek memiliki akses yang sesuai dan konfirmasikan izin penggunaan data untuk penelitian machine learning sebelum pengumpulan.

Contoh `.env.example`:

```env
X_BEARER_TOKEN=
```

Simpan token hanya di `.env`, abaikan file itu melalui `.gitignore`, jangan pernah mencetak token ke log atau membagikannya. Jika akses ditolak atau batas API tercapai, hentikan proses dan ikuti petunjuk resmi—jangan mencoba mengakali batasan.

---

## 4. Struktur Folder yang Disarankan

```text
catcalling-x-sentiment/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── config/
│   ├── settings.yaml
│   └── keywords.txt
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   ├── interim/
│   │   └── .gitkeep
│   ├── processed/
│   │   └── .gitkeep
│   └── exports/
│       └── .gitkeep
├── logs/
│   └── .gitkeep
├── notebooks/
│   └── 01_data_exploration.ipynb
├── scripts/
│   ├── run_collection.py
│   ├── validate_dataset.py
│   └── export_dataset.py
├── src/
│   └── catcalling_x/
│       ├── __init__.py
│       ├── config.py
│       ├── auth.py
│       ├── query_builder.py
│       ├── collector.py
│       ├── pagination.py
│       ├── parser.py
│       ├── language_filter.py
│       ├── relevance_filter.py
│       ├── deduplication.py
│       ├── normalization.py
│       ├── storage.py
│       ├── checkpoint.py
│       ├── logging_config.py
│       └── schemas.py
├── tests/
│   ├── test_query_builder.py
│   ├── test_parser.py
│   ├── test_deduplication.py
│   ├── test_language_filter.py
│   └── test_relevance_filter.py
└── reports/
    ├── data_collection_log.md
    └── data_quality_report.md
```

### Tanggung jawab modul

| Modul | Tanggung jawab |
|---|---|
| `config.py` | Membaca konfigurasi, tanggal, zona waktu, dan lokasi file |
| `auth.py` | Memuat dan memvalidasi keberadaan kredensial tanpa mencetak nilainya |
| `query_builder.py` | Membentuk kueri berdasarkan kata kunci dan periode |
| `collector.py` | Mengambil hasil melalui metode yang dipilih |
| `pagination.py` | Mengelola halaman/cursor hasil dan mencegah pengambilan berulang |
| `parser.py` | Mengubah respons sumber menjadi format internal yang konsisten |
| `language_filter.py` | Menyaring kandidat teks berbahasa Indonesia |
| `relevance_filter.py` | Menandai konten yang benar-benar membahas catcalling |
| `deduplication.py` | Menghapus duplikasi berdasarkan ID konten |
| `normalization.py` | Menyiapkan teks untuk analisis tanpa merusak teks mentah |
| `storage.py` | Menyimpan data mentah dan data hasil pemrosesan |
| `checkpoint.py` | Menyimpan progres agar pengumpulan dapat dilanjutkan |
| `schemas.py` | Mendefinisikan kolom dan tipe data yang diharapkan |

---

## 5. Rancangan Pipeline

```text
Konfigurasi & validasi kredensial
              ↓
Muat kata kunci dan rentang tanggal
              ↓
Buat kueri per kata kunci dan rentang waktu
              ↓
Ambil hasil dengan pagination dan jeda yang wajar
              ↓
Simpan respons mentah + checkpoint
              ↓
Parse ke skema internal
              ↓
Filter tanggal dan kandidat bahasa Indonesia
              ↓
Tandai relevansi terhadap fenomena catcalling
              ↓
Gabungkan hasil dari seluruh kueri
              ↓
Deduplicasi berdasarkan ID konten
              ↓
Validasi kualitas dan simpan dataset
              ↓
Ekspor CSV/Parquet + laporan pengumpulan
```

### Rekomendasi pengumpulan bertahap

1. **Uji coba kecil:** jalankan beberapa kata kunci untuk rentang waktu pendek.
2. **Evaluasi hasil:** periksa sampel secara manual untuk mengukur relevansi, bahasa, duplikasi, dan jenis konten.
3. **Pengumpulan bertahap:** bagi periode Januari 2026 hingga tanggal terakhir menjadi interval waktu yang lebih kecil. Simpan checkpoint setiap interval.
4. **Penggabungan:** gabungkan hasil setiap interval dan kata kunci, lalu deduplikasi.
5. **Validasi akhir:** periksa rentang tanggal, kelengkapan kolom, jumlah duplikasi, dan proporsi data relevan.

Hindari pengulangan permintaan secara agresif. Terapkan batas laju yang sesuai, jeda, penanganan kegagalan, dan penghentian otomatis jika muncul respons pembatasan akses. Jangan mencoba mengakali pembatasan tersebut.

---

## 6. Skema Dataset

### 6.1 Kolom yang disarankan

| Kolom | Tipe | Keterangan |
|---|---|---|
| `post_id` | string | ID unik konten |
| `created_at_utc` | datetime | Waktu publikasi dalam UTC, jika tersedia |
| `created_at_wib` | datetime | Waktu publikasi dalam WIB |
| `content_type` | category | `original_post`, `reply`, `quote`, atau `repost` |
| `text_raw` | string | Teks asli yang dikumpulkan, sesuai akses yang diizinkan |
| `text_clean` | string | Teks yang dibersihkan untuk pemrosesan |
| `lang_source` | string/null | Label bahasa dari sumber, jika tersedia |
| `lang_detected` | string/null | Hasil deteksi bahasa lokal |
| `conversation_id` | string/null | ID percakapan, jika tersedia |
| `reply_to_id` | string/null | ID konten yang dibalas, jika tersedia |
| `quoted_post_id` | string/null | ID konten yang dikutip, jika tersedia |
| `repost_of_id` | string/null | ID konten yang dibagikan ulang, jika tersedia |
| `keyword_query` | string | Kata kunci/kueri yang menemukan konten |
| `source_url` | string/null | URL konten jika tersedia dan boleh disimpan |
| `collected_at_utc` | datetime | Waktu pengumpulan |
| `relevance_label` | category/null | Label relevansi hasil pemeriksaan |
| `sentiment_label` | category/null | Label sentimen setelah anotasi |
| `annotation_status` | category | Status anotasi, misalnya `unlabeled`, `reviewed` |

Tidak semua metode pengambilan data menyediakan semua metadata. Jika suatu field tidak tersedia, isi dengan nilai kosong dan dokumentasikan; jangan membuat nilai seolah-olah berasal dari X.

### 6.2 Format penyimpanan

- **Raw:** JSON Lines (`.jsonl`) jika respons mentah dapat disimpan sesuai ketentuan akses.
- **Interim/processed:** Parquet untuk pemrosesan yang efisien.
- **Export:** CSV UTF-8 untuk pemeriksaan manual dan penggunaan di perangkat analisis.
- **Checkpoint:** JSON kecil berisi kueri/interval yang sudah selesai, waktu, dan status—tanpa cookie atau rahasia.

Jangan menyimpan informasi profil yang tidak dibutuhkan untuk tujuan penelitian. Jika nama akun atau ID pengguna tidak diperlukan untuk analisis, hindari memasukkannya ke dataset final.

---

## 7. Pembersihan dan Seleksi Data

Pembersihan dilakukan pada salinan teks, bukan dengan menimpa `text_raw`.

1. Hapus duplikasi berdasarkan `post_id`.
2. Filter berdasarkan waktu publikasi, bukan waktu pengambilan.
3. Tandai kandidat bahasa Indonesia; periksa manual teks yang pendek atau campuran bahasa.
4. Buat `text_clean` dengan aturan yang terdokumentasi:
   - normalisasi whitespace;
   - tentukan perlakuan terhadap URL, mention, hashtag, emoji, dan tanda baca;
   - pertahankan negasi, kata slang, dan ekspresi yang dapat memengaruhi sentimen;
   - jangan menghapus kata kasar atau kata seksual secara otomatis karena dapat penting bagi konteks catcalling.
5. Tandai relevansi terhadap catcalling. Jangan mengandalkan kata kunci saja: sebuah konten bisa menyebut “catcalling” untuk edukasi, berita, sarkasme, atau konteks yang tidak membahas pengalaman/opini terkait.
6. Keluarkan spam, promosi tidak relevan, dan teks kosong berdasarkan aturan yang dicatat.
7. Simpan alasan eksklusi dalam laporan kualitas, bukan hanya menghapus data tanpa jejak.

---

## 8. Rencana Pelabelan Sentimen

Label sentimen tidak sebaiknya langsung disamakan dengan posisi pro/kontra terhadap istilah tertentu. Buat pedoman anotasi yang mempertimbangkan konteks.

Pilihan label awal yang bisa diuji:
- `negatif`: mengecam, menunjukkan dampak buruk, takut, marah, atau tidak nyaman terhadap catcalling;
- `netral`: informasi faktual, berita, pertanyaan informatif, atau teks tanpa polaritas yang jelas;
- `positif`: mendukung atau menilai positif tindakan catcalling;
- `ambigu`: sarkasme, konteks tidak cukup, atau makna yang tidak dapat ditentukan.

**Penting:** sentimen terhadap fenomena dan sentimen emosional penulis tidak selalu sama. Contoh, “Aku takut waktu itu di-catcall” mengungkapkan emosi negatif penulis sekaligus pengalaman negatif terhadap fenomena. Sebaliknya, kalimat yang mengecam catcalling dengan nada tenang belum tentu memiliki emosi negatif yang kuat. Tentukan sejak awal apakah penelitian mengukur **sentimen terhadap fenomena** atau **emosi yang diekspresikan penulis**.

Rencana anotasi:
1. Tulis pedoman label dan contoh positif/negatif/netral/ambigu.
2. Ambil sampel uji dan anotasi manual.
3. Jika memungkinkan, gunakan dua anotator untuk sebagian data dan ukur kesepakatan, misalnya Cohen's kappa.
4. Tinjau kasus sarkasme, kutipan berita, edukasi, dan teks campuran.
5. Pisahkan data latih, validasi, dan uji setelah label diperiksa. Hindari duplikasi konten yang sama tersebar di beberapa split.

---

## 9. Kualitas Data dan Evaluasi

Buat laporan yang sekurang-kurangnya berisi:

- jumlah konten yang dikumpulkan per kata kunci dan per bulan;
- jumlah berdasarkan `content_type`;
- jumlah konten yang lolos filter bahasa dan relevansi;
- jumlah duplikasi yang dihapus;
- jumlah teks kosong atau terlalu pendek;
- distribusi label sentimen setelah anotasi;
- contoh kesalahan pencarian yang umum;
- tanggal terakhir data berhasil diambil;
- kueri yang gagal, interval yang belum selesai, dan keterbatasan cakupan.

Pemeriksaan otomatis minimum:
- `post_id` tidak kosong untuk konten yang masuk dataset final;
- `created_at_utc` berada dalam periode target;
- tidak ada duplikasi `post_id` dalam tabel final;
- kolom wajib tersedia;
- teks tidak kosong untuk data yang akan dianalisis sentimennya;
- nilai `content_type` berada dalam kategori yang ditentukan.

---

## 10. Dependensi dan Konfigurasi

Dependensi awal yang mungkin diperlukan (sesuaikan dengan metode pengumpulan yang akhirnya dipilih):

```text
python-dotenv
pandas
pyarrow
PyYAML
tqdm
pytest
```

Tambahkan pustaka klien pengumpulan hanya setelah metode yang digunakan dipastikan dan ditinjau dari sisi akses serta ketentuan platform. Jangan memasang paket yang tidak diperlukan hanya untuk mengantisipasi kemungkinan.

Contoh `config/settings.yaml` (rentang mulai Januari 2025; tanggal akhir otomatis tanggal saat skrip dijalankan):

```yaml
collection:
  start_date: "2026-01-01"
  end_date: null  # null berarti tanggal pengambilan saat skrip dijalankan
  timezone: "Asia/Jakarta"
  language: "id"
  content_types:
    - original_post
    - reply
    - quote
  checkpoint_every: 1

storage:
  raw_dir: "data/raw"
  interim_dir: "data/interim"
  processed_dir: "data/processed"
  export_dir: "data/exports"

quality:
  deduplicate_by: "post_id"
  require_nonempty_text: true
```

`settings.yaml` adalah konfigurasi rancangan; implementasi final harus menyesuaikannya dengan kemampuan metode pengambilan data yang dipilih.

Contoh `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ipynb_checkpoints/
logs/*
!logs/.gitkeep
data/raw/*
!data/raw/.gitkeep
data/interim/*
!data/interim/.gitkeep
data/processed/*
!data/processed/.gitkeep
data/exports/*
!data/exports/.gitkeep
```

Dataset dan log bisa mengandung teks publik yang tetap sensitif dalam konteks penelitian. Jangan otomatis mengunggahnya ke repositori publik.

---

## 11. Tahapan Implementasi

| Tahap | Pekerjaan | Kriteria selesai |
|---|---|---|
| 1 | Tetapkan definisi data dan aturan etika | Definisi postingan, reply, quote, repost, bahasa, dan periode tertulis |
| 2 | Pilih metode akses | Metode dan batasan akses sudah ditinjau; tidak bergantung pada bypass |
| 3 | Siapkan proyek | Struktur folder, konfigurasi, `.env.example`, dan `.gitignore` siap |
| 4 | Implementasi kueri | Kueri per kata kunci dan periode dapat dibuat serta diuji |
| 5 | Implementasi pengambilan | Hasil dapat diambil bertahap, diparse, dan dilanjutkan dari checkpoint |
| 6 | Implementasi pemrosesan | Filter bahasa/relevansi, normalisasi, dan deduplikasi berjalan |
| 7 | Uji kualitas | Tes unit dan laporan kualitas tersedia |
| 8 | Pengumpulan penuh | Periode target diproses dengan catatan kegagalan dan cakupan |
| 9 | Anotasi sentimen | Pedoman label, label manual, dan pemeriksaan kesepakatan tersedia |
| 10 | Dataset final | Dataset anonim/minimal, terdokumentasi, dan siap untuk eksperimen model |

---

## 12. Risiko dan Mitigasi

| Risiko | Mitigasi |
|---|---|
| Perubahan struktur situs atau metode akses | Pisahkan modul kolektor dari parser dan dokumentasikan versi metode |
| Sesi kedaluwarsa atau akses ditolak | Hentikan proses dengan aman; jangan mencetak rahasia atau mengakali pembatasan |
| Hasil tidak mencakup seluruh postingan | Nyatakan sebagai keterbatasan; jangan mengklaim dataset lengkap |
| Banyak konten tidak relevan | Uji kata kunci, gunakan penyaringan relevansi, dan audit sampel |
| Bahasa salah terdeteksi | Gabungkan metadata bahasa, deteksi lokal, dan pemeriksaan sampel |
| Duplikasi lintas kata kunci | Deduplikasi berdasarkan ID konten |
| Ketimpangan label sentimen | Laporkan distribusi dan gunakan metrik per kelas saat evaluasi model |
| Data pribadi atau konteks sensitif | Minimalkan data, batasi akses, dan ikuti pedoman etik kampus |
| Kebocoran cookie | `.env` lokal, `.gitignore`, tanpa logging nilai rahasia, dan rotasi sesi bila bocor |

---

## 13. Keputusan yang Perlu Dikonfirmasi Sebelum Menulis Script

1. **Jenis konten:** apakah dataset utama mencakup postingan asli yang mengandung kata kunci, semua balasan pada postingan tersebut, dan *quote posts*; sedangkan repost tanpa komentar hanya dicatat sebagai metadata atau tidak dikumpulkan?
2. **Metode akses:** apakah kampus/penelitian mengizinkan penggunaan metode berbasis sesi/cookie, dan apakah Anda sudah menentukan pustaka atau alat yang akan dipakai? Cookie sesi tidak menjamin akses dan dapat tunduk pada perubahan maupun ketentuan platform.
3. **Bahasa:** apakah hanya teks yang sepenuhnya berbahasa Indonesia, atau teks campuran Indonesia–Inggris juga diterima?
4. **Skala dataset:** apakah ada target jumlah data (misalnya, semua hasil yang dapat diakses secara wajar atau target sampel tertentu)?
5. **Tujuan label:** apakah yang ingin diklasifikasikan adalah sentimen masyarakat **terhadap fenomena catcalling** (mendukung/mengecam/netral), atau emosi yang diekspresikan penulis (marah, takut, sedih, dan sebagainya)?

Setelah keputusan ini jelas, rancangan dapat diturunkan menjadi implementasi script yang sesuai tanpa mengunci asumsi penting terlalu dini.
