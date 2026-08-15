# 📊 کد کامل UART با دو حالت Bootloader و Terminal
┌─────────────────────────────────────────────────────────────────────────────┐
│                         فرانت‌اند (Terminal Page)                          │
│                                                                             │
│  1. کاربر روی دکمه 🔌 Connect کلیک می‌کند                                 │
│                                                                             │
│  2. فرانت‌اند ابتدا Config را از طریق HTTP API ارسال می‌کند:              │
│     POST /api/config                                                       │
│     {                                                                      │
│       "protocol": "UART",                                                  │
│       "settings": {                                                        │
│         "baud": 115200,                                                    │
│         "dataBits": 8,                                                     │
│         "parity": "none",                                                  │
│         "stopBits": "1",                                                   │
│         "port": "uart1",                                                   │
│         "mode": "terminal"   ← می‌گوید Terminal Mode است                   │
│       }                                                                    │
│     }                                                                      │
│                                                                             │
│  3. ESP32 Config را دریافت می‌کند و می‌فهمد که Terminal Mode است           │
│     → WebSocket Server را شروع می‌کند                                      │
│     → تسک‌های UART را ایجاد می‌کند                                        │
│                                                                             │
│  4. فرانت‌اند به WebSocket متصل می‌شود                                     │
│     ws://192.168.1.17:8080/terminal                                        │
│                                                                             │
│  5. ارتباط برقرار است (Full Duplex)                                       │
│                                                                             │
│  6. کاربر روی 🔌 Disconnect کلیک می‌کند                                   │
│                                                                             │
│  7. فرانت‌اند WebSocket را می‌بندد                                         │
│                                                                             │
│  8. ESP32 WebSocket را می‌بندد                                             │
│     → تسک‌ها متوقف می‌شوند                                                 │
│     → UART Deinit می‌شود                                                   │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         فرانت‌اند (Terminal Page)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📌 مرحله ۱: کاربر روی دکمه 🔌 Connect کلیک می‌کند                        │
│                                                                             │
│  📌 مرحله ۲: فرانت‌اند Config را از طریق HTTP API ارسال می‌کند            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  POST /api/config                                                   │   │
│  │  {                                                                  │   │
│  │    "protocol": "UART",                                              │   │
│  │    "settings": {                                                    │   │
│  │      "baud": 115200,                                                │   │
│  │      "dataBits": 8,                                                 │   │
│  │      "parity": "none",                                              │   │
│  │      "stopBits": "1",                                               │   │
│  │      "port": "uart1",                                               │   │
│  │      "mode": "terminal"   ← کلید اصلی!                             │   │
│  │    }                                                                │   │
│  │  }                                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  📌 مرحله ۳: ESP32 Config را دریافت می‌کند                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  I (xxxx) UART: ⚙️ UART Config: {"baud":115200,...,"mode":"terminal"} │   │
│  │  I (xxxx) UART: 🔌 Terminal mode requested                         │   │
│  │  I (xxxx) UART: 🔌 Starting Terminal WebSocket Server...           │   │
│  │  I (xxxx) UART: 🌐 Terminal WebSocket: ws://192.168.4.1:8080/terminal │   │
│  │  I (xxxx) UART: 📡 UART0 → WebSocket task started                  │   │
│  │  I (xxxx) UART: 📡 UART1 → WebSocket task started                  │   │
│  │  I (xxxx) UART: ✅ Terminal mode ACTIVE                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  📌 مرحله ۴: فرانت‌اند پاسخ Config را دریافت می‌کند                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  {"status":"configured","protocol":"UART"}                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  📌 مرحله ۵: فرانت‌اند به WebSocket متصل می‌شود                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ws://192.168.1.17:8080/terminal                                   │   │
│  │  ✅ WebSocket connected!                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  📌 مرحله ۶: ارتباط Full Duplex برقرار است! 🎉                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  📤 کاربر تایپ می‌کند: Hello                                       │   │
│  │  📥 اکو دریافت می‌کند: Hello                                       │   │
│  │  📤 کاربر تایپ می‌کند: AT                                          │   │
│  │  📥 اکو دریافت می‌کند: AT                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  📌 مرحله ۷: کاربر روی 🔌 Disconnect کلیک می‌کند                         │
│                                    │                                        │
│                                    ▼                                        │
│  📌 مرحله ۸: WebSocket بسته می‌شود                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  I (xxxx) UART: 🔌 WebSocket CLOSE received!                       │   │
│  │  I (xxxx) UART: UART deinit for Terminal                           │   │
│  │  I (xxxx) UART: 📡 UART0 task stopped                              │   │
│  │  I (xxxx) UART: 📡 UART1 task stopped                              │   │
│  │  I (xxxx) UART: 🔌 Terminal Mode DEACTIVATED                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  📌 مرحله ۹: فرانت‌اند وضعیت را نمایش می‌دهد                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ⚪ Disconnected                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

