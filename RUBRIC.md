# Rubric cá nhân — 100 điểm

Điểm dựa trên bằng chứng và khả năng tái lập, không dựa vào việc đạt Hit@3 cao. Một kết quả thấp nhưng giải thích trung thực vẫn có thể đạt điểm tốt.

| Hạng mục | Điểm | Bằng chứng |
|---|---:|---|
| Corpus và xử lý | 20 | ≥20 trang hợp lệ, manifest/giấy phép (8); đọc, chuẩn hóa, ghi lỗi, truy vết nguồn (12) |
| Ba chiến lược và lưu trữ | 20 | 3 cấu hình chạy được và ghi tham số (8); so sánh có kiểm soát (6); lưu vector, metadata, nạp lại không trùng hoặc giải thích minh chứng (6) |
| Benchmark và retrieval | 20 | ≥20 câu có evidence, tách dev/test trước thử nghiệm (10); trace và Hit@1/Hit@3 đúng, chạy đủ ba cấu hình (10) |
| Năm khía cạnh và phân tích | 25 | Retrieval (5), coherence có nhãn (5), metadata đủ/đúng và hữu dụng (5), grounding thủ công (5), data strategy impact & trade-off (5) |
| Tái lập và báo cáo | 15 | Lệnh chạy, model/chi phí, artifacts (8); kết luận, ví dụ lỗi, giới hạn và trình bày (7) |

Thiếu thành phần chỉ được chấm phần có bằng chứng; không tự giả định dữ liệu/test hoặc kết quả. Corpus chưa đủ 20 trang không đạt phần tương ứng; dưới ba chiến lược không đạt đầy đủ hạng mục chiến lược. Không dùng điểm test để tinh chỉnh rồi báo như holdout độc lập.
