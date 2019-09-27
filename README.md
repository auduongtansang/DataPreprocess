# DataPreprocess
Chương trình command line hỗ trợ các thao tác cơ bản trong tiền xử lý dữ liệu.

## Cài đặt
  - Yêu cầu: tải và cài đặt [Python 3.x](https://www.python.org/downloads/)
  - Chương trình chạy trực tiếp từ file mã nguồn thông qua tham số dòng lệnh, không cần cài đặt
  - Clone repo này (bao gồm mã nguồn và dữ liệu mẫu) bằng lệnh:
  ```bash
  git clone https://github.com/auduongtansang/DataPreprocess.git
  ```
  
## Tổng quan
  - Lệnh thực thi cơ bản sẽ có dạng:
  ```bash
  python3 --fileMãNguồn --tênThamSố thamSố01 thamSố02 ... --tênThamSố thamSố01 thamSố02 ...
  ```
  
  - Các tham số dưới đây là bắt buộc cho mọi câu lệnh:
  ```bash
  --input fileInput
  --output fileOutput
  --task tênThaoThác
  --prop danhSáchThuộcTính
  ```
  
## Chi tiết cách sử dụng
1. Chuẩn hóa min - max:
  ```bash
  --task minMaxNorm --newMinMax newMin newMax
  ```
2. Chuẩn hóa z - score:
  ```bash
  --task zScoreNorm
  ```
3. Rời rạc hóa - chia giỏ theo chiều rộng:
  ```bash
  --task widthBin --bin numberOfBins
  ```
4. Rời rạc hóa - chia giỏ theo chiều sâu:
  ```bash
  --task depthBin --bin numberOfBins
  ```
5. Xóa các mẫu thiếu thuộc tính:
  ```bash
  --task remove
  ```
6. Điền các thuộc tính bị thiếu bằng mean hoặc mode:
  ```bash
  --task fillIn
  ```

  - Ví dụ:
  ```bash
  python3 21_B1.py --input data.csv --output processed.csv --task minMaxNorm --newMinMax 0 1 --prop age
  ```

## Giấy phép
  - Đây chỉ là phần mềm đơn giản phục vụ học tập
  - Không vì mục đích kinh doanh

