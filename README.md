# LibrarySocket

## Cấu trúc message:
 - Đăng nhập: 01~username~password
    Server trả lời: 01~ok hoặc 01~error
 - Đăng ký: 02~username~password
    Server trả lời: 02~ok hoặc 02~error
 - Tra cứu:
    + F_ID: 03~id~"ID ở đây"
    + F_Name: 03~name~"Tên sách"
    + F_Type: 03~type~"Loại sách"
    + F_Author: 03~author~"Tên TG"
    Server trả lời: 03~ok hoặc 03~error
 - Xem sách: 04 (sách đã tra cứu)
    Server gửi toàn bộ nội dung
 - Tải sách: 05 (sách đã tra cứu)
    Server gửi toàn bộ nội dung
 - Thoát: exit

## Cấu trúc file
 ### Server
 - 1 file dùng để khởi tạo kết nối
 - 1 file dùng để tạo GUI chính
 - Các chức năng
 - 1 folder dùng để lưu cơ sở dữ liệu

 ### Client
 - 1 file dùng để khởi tạo kết nối
 - 1 file dùng để tạo GUI chính
 - Các chức năng
 - 1 folder dùng để lưu sách

## Các chức năng đã làm được ở câu lý thuyết:
 - Kết nối.
 - Quản lý kết nối.
 - Thoát.
 - Giao diện.


## Tra cứu:
 ### Server:
  - Lưu: ID sách, tên sách, thể loại, tên tác giả, năm xuất bản, địa chỉ file -> 1 table (1db).
    + Tra cứu bằng lệnh `F_ID 1234` hoặc `F_Name "Computer Network"`.
    + Tra cứu bằng lệnh `F_Type Computer Science` hoặc `F_Author "Jack London"`.

 - Đọc: Hiển thị sách lên GUI cho client.
 - Tải: Tải xuống theo định dạng txt.
 - Quản lý cơ sở dữ liệu:
    + Sách: lưu vào các file txt.
    + Thông tin sách: lưu vào cơ sở dữ liệu (SQL).