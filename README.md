# Day 06 — Data Ingestion Engineering (Nguyễn Anh Tú, 2A202603434, L3A)

Pipeline truy xuất trên **Introduction to Computer Science (OpenStax)**, chương 6–8, so sánh ba chiến lược dữ liệu (A: chunk cố định, B: chia theo câu, C: B + lọc metadata) trên 23 câu benchmark tự viết. Báo cáo: `report/individual/2A202603434_NguyenAnhTu.md`.

Nguồn dữ liệu: *Introduction to Computer Science*, OpenStax, Rice University, CC BY 4.0. **Access for free at openstax.org** (https://openstax.org/details/books/introduction-computer-science). Chỉ dùng phần văn bản; hình minh họa có giấy phép riêng và không nằm trong repo. `data/pages.jsonl` là văn bản trích từ sách, giữ lại để tái lập (nguồn và giấy phép trong `data/manifest.json`).

## Cấu trúc

```text
data/manifest.json, data/pages.jsonl   # nguồn, quyền, trang, văn bản (data/raw/ không commit)
benchmark/questions.json               # 23 câu (17 dev / 6 test), evidence đã kiểm chứng
starter/src/                           # ingestion, chunking, embeddings, store, evaluation, run
scripts/                               # build_manifest, verify_benchmark, audit, finalize_logs
artifacts/                             # experiment_log.csv, selection_criteria.md
results/                               # trace top-3, summary, audit, run_meta
report/individual/                     # báo cáo cá nhân
```

## Cài đặt và chạy (macOS/Linux)

Yêu cầu: Docker, Python 3.11–3.14, khóa OpenRouter. Trên macOS, Docker Desktop cần quyền đọc thư mục chứa repo (System Settings → Privacy & Security → Files and Folders / Full Disk Access).

```bash
cd starter
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env     # điền OPENROUTER_API_KEY; đặt EMBEDDING_MODEL=openai/text-embedding-3-small
docker compose up -d --wait
python scripts/check_setup.py
cd ..
# (tùy chọn) dựng lại corpus: tải PDF từ trang OpenStax ở trên, đặt vào data/raw/openstax_intro_cs.pdf rồi
python scripts/build_manifest.py
python scripts/verify_benchmark.py
cd starter && python -m src.run              # nạp A, B; chạy A/B/C; in kết quả dev
python -m src.run --show-test                # in kết quả test đã lưu
cd .. && python scripts/finalize_logs.py     # audit grounding/metadata và experiment_log
```

`.env` chứa khóa API và **không được commit**. Phiên bản chính xác của model, Postgres, pgvector và thư viện nằm trong `results/run_meta.json`.

## Ghi chú trung thực

Một số nhãn thủ công (coherence, grounding) do AI chấm khởi tạo rồi tác giả xem lại; xem phần "Cách tạo nhãn" trong báo cáo. Benchmark nhỏ (17 dev / 6 test), kết quả chỉ minh họa trên corpus này.
