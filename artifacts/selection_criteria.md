# Tiêu chí chọn chiến lược (cố định trước khi chạy thí nghiệm, trước khi đọc kết quả test)

Chỉ dùng kết quả **dev** để chọn. Test chỉ để báo cáo, không dùng để chọn hay chỉnh tham số.

1. Evidence Hit@3 trên dev cao hơn thắng; chênh <= 1 câu coi là hòa (mẫu nhỏ).
2. Nếu hòa: Hit@1 trên dev cao hơn.
3. Nếu vẫn hòa: điểm chunk coherence trung bình (audit thủ công, 10 vị trí cố định) cao hơn.
4. Nếu vẫn hòa: ít tài nguyên hơn (số chunk, thời gian ingest, chi phí embedding).

C so với B chỉ đánh giá trên các câu có filter (q15, q18 dev; q20 test); mẫu rất nhỏ nên chỉ mô tả, không kết luận tổng quát.
Cấu hình: A = cố định 500 ký tự/overlap 50; B = gom theo câu <= 500 ký tự (gộp mảnh < 80); C = B + lọc metadata (chapter/section) chỉ khi câu hỏi có filter.
