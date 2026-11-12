# Pseudocode — tự hiện thực

```text
load_manifest(); assert content_page_count >= 30
for page in sources:
    raw = read(page)                         # theo định dạng, giữ page_id
    clean = normalize_unicode_and_whitespace(raw)
    if empty(clean): record_error(page); continue
    save_clean_page(page.id, clean, verified_metadata)

benchmark = load_questions_and_gold()        # đã tách dev/test, kiểm chứng evidence
for question in benchmark:
    assert evidence_found_in_gold_source(question)

for config in [fixed, sections, sections_plus_filter]:
    for page in clean_pages:
        chunks = split(page.text, config.chunking)
        for chunk in chunks:
            chunk.id = stable_hash(page.id, config, position, chunk.text)
            chunk.metadata = verified_document_source_page_and_filter_metadata(page)
    vectors = same_embedding_model.encode_documents(chunks)
    upsert_or_replace_index(config.id, chunks, vectors)
    verify_reingest_is_idempotent()
    for question in benchmark:
        filter = question.filter if config.uses_filter else none
        top3 = index.search(same_embedding_model.encode_query(question.text), filter, limit=3)
        save_full_trace(question, config, top3)
    calculate_hit_at_1_and_3_by_split()
    record_chunk_counts_time_cost()

# Mẫu vị trí coherence xác định trước; chấm thủ công coherence, metadata,
# grounding trên cùng mẫu và ghi lý do. So sánh dev, cố định cấu hình,
# rồi đánh giá test một lần. Chọn chiến lược theo tiêu chí đã công bố.
```

ID ổn định phải bao gồm phiên bản tài liệu/cấu hình và nội dung hoặc vị trí. Khi nội dung thay đổi, cần xóa các chunk cũ của tài liệu trước khi ghi bản mới; chỉ upsert ID mới không tự xóa bản cũ.