I (xxxx) UART: ═══ UART Init ═══
I (xxxx) UART: 📡 Target UART: TX=GPIO17, RX=GPIO16
I (xxxx) UART: ✅ UART initialized (baud=115200)
---

## 📊 خلاصه تغییرات

| تغییر | توضیح |
|-------|-------|
| **`uart_mode_t`** | سه حالت: IDLE, BOOTLOADER, TERMINAL |
| **`g_uart_mode`** | متغیر نگهدارنده حالت فعلی |
| **Bootloader Mode** | `uart_connect()` + `uart_detect()` + توابع Read/Write |
| **Terminal Mode** | WebSocket Handler + داده‌های زنده |
| **RESET (GPIO5)** | برای ورود به Bootloader |
| **Echo** | قابلیت اکو در ترمینال |
| **Timeout** | تایم‌اوت قابل تنظیم از فرانت‌اند |
| **توابع کمکی** | `uart_is_bootloader_mode()`, `uart_is_terminal_mode()` |

---

## 🚀 نحوه تست

### Bootloader Mode:
```bash
curl -X POST http://192.168.1.17/api/config \
  -H "Content-Type: application/json" \
  -d '{"protocol":"UART","settings":{"baud":115200,"dataBits":8,"parity":"none","stopBits":"1","port":"uart1"}}'


  curl -X POST http://192.168.1.17/api/connect \
  -H "Content-Type: application/json" \
  -d '{"device":"ESP32","family":"ESP32","voltage":33}'



# 1. قطع اتصال
curl -X POST http://192.168.1.17/api/disconnect -H "Content-Type: application/json" -d '{}'

# 2. حالا در فرانت‌اند روی Connect کلیک کنید
# WebSocket باید UART را در Terminal Mode قرار دهد

```

# 📊 تست Terminal Mode - راهنمای کامل

## 🎯 هدف: تست WebSocket Terminal Mode UART

با توجه به کد کامل `protocol_uart.c` که دو حالت **Bootloader** و **Terminal** دارد، حالا می‌خواهیم حالت Terminal را تست کنیم.

---

## 🔧 مراحل تست

### ۱. فلش کردن ESP32

```bash
cd ~/project/programer/all_programer
idf.py -p /dev/ttyUSB0 flash monitor
```

### ۲. اتصال به WiFi ESP32

```
SSID: L-Programmer
Password: 12345678
IP: 192.168.4.1
```

### ۳. باز کردن صفحه Terminal در مرورگر

```
http://192.168.4.1/#/terminal
```

---

## 📋 ساختار صفحه Terminal

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🖥️ ترمینال چندمنظوره                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  📌 دستگاه: ESP32 (ESP32)                              [📡 انتخاب دستگاه] │
├─────────────────────────────────────────────────────────────────────────────┤
│  📡 پروتکل: [UART (TTL/RS232) ▼]                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  🔌 پورت: [UART1 (Target) ▼]  ⚡ Baud: [115200 ▼]                 │   │
│  │  📊 Data Bits: [8 ▼]  ✅ Parity: [None ▼]  🛑 Stop Bits: [1 ▼]   │   │
│  │  🔄 Flow Control: [None ▼]                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│  [🔌 Connect] [🔌 Disconnect]  [🗑️ Clear] [📜 Auto Scroll: ON] [💾 Save] │
│  [🔢 HEX Mode] [⏱️ Timestamps] [📝 Local Echo] [📷 Capture]               │
│  ⚪ Disconnected                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  ⚡ Quick Commands: [AT] [AT+GMR] [AT+CWMODE=1] [AT+CWLAP] [AT+CIPSTART] │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  🖥️ Terminal Ready.                                                │   │
│  │  Protocol: UART | Baud: 115200 | 8N1                              │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │   │
│  │  [اینجا خروجی ترمینال نشان داده می‌شود]                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│  [📤 Send] [HEX Send] [⏎ NL]                                              │
│  TX: 0 bytes | RX: 0 bytes | ⏱️ 00:00:00                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  [📁 Send File] [💾 Receive to File] [📜 Script]                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 تست اتصال WebSocket

### روش ۱: از طریق صفحه Terminal

1. روی دکمه **🔌 Connect** کلیک کنید
2. در کنسول مرورگر (F12) لاگ‌های WebSocket را ببینید

### روش ۲: از طریق کنسول مرورگر

```javascript
// باز کردن کنسول مرورگر (F12) و اجرا:
const ws = new WebSocket('ws://192.168.4.1:8080/terminal');

ws.onopen = () => {
    console.log('✅ WebSocket connected');
    // ارسال تنظیمات
    ws.send(JSON.stringify({
        cmd: "config",
        baud: 115200,
        dataBits: 8,
        parity: "none",
        stopBits: "1",
        protocol: "uart",
        port: "uart1"
    }));
};

ws.onmessage = (event) => {
    console.log('📥', event.data);
};

ws.onclose = () => console.log('🔌 Disconnected');
ws.onerror = (err) => console.log('❌ Error:', err);

// ارسال داده
ws.send('AT\r\n');
```

---

## 📤 ارسال داده

### از طریق صفحه Terminal:
1. در قسمت ورودی تایپ کنید: `AT`
2. دکمه **📤 Send** را بزنید یا Enter بزنید

### از طریق کنسول:
```javascript
ws.send('AT+GMR\r\n');
ws.send('Hello World!\r\n');
```



┌─────────────────────────────────────────────────────────────────────────────┐
│                         جریان کامل داده                                    │
│                                                                             │
│  ┌──────────┐    WebSocket    ┌─────────────────────────────────────────┐  │
│  │ فرانت‌اند │ ◄────────────► │  protocol_websocket.c                  │  │
│  │          │                 │  ┌───────────────────────────────────┐  │  │
│  └──────────┘                 │  │  ws_task() - حلقه اصلی           │  │  │
│                               │  │  while (1) {                     │  │  │
│                               │  │    mg_mgr_poll()                 │  │  │
│                               │  │    protocol_poll_all() ← ✅      │  │  │
│                               │  │  }                              │  │  │
│                               │  └───────────────────────────────────┘  │  │
│                               │         │                              │  │
│                               │         ▼                              │  │
│                               │  ┌───────────────────────────────────┐  │  │
│                               │  │  protocol.c                      │  │  │
│                               │  │  protocol_poll_all() ← ✅ جدید   │  │  │
│                               │  │  فقط پروتکل‌های Mode=TERMINAL   │  │  │
│                               │  └───────────────────────────────────┘  │  │
│                               │         │                              │  │
│                               │         ▼                              │  │
│                               │  ┌───────────────────────────────────┐  │  │
│                               │  │  protocol_uart.c                 │  │  │
│                               │  │  uart_terminal_poll() ← Ring Buf │  │  │
│                               │  │  uart_rx_interrupt() ← وقفه      │  │  │
│                               │  └───────────────────────────────────┘  │  │
│                               └─────────────────────────────────────────┘  │
│                                                                             │
│  📌 main.c: فقط HTTP API + WebSocket شروع                                 │
│  📌 protocol.c: مدیریت حالت و Polling                                     │
│  📌 protocol_uart.c: Ring Buffer + Interrupt                              │
│  📌 protocol_websocket.c: WebSocket Server + Poll                         │
└─────────────────────────────────────────────────────────────────────────────┘

