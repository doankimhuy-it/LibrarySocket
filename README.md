# LibrarySocket

## Cấu trúc message:
 - Đăng nhập: ...
 - Đăng ký: ...
 - Tra cứu: ...
 - Xem sách: ...
 - Tải sách: ...
 - Thoát: ...

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