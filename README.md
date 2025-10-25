# Simple Bot

A modular and easy-to-use Discord bot written in Python.

## Features

- Modular command system (add/remove commands easily via the `commands/` folder)
- Example commands included:
  - **autoresponse**: Tự động phản hồi tin nhắn
  - **avatar_banner**: Lấy avatar hoặc banner người dùng
  - **moderation**: Các lệnh quản lý (kick, ban, clear, ...)
  - **nuke**: Xóa toàn bộ tin nhắn trong kênh
  - **ping**: Kiểm tra độ trễ của bot
  - **snipe**: Xem tin nhắn bị xóa gần nhất
  - **welcome**: Chào mừng thành viên mới

## Getting Started

### Prerequisites

- Python 3.8+
- Discord bot token

### Installation

1. **Clone this repository:**
    ```bash
    git clone https://github.com/viego-2077/simple-bot.git
    cd simple-bot
    ```

2. **Cài đặt các thư viện phụ thuộc:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Cấu hình bot:**

    - Mở file `config` và nhập token cùng prefix bạn muốn dùng:
      ```json
      {
        "token": "enter your token",
        "prefix": "enter your prefix"
      }
      ```

4. **Khởi động bot:**
    ```bash
    python main.py
    ```
    *(hoặc file chạy chính của bạn nếu không phải main.py)*

### Folder Structure

- `commands/` – Chứa các lệnh mở rộng cho bot
- `config` – File cấu hình với token và prefix
- `requirements.txt` – Danh sách các thư viện cần thiết

## Customization

Bạn có thể thêm/xóa/chỉnh sửa các file trong thư mục `commands/` để mở rộng chức năng cho bot của mình.

## License

MIT License. Xem file LICENSE để biết thêm chi tiết.

---

*Made with ❤️ by viego-2077*
