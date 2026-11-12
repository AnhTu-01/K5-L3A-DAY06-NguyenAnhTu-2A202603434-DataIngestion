# Thiết kế benchmark — 20 câu hỏi có bằng chứng

Bộ câu hỏi do **mỗi học viên tự viết theo corpus của mình**, trước khi chạy thử. Mục tiêu là kiểm tra các lỗi khác nhau, không chỉ tìm một câu trùng từ khóa trong tài liệu. Mỗi câu gán **một loại chính**; nếu thỏa nhiều loại, chọn loại thể hiện mục tiêu kiểm tra chính.

| Loại câu | Số câu trong bộ tối thiểu | Kiểm tra gì? |
|---|---:|---|
| Thông tin trực tiếp | 6 | Tìm được một thông tin rõ ràng có trong nguồn |
| Paraphrase | 5 | Tìm được bằng chứng khi câu hỏi diễn đạt khác nguồn nhưng giữ nguyên ý |
| Điều kiện / ngoại lệ | 5 | Giữ được đối tượng, điều kiện, giới hạn hoặc ngoại lệ cần thiết |
| Phân biệt theo metadata | 4 | Dùng metadata đã biết để phân biệt các phạm vi có thể gây nhầm lẫn |
| **Tổng** | **20** | |

Tách trước **15 dev / 5 test**, mỗi loại xuất hiện trong cả hai tập; câu test thứ năm tự chọn. Nếu có hơn 20 câu, chỉ cần bộ tối thiểu đáp ứng ma trận; ghi rõ cách phân chia các câu bổ sung. Không sửa câu test hoặc điều chỉnh chiến lược dựa vào test. Nếu đã xem test để sửa bài, báo rõ và tạo tập test mới nếu có thể.

Câu metadata cần có ít nhất một trường lọc hữu ích và có giá trị đáng tin từ nguồn, ví dụ `year`, `section`, `category`, `audience`, `language` hoặc `version`. Chuẩn bị ít nhất hai giá trị hoặc phạm vi có thể phân biệt trong corpus; không tạo giá trị giả để filter đạt điểm. Bốn câu có filter, trong đó ít nhất một câu thuộc test. Giá trị filter là input được cung cấp từ câu hỏi hoặc ngữ cảnh **trước khi truy xuất**, không lấy từ gold để đưa cho hệ thống. Nếu một câu không có filter, chạy C không filter cho câu đó và ghi rõ.

## Gold và kiểm chứng

Mỗi câu ghi: `id`, `type`, `split`, `question`, `expected_answer`, `gold_source_id`, `gold_page`, `evidence_quote` và `filter` nếu dùng. Trường `gold_page` là vị trí truy vết: số trang PDF hoặc ID đơn vị đã định nghĩa đối với tài liệu không có trang.

Trước khi chạy, kiểm tra:

- Đoạn evidence tồn tại ở nguồn/trang và **đủ** để hỗ trợ đáp án, kể cả điều kiện/ngoại lệ.
- Câu có thể trả lời từ corpus; không cần kiến thức bên ngoài. Không đưa đáp án hoặc gold source vào query/filter.
- Nếu có nhiều bằng chứng hợp lệ, ghi tất cả nguồn/trang/đoạn và chấp nhận một trong số đó khi chấm. Khi evidence trải nhiều chunk, ghi rõ cách đánh giá; chỉ số chính vẫn theo định nghĩa [GUIDE.md](GUIDE.md).
- Nêu cách tự kiểm tra evidence, người gán nhãn, các câu khó/nhãn chưa chắc và nguồn có thể hạn chế tái phân phối.

Xem [data/format-example.json](data/format-example.json) để tham khảo cấu trúc đơn giản; file đó chỉ minh họa định dạng, không phải benchmark hoàn chỉnh. Phương pháp đo **retrieval, coherence, metadata, grounding và tác động chiến lược** được quy định ở [GUIDE.md](GUIDE.md). Rubric chấm bài 100 điểm nằm ở [RUBRIC.md](RUBRIC.md).
