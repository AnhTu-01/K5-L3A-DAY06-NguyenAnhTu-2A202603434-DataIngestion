# Báo cáo cá nhân — Day 6

## Dữ liệu và pipeline
- Chủ đề, nguồn/quyền, số trang và quy tắc tính trang:
- Chuẩn hóa, lỗi và giới hạn:
- Vectorizer, version, storage, lệnh chạy, chi phí:

## Cấu hình và benchmark
- A / B / C (tham số cụ thể, khác biệt duy nhất B–C):
- 20 câu: 15 dev / 5 test; cách chia và kiểm chứng evidence:
- Tiêu chí chọn chiến lược đã chốt trước khi xem test:

## Kết quả
| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian | Chi phí |
|---|---|---|---|---|---|---|

| Strategy | Coherence trung bình /2 (n) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N hoặc N/A) | Grounding 0/1/2 (số câu) và trung bình /2 |
|---|---|---|---|---|

Đường dẫn trace, nhãn thủ công và cách chọn mẫu:

## Phân tích và kết luận
- So sánh A–B và B–C; 2 ví dụ sai có ID câu và nguồn:
- Chiến lược chọn, đánh đổi, điều kiện áp dụng:
- Hạn chế của dữ liệu, nhãn, test nhỏ, đo thời gian/chi phí:
- Nếu làm lại hoặc mở rộng, cải tiến gì?
