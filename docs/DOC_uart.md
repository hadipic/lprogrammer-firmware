```markdown
# 📚 مستندات کامل پروتکل UART (دوحالته: Bootloader + Terminal)

## 🎯 معرفی

**UART** (Universal Asynchronous Receiver/Transmitter) یکی از پرکاربردترین پروتکل‌های ارتباط سریال است. در L-Programmer، پروتکل UART در دو حالت کار می‌کند:

1. **Bootloader Mode** - برای برنامه‌ریزی فلش میکروکنترلرها (ESP32, STM32)
2. **Terminal Mode** - برای ارتباط زنده و مانیتورینگ (Serial Monitor)

---

## 🔌 اتصال سخت‌افزاری

### پین‌های ESP32

| GPIO | سیگنال | کاربرد |
|------|--------|--------|
| **GPIO17** | TX | ارسال داده به Target |
| **GPIO16** | RX | دریافت داده از Target |
| **GPIO5** | RESET | ریست Target (برای Bootloader Mode) |
| **GND** | GND | زمین مشترک |

### اتصال به Target

```
ESP32 (L-Programmer)          Target (ESP32/STM32)
─────────────────────          ─────────────────────
GPIO17 (TX) ────────────────►  RX
GPIO16 (RX) ◄────────────────  TX
GPIO5  (RST) ───────────────►  EN/RESET
GND        ────────────────►  GND
```

---

## ⚡ مشخصات

| پارامتر | مقدار |
|---------|-------|
| **Baud Rate** | 300 - 921600 (قابل تنظیم) |
| **Data Bits** | 5, 6, 7, 8 |
| **Parity** | None, Even, Odd, Mark, Space |
| **Stop Bits** | 1, 1.5, 2 |
| **Flow Control** | None, RTS/CTS, XON/XOFF, DTR/DSR |
| **Buffer** | 2048 بایت (Ring Buffer) |
| **UART Debug** | UART_NUM_0 (GPIO1 TX, GPIO3 RX) |
| **UART Target** | UART_NUM_1 (GPIO17 TX, GPIO16 RX) |

---

## 🔄 دو حالت UART

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UART Protocol                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────┐    ┌─────────────────────────────────┐ │
│  │   حالت ۱: Bootloader Mode      │    │   حالت ۲: Terminal Mode        │ │
│  │   (پروگرامر)                   │    │   (Live Communication)          │ │
│  ├─────────────────────────────────┤    ├─────────────────────────────────┤ │
│  │  • نوشتن/خواندن فلش            │    │  • WebSocket Real-time          │ │
│  │  • Erase/Verify                │    │  • داده‌های زنده                │ │
│  │  • تشخیص دستگاه                │    │  • AT Commands                 │ │
│  │  • از طریق HTTP API            │    │  • از طریق WebSocket            │ │
│  │  • حالت پیش‌فرض                │    │  • Full Duplex                  │ │
│  └─────────────────────────────────┘    └─────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    اشتراک‌ها                                            │ │
│  │  • تنظیمات UART (Baud, Parity, DataBits, StopBits)                    │ │
│  │  • پین‌های TX/RX (GPIO17/16)                                          │ │
│  │  • UART Driver ESP-IDF                                                │ │
│  │  • Ring Buffer (2048 بایت)                                            │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 تنظیمات (Config)

### ساختار JSON

```json
{
  "protocol": "UART",
  "settings": {
    "baud": 115200,
    "dataBits": 8,
    "parity": "none",
    "stopBits": "1",
    "flowControl": "none",
    "rtsPin": -1,
    "ctsPin": -1,
    "bufferSize": 2048,
    "port": "uart1",
    "mode": "terminal"
  }
}
```

### فیلدها

| فیلد | نوع | پیش‌فرض | توضیح |
|------|-----|---------|-------|
| `baud` | uint32 | 115200 | سرعت ارتباط |
| `dataBits` | uint8 | 8 | تعداد بیت داده (5-8) |
| `parity` | string | "none" | parity (none/even/odd/mark/space) |
| `stopBits` | string | "1" | stop bits (1/1.5/2) |
| `flowControl` | string | "none" | کنترل جریان |
| `rtsPin` | int | -1 | پین RTS (-1 = غیرفعال) |
| `ctsPin` | int | -1 | پین CTS (-1 = غیرفعال) |
| `bufferSize` | uint32 | 2048 | اندازه بافر |
| `port` | string | "uart1" | uart0 (Debug) یا uart1 (Target) |
| `mode` | string | "terminal" | terminal یا bootloader |

---

## 🔄 جریان کار (Workflow)

### حالت Bootloader

```
┌──────────┐     HTTP API      ┌──────────┐     UART      ┌──────────┐
│ فرانت‌اند │ ────────────────► │  ESP32   │ ────────────► │  Target  │
│          │  POST /api/config │          │   داده‌های    │  (ESP32/ │
│          │  POST /api/connect│          │   HEX/BIN    │  STM32)  │
│          │  POST /api/program│          │              │          │
│          │  POST /api/read   │          │              │          │
│          │  POST /api/erase  │          │              │          │
│          │  POST /api/verify │          │              │          │
└──────────┘                    └──────────┘              └──────────┘
```

### حالت Terminal

```
┌──────────┐    WebSocket       ┌──────────┐     UART      ┌──────────┐
│ فرانت‌اند │ ◄───────────────► │  ESP32   │ ◄───────────► │  Target  │
│          │  داده‌های زنده     │          │   داده‌های    │  (ESP32/ │
│          │  AT Commands       │          │   زنده       │  STM32)  │
│          │  تنظیمات Config    │          │              │          │
└──────────┘                    └──────────┘              └──────────┘
```

---

## 📡 WebSocket Endpoint

### مسیر

```
ws://IP:8080/terminal       → JSON (کنترل و تنظیمات)
ws://IP:8080/uart/terminal  → Raw Data (داده خام)
```

### پیام‌ها

#### ارسال Config:

```json
{
  "cmd": "config",
  "baud": 115200,
  "dataBits": 8,
  "parity": "none",
  "stopBits": "1",
  "protocol": "uart",
  "port": "uart1"
}
```

#### ارسال داده:

```json
{
  "cmd": "send",
  "data": "AT\r\n"
}
```

#### پاسخ Config:

```json
{
  "status": "configured",
  "protocol": "UART"
}
```

---

## 🔧 توابع API

### توابع عمومی

| تابع | توضیح |
|------|--------|
| `uart_init()` | مقداردهی اولیه UART |
| `uart_deinit()` | غیرفعال کردن UART |
| `uart_connect()` | اتصال به Target |
| `uart_disconnect()` | قطع اتصال |
| `uart_config(json)` | تنظیم از JSON |

### توابع Bootloader Mode

| تابع | توضیح |
|------|--------|
| `uart_detect()` | تشخیص خودکار دستگاه |
| `uart_read_mem()` | خواندن حافظه |
| `uart_write_mem()` | نوشتن حافظه |
| `uart_erase()` | پاک کردن فلش |
| `uart_verify()` | تأیید نوشتن |

### توابع Terminal Mode

| تابع | توضیح |
|------|--------|
| `uart_send_raw()` | ارسال داده خام |
| `uart_send_data()` | ارسال داده متنی |
| `uart_config_ws()` | تنظیمات از WebSocket |
| `uart_terminal_poll()` | پردازش Ring Buffer |
| `uart_ws_on_open()` | هندلر باز شدن WebSocket |
| `uart_ws_on_close()` | هندلر بسته شدن WebSocket |
| `uart_ws_handler()` | هندلر داده WebSocket |

---

## 📊 ساختار فایل protocol_uart.c

```
protocol_uart.c
│
├── بخش ۱: هدرها و تعاریف
│   ├── #include ها
│   ├── TAG
│   ├── پین‌های TX/RX
│   ├── بافر Ring
│   └── uart_mode_t (enum)
│
├── بخش ۲: متغیرهای سراسری
│   ├── g_uart_mode
│   ├── g_config
│   └── ring_buffer
│
├── بخش ۳: توابع کمکی
│   ├── uart_parity_from_string()
│   ├── uart_stop_from_string()
│   └── uart_apply_config()
│
├── بخش ۴: Ring Buffer
│   ├── ring_buffer_init()
│   ├── ring_buffer_write()
│   ├── ring_buffer_read()
│   ├── ring_buffer_available()
│   └── ring_buffer_reset()
│
├── بخش ۵: Bootloader Mode
│   ├── uart_connect()
│   ├── uart_detect()
│   ├── uart_read_mem()
│   ├── uart_write_mem()
│   ├── uart_erase()
│   └── uart_verify()
│
├── بخش ۶: Terminal Mode
│   ├── uart_send_raw()
│   ├── uart_send_data()
│   ├── uart_config_ws()
│   ├── uart_terminal_poll()
│   └── uart_rx_interrupt()
│
├── بخش ۷: WebSocket Handler
│   ├── uart_ws_on_open()
│   ├── uart_ws_on_close()
│   └── uart_ws_handler()
│
├── بخش ۸: توابع API اصلی
│   ├── uart_init()
│   ├── uart_deinit()
│   └── uart_config()
│
└── بخش ۹: تعریف پروتکل
    └── g_uart_protocol
```

---

## 🧪 تست

### تست Terminal Mode

```bash
# 1. اتصال به WebSocket
wscat -c ws://192.168.4.1:8080/terminal

# 2. ارسال Config
{"cmd":"config","baud":115200,"dataBits":8,"parity":"none","stopBits":"1"}

# 3. ارسال داده
{"cmd":"send","data":"AT\r\n"}

# 4. ارسال داده خام (در مسیر /uart/terminal)
# مستقیماً: AT\r\n
```

### تست Bootloader Mode

```bash
# 1. تنظیم Config
curl -X POST http://192.168.4.1/api/config \
  -H "Content-Type: application/json" \
  -d '{"protocol":"UART","settings":{"baud":115200,"port":"uart1","mode":"bootloader"}}'

# 2. اتصال
curl -X POST http://192.168.4.1/api/connect \
  -H "Content-Type: application/json" \
  -d '{"device":"ESP32","family":"ESP32","voltage":33}'

# 3. تشخیص
curl -X POST http://192.168.4.1/api/detect

# 4. خواندن
curl -X POST http://192.168.4.1/api/read \
  -H "Content-Type: application/json" \
  -d '{"address":0x0,"size":1024}'
```

---

## 🐛 عیب‌یابی

| مشکل | علت | راه‌حل |
|------|------|--------|
| **WebSocket وصل نمی‌شود** | سرور روشن نیست | چک `mg_mgr_poll` |
| **داده ارسال نمی‌شود** | UART init نشده | چک `uart_initialized` |
| **داده دریافت نمی‌شود** | RX پین اشتباه | چک GPIO16 |
| **Baud اشتباه** | Config اعمال نشده | چک `uart_apply_config` |
| **Buffer پر می‌شود** | بافر کوچک | افزایش `bufferSize` |
| **خطای `undefined reference`** | توابع پیاده‌سازی نشده | اضافه کردن `uart_send_raw` و ... |

---

## 📚 منابع

- **ESP-IDF UART Driver** - مستندات رسمی
- **ESP32 Technical Reference Manual**
- **STM32 UART Bootloader** - AN3155

---

**پایان مستندات UART** ✅
<<<<<<< HEAD
```
=======
```
>>>>>>> fffed0822197c4e905bbc48de0687a548f7bac43