---

## 📥 دریافت داده

داده‌های دریافتی از Target در قسمت ترمینال نمایش داده می‌شود:
- **سبز** = داده ارسالی (TX)
- **سفید** = داده دریافتی (RX)
- **زرد** = پیام‌های سیستم
- **قرمز** = خطاها

---

## 🛠️ تنظیمات مهم

| تنظیم | توضیح |
|-------|-------|
| **پورت** | UART1 = Target (دو طرفه) / UART0 = Debug (فقط خواندنی) |
| **Baud Rate** | سرعت ارتباط (پیش‌فرض 115200) |
| **Data Bits** | 5-8 بیت (پیش‌فرض 8) |
| **Parity** | None/Even/Odd/Mark/Space |
| **Stop Bits** | 1/1.5/2 |
| **Flow Control** | None/RTS-CTS/XON-XOFF/DTR-DSR |
| **Local Echo** | نمایش داده‌های ارسالی در ترمینال |
| **HEX Mode** | نمایش داده‌ها به صورت HEX |
| **Timestamps** | نمایش زمان هر پیام |
| **Auto Scroll** | اسکرول خودکار به انتها |

---

## ⚡ دستورات سریع (Quick Commands)

دکمه‌های زیر به صورت خودکار برای هر پروتکل نمایش داده می‌شوند:

### UART:
- `AT` - تست ارتباط
- `AT+GMR` - اطلاعات دستگاه
- `AT+CWMODE=1` - تنظیم WiFi Mode
- `AT+CWLAP` - اسکن WiFi
- `AT+CIPSTART` - شروع اتصال TCP

---

## 🐛 عیب‌یابی

### ۱. WebSocket وصل نمی‌شود

**بررسی:**
```bash
# از خط فرمان تست کن
curl -v http://192.168.4.1:8080/terminal
```

**پاسخ باید:** `HTTP/1.1 404 Not Found` یا `WebSocket upgrade`

### ۲. لاگ‌های ESP32 را ببینید

```bash
idf.py -p /dev/ttyUSB0 monitor | grep -i "uart\|websocket"
```

**لاگ‌های مورد انتظار:**
```
I (xxxx) UART: 🌐 Terminal WebSocket: ws://192.168.4.1:8080/terminal
I (xxxx) UART: 📡 UART0 (Debug) → WebSocket (فقط خواندنی)
I (xxxx) UART: 📡 UART1 (Target) → WebSocket (دو طرفه)
I (xxxx) UART: 🔌 WebSocket connected - Terminal Mode ACTIVE
I (xxxx) UART: ⚙️ UART Config: {"cmd":"config","baud":115200,...}
I (xxxx) UART: ⚡ UART config: baud=115200, 8N1
```

### ۳. اگر داده‌ای دریافت نمی‌شود

- بررسی کنید که Target (ESP32/STM32) به درستی وصل شده باشد
- بررسی کنید که Target روشن باشد
- بررسی کنید که پین‌های TX/RX درست وصل شده باشند
- بررسی کنید که Baud Rate با Target هماهنگ باشد

---

## 🚀 گام بعدی

پس از تست موفق Terminal Mode، به سراغ **Bootloader Mode** می‌رویم تا قابلیت برنامه‌ریزی از طریق HTTP API را تست کنیم.


# 📊 بله! کد فرانت‌اند درست است ✅

## 🎯 توضیح نام‌گذاری در فرانت‌اند

شما درست متوجه شدید! در کد `terminal.js` این خط را داریم:

```html
<option value="uart1" selected>UART1 (Target)</option>
<option value="uart0">UART0 (Debug)</option>
```

---

## 📋 تطابق نام‌ها

| در فرانت‌اند | در ESP-IDF | روی برد شما | پین‌ها |
|-------------|------------|-------------|--------|
| **`uart1`** | `UART_NUM_1` | **TX2 / RX2** | GPIO17 / GPIO16 |
| **`uart0`** | `UART_NUM_0` | **TX0 / RX0** | GPIO1 / GPIO3 |

---

## ⚠️ نکته مهم درباره نام‌گذاری

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            📌 توجه!                                        │
│                                                                             │
│  در فرانت‌اند ما از نام `uart1` استفاده کرده‌ایم، اما این به معنی         │
│  UART1 در ESP-IDF نیست!                                                    │
│                                                                             │
│  این فقط یک نام نمایشی (Label) است که در dropdown به کاربر نشان داده       │
│  می‌شود. مهم این است که مقدار (value) به درستی به بک‌اند ارسال شود.       │
│                                                                             │
│  در بک‌اند (protocol_uart.c):                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  if (port) {                                                        │   │
│  │      g_config.port = (strcmp(port->valuestring, "uart0") == 0) ?  │   │
│  │                      UART_DEBUG_PORT : UART_TARGET_PORT;           │   │
│  │  }                                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  • اگر `uart0` → از `UART_DEBUG_PORT` (UART_NUM_0) استفاده می‌شود        │
│  • اگر `uart1` → از `UART_TARGET_PORT` (UART_NUM_1) استفاده می‌شود       │
│                                                                             │
│  و `UART_TARGET_PORT` در کد به صورت زیر تعریف شده است:                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  #define UART_TARGET_PORT    UART_NUM_1                            │   │
│  │  #define UART_TARGET_TX      17              // GPIO17 = TX2       │   │
│  │  #define UART_TARGET_RX      16              // GPIO16 = RX2       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 جدول کامل تطابق

| در فرانت‌اند (value) | در فرانت‌اند (نمایش) | در بک‌اند | پین‌های واقعی | روی برد |
|---------------------|---------------------|-----------|--------------|---------|
| `"uart0"` | "UART0 (Debug)" | `UART_DEBUG_PORT` = `UART_NUM_0` | GPIO1 (TX0) / GPIO3 (RX0) | **TX0 / RX0** |
| `"uart1"` | "UART1 (Target)" | `UART_TARGET_PORT` = `UART_NUM_1` | GPIO17 (TX2) / GPIO16 (RX2) | **TX2 / RX2** |

---

## ✅ پس روی برد شما:

```
فرانت‌اند: "uart1" (Target)
    ↓
بک‌اند: UART_TARGET_PORT = UART_NUM_1
    ↓
پین‌ها: GPIO17 (TX) / GPIO16 (RX)
    ↓
روی برد: TX2 / RX2  ← ✅ این همان است!
```

---

## 🧪 برای تست روی برد شما:

1. **پورت** را روی **`UART1 (Target)`** بگذارید
2. این یعنی از **TX2 (GPIO17)** و **RX2 (GPIO16)** استفاده می‌شود
3. اینها همان پین‌هایی هستند که روی برد برچسب **TX2 / RX2** دارند

---

## 📝 خلاصه

| سوال | پاسخ |
|------|------|
| **نام درست روی برد چیست؟** | TX2 / RX2 |
| **در فرانت‌اند چه نامی دارد؟** | `UART1 (Target)` |
| **مقدار آن چیست؟** | `"uart1"` |
| **پین‌های آن کدامند؟** | GPIO17 (TX) / GPIO16 (RX) |
| **آیا این درست است؟** | ✅ بله، کاملاً درست است! |

**پس برای تست از `UART1 (Target)` استفاده کنید که همان TX2/RX2 روی برد شماست!** 🚀


# 📊 **رفع خطاهای UART - توابع پیاده‌سازی نشده**

## ❌ خطاها:
```
undefined reference to `uart_send_raw'
undefined reference to `uart_send_data'
undefined reference to `uart_config_ws'
undefined reference to `uart_read_register'
```

## 🔍 علت:
این توابع در `protocol_websocket.c` صدا زده شده‌اند اما در `protocol_uart.c` پیاده‌سازی نشده‌اند.

---

## 🔧 **راه‌حل ۱: اضافه کردن توابع به `protocol_uart.c`**
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WebSocket Server (Port 8080) - یکپارچه                  │
│                         مدیریت همه پروتکل‌ها                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ws://IP:8080/uart/terminal    → UART Terminal                            │
│  ws://IP:8080/uart/monitor     → UART Monitor                             │
│  ws://IP:8080/gpio/read        → GPIO Read                                │
│  ws://IP:8080/gpio/write       → GPIO Write                               │
│  ws://IP:8080/swd/debug        → SWD Debug                                │
│  ws://IP:8080/openocd          → OpenOCD Bridge                           │
│  ...                                                                        │
│                                                                             │
│  ✅ یک WebSocket Server برای همه پروتکل‌ها                                │
│  ✅ هر پروتکل آدرس اختصاصی دارد                                           │
│  ✅ بدون تداخل و بدون باز/بسته کردن                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```c
// ============================================================
//  ✅ توابع UART برای استفاده در WebSocket
// ============================================================

// ----- ارسال داده خام -----
void uart_send_raw(const char *data, uint32_t len) {
    if (!uart_initialized || g_uart_mode != UART_PROTOCOL_MODE_TERMINAL) {
        ESP_LOGW(TAG, "⚠️ Cannot send raw data - not in terminal mode");
        return;
    }
    uart_write_bytes(UART_TARGET_PORT, data, len);
    ESP_LOGI(TAG, "📤 Raw sent: %.*s", len, data);
}

// ----- ارسال داده متنی -----
void uart_send_data(const char *data) {
    if (!data) return;
    if (!uart_initialized || g_uart_mode != UART_PROTOCOL_MODE_TERMINAL) {
        ESP_LOGW(TAG, "⚠️ Cannot send data - not in terminal mode");
        return;
    }
    uart_write_bytes(UART_TARGET_PORT, data, strlen(data));
    ESP_LOGI(TAG, "📤 Data sent: %s", data);
}

// ----- تنظیمات از WebSocket -----
void uart_config_ws(uint32_t baud, uint8_t data_bits, const char *parity, const char *stop_bits) {
    ESP_LOGI(TAG, "⚙️ WS Config: baud=%lu, data_bits=%d, parity=%s, stop=%s", 
             baud, data_bits, parity, stop_bits);
    
    g_config.baud_rate = baud;
    g_config.data_bits = data_bits;
    g_config.parity = uart_parity_from_string(parity);
    g_config.stop_bits = uart_stop_from_string(stop_bits);
    
    if (uart_initialized) {
        uart_apply_config();
    }
}

// ----- خواندن رجیستر UART -----
uint32_t uart_read_register(uint32_t addr) {
    // برای ESP32، خواندن رجیسترهای UART
    // این یک پیاده‌سازی نمونه است
    ESP_LOGI(TAG, "📖 Read UART register: 0x%08lX", addr);
    
    // اگر آدرس در محدوده UART باشد
    if (addr >= 0x3FF40000 && addr < 0x3FF50000) {
        return *((volatile uint32_t*)addr);
    }
    return 0x00000000;
}
```

---

## 🔧 **راه‌حل ۲: اصلاح `protocol_websocket.c` - حذف توابع UART اضافی**

اگر نمی‌خواهید این توابع را پیاده‌سازی کنید، می‌توانید `uart_ws_handler` را ساده‌تر کنید:

```c
// ----- UART Handler (ساده‌شده) -----
static void uart_ws_handler(struct mg_connection *c, char *data, uint32_t len) {
    ESP_LOGI(TAG, "📥 UART: %.*s", len, data);
    
    cJSON *json = cJSON_Parse(data);
    if (!json) {
        // داده خام - فقط به UART ارسال کن
        extern void uart_send_raw(const char *data, uint32_t len);
        uart_send_raw(data, len);
        return;
    }
    
    cJSON *cmd = cJSON_GetObjectItem(json, "cmd");
    if (!cmd) {
        cJSON_Delete(json);
        return;
    }
    
    if (strcmp(cmd->valuestring, "send") == 0) {
        cJSON *data_obj = cJSON_GetObjectItem(json, "data");
        if (data_obj) {
            extern void uart_send_data(const char *data);
            uart_send_data(data_obj->valuestring);
        }
    }
    else if (strcmp(cmd->valuestring, "config") == 0) {
        cJSON *baud = cJSON_GetObjectItem(json, "baud");
        cJSON *data_bits = cJSON_GetObjectItem(json, "dataBits");
        cJSON *parity = cJSON_GetObjectItem(json, "parity");
        cJSON *stop_bits = cJSON_GetObjectItem(json, "stopBits");
        
        extern void uart_config_ws(uint32_t baud, uint8_t data_bits, const char *parity, const char *stop_bits);
        uart_config_ws(
            baud ? baud->valueint : 115200,
            data_bits ? data_bits->valueint : 8,
            parity ? parity->valuestring : "none",
            stop_bits ? stop_bits->valuestring : "1"
        );
        
        cJSON *resp = cJSON_CreateObject();
        cJSON_AddStringToObject(resp, "status", "configured");
        ws_send_json(c, resp);
    }
    cJSON_Delete(json);
}
```

---

## 📝 **کد کامل توابع اضافه شده به `protocol_uart.c`**

```c
// ============================================================
//  ✅ توابع UART برای استفاده در WebSocket
//  (قبل از تعریف g_uart_protocol اضافه کنید)
// ============================================================

// ----- ارسال داده خام -----
void uart_send_raw(const char *data, uint32_t len) {
    if (!uart_initialized || g_uart_mode != UART_PROTOCOL_MODE_TERMINAL) {
        ESP_LOGW(TAG, "⚠️ Cannot send raw data - not in terminal mode");
        return;
    }
    uart_write_bytes(UART_TARGET_PORT, data, len);
    ESP_LOGI(TAG, "📤 Raw sent: %.*s", len, data);
}

// ----- ارسال داده متنی -----
void uart_send_data(const char *data) {
    if (!data) return;
    if (!uart_initialized || g_uart_mode != UART_PROTOCOL_MODE_TERMINAL) {
        ESP_LOGW(TAG, "⚠️ Cannot send data - not in terminal mode");
        return;
    }
    uart_write_bytes(UART_TARGET_PORT, data, strlen(data));
    ESP_LOGI(TAG, "📤 Data sent: %s", data);
}

// ----- تنظیمات از WebSocket -----
void uart_config_ws(uint32_t baud, uint8_t data_bits, const char *parity, const char *stop_bits) {
    ESP_LOGI(TAG, "⚙️ WS Config: baud=%lu, data_bits=%d, parity=%s, stop=%s", 
             baud, data_bits, parity, stop_bits);
    
    g_config.baud_rate = baud;
    g_config.data_bits = data_bits;
    g_config.parity = uart_parity_from_string(parity);
    g_config.stop_bits = uart_stop_from_string(stop_bits);
    
    if (uart_initialized) {
        uart_apply_config();
    }
}

// ----- خواندن رجیستر UART -----
uint32_t uart_read_register(uint32_t addr) {
    ESP_LOGI(TAG, "📖 Read UART register: 0x%08lX", addr);
    // این یک پیاده‌سازی نمونه است
    return 0x00000000;
}
```

---

## 🚀 **حالا کامپایل کنید:**

```bash
idf.py clean
idf.py build
```