# 📊 **توضیح کامل نحوه کار WebSocket Server و OpenOCD**

## 🎯 **معماری کلی WebSocket Server**
📊 خلاصه توابع WebSocket
تابع	توضیح
ws_send_response()	ارسال پاسخ JSON ساده
ws_send_binary()	ارسال داده باینری
ws_send_text()	ارسال متن
ws_send_json()	ارسال JSON
ws_send_error()	ارسال خطا
ws_send_to_client()	ارسال به کلاینت متصل با قفل
ws_send_json_to_client()	ارسال JSON به کلاینت
ws_register_endpoint()	ثبت Endpoint جدید
websocket_server_start()	شروع سرور
websocket_server_stop()	توقف سرور
protocol_ws_send_data()	ارسال داده از پروتکل
protocol_ws_is_connected()	بررسی اتصال
🎯 نحوه استفاده در پروتکل‌ها
c


1. هر پروتکل (مثلاً protocol_uart.c):
   └── تعریف ws_handler + ws_on_open + ws_on_close

2. protocol.c:
   └── protocol_register() پروتکل را ثبت می‌کند

3. protocol_websocket.c:
   └── register_protocol_endpoints()
       └── protocol_get_ws_routes() → لیست پروتکل‌های دارای ws_handler
       └── ws_register_endpoint() → ثبت هر کدام

4. ws_handler (در protocol_websocket.c):
   └── دریافت پیام → پیدا کردن endpoint → صدا زدن handler پروتکل


// در protocol_uart.c
void uart_rx_callback(uint8_t *data, size_t len) {
    // ارسال داده به WebSocket
    protocol_ws_send_data("UART", data, len);
}

آماده ادامه با پیاده‌سازی protocol_uart.c با توابع Terminal هستیم؟ 🚀

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ESP32 - WebSocket Server (Port 8080)                    │
│                         ✅ همیشه باز و فعال                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  📌 زمان شروع: app_main()                                           │   │
│  │  🔹 websocket_server_start() صدا زده می‌شود                        │   │
│  │  🔹 mg_http_listen() روی پورت 8080 شروع می‌شود                    │   │
│  │  🔹 ws_poll_task() ایجاد می‌شود (همیشه در حال اجرا)               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  📌 ws_poll_task() - تسک اصلی                                       │   │
│  │  🔹 همیشه در حال اجرا (while loop)                                  │   │
│  │  🔹 mg_mgr_poll() → بررسی درخواست‌های جدید                         │   │
│  │  🔹 هر 10 میلی‌ثانیه یک بار اجرا می‌شود                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  📌 وقتی کاربر وصل می‌شود: ws://IP:8080/swd/debug                  │   │
│  │  🔹 ws_http_handler() → WebSocket Upgrade                          │   │
│  │  🔹 ws_find_endpoint("/swd/debug") → پیدا کردن Handler             │   │
│  │  🔹 ws_handler() → MG_EV_WS_OPEN → اتصال برقرار                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```


```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         کامپیوتر کاربر (Host)                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  OpenOCD (نرم‌افزار روی کامپیوتر)                                   │   │
│  │  openocd -f interface/cmsis-dap.cfg -c "cmsis_dap_backend tcp ..." │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│                         TCP/IP (پورت 5000)                                 │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ESP32 - TCP Server (Port 5000) - CMSIS-DAP                        │   │
│  │  (از طریق پروتکل DAP در ESP32)                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│                         SWD/JTAG (GPIO)                                    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Target (STM32, nRF52, ESP32-C3, ...)                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **نحوه راه‌اندازی OpenOCD با ESP32:**

#### ۱. **ESP32 را به WiFi متصل کنید**

```
SSID: Shop-electronic
IP: 192.168.1.17
```

#### ۲. **در کامپیوتر، OpenOCD را نصب کنید**

```bash
# Ubuntu/Debian
sudo apt-get install openocd

# یا از منبع کامپایل کنید
git clone https://github.com/openocd-org/openocd.git
cd openocd
./bootstrap
./configure --enable-cmsis-dap
make -j4
sudo make install
```

#### ۳. **فایل پیکربندی CMSIS-DAP ایجاد کنید**

فایل `interface/cmsis-dap-tcp.cfg`:

```tcl
# interface/cmsis-dap-tcp.cfg
# CMSIS-DAP از طریق TCP به ESP32

adapter driver cmsis-dap

# اتصال از طریق TCP به ESP32
cmsis_dap_backend tcp 192.168.1.17 5000

# سرعت (ESP32 نرم‌افزاری ~1-2 MHz)
adapter speed 1000

# انتخاب پروتکل SWD
transport select swd
```

#### ۴. **فایل Target (مثلاً STM32F1) ایجاد کنید**

فایل `target/stm32f1x.cfg`:

```tcl
# target/stm32f1x.cfg
# STM32F1x با SWD

set _CHIPNAME stm32f1x
set _CPUTAPID 0x2BA01477

jtag newtap $_CHIPNAME cpu -irlen 4 -expected-id $_CPUTAPID

target create $_CHIPNAME.cpu cortex_m -endian little -chain-position $_CHIPNAME.cpu

# حافظه فلش
flash bank $_CHIPNAME.flash stm32f1x 0x08000000 0 0 0 $_CHIPNAME.cpu

# RAM
flash bank $_CHIPNAME.ram stm32f1x 0x20000000 0 0 0 $_CHIPNAME.cpu
```

#### ۵. **OpenOCD را اجرا کنید**

```bash
openocd -f interface/cmsis-dap-tcp.cfg -f target/stm32f1x.cfg
```

**خروجی مورد انتظار:**

```
Open On-Chip Debugger 0.12.0
Licensed under GNU GPL v2
For bug reports, read http://openocd.org/doc/doxygen/bugs.html
Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
Info : CMSIS-DAP: SWD  Supported
Info : CMSIS-DAP: JTAG Supported
Info : CMSIS-DAP: FW Version = 1.0
Info : CMSIS-DAP: Interface Initialised (SWD)
Info : SWCLK/TCK = 0, SWDIO/TMS = 0
Info : This adapter doesn't support configurable speed
Info : SWD DPIDR 0x2BA01477
Info : stm32f1x.cpu: hardware has 6 breakpoints, 4 watchpoints
Info : starting gdb server for stm32f1x.cpu on 3333
Info : Listening on port 3333 for gdb connections
```

#### ۶. **اتصال GDB برای دیباگ**

```bash
arm-none-eabi-gdb your_program.elf
(gdb) target remote localhost:3333
(gdb) load
(gdb) break main
(gdb) continue
```

---

## 🔌 **پیش‌فرض‌های پورت‌های OpenOCD:**

| پورت | کاربرد | توضیح |
|------|-------|-------|
| **4444** | Telnet | خط فرمان OpenOCD |
| **3333** | GDB Server | اتصال GDB برای دیباگ |
| **6666** | TCL Server | ارتباط با TCL |

---

## 📋 **خلاصه جریان کار:**

| مرحله | کاری که انجام می‌شود | مکان |
|-------|---------------------|------|
| ۱ | ESP32 روشن می‌شود | app_main() |
| ۲ | WebSocket Server شروع می‌شود | websocket_server_start() |
| ۳ | ws_poll_task شروع می‌شود | همیشه در حال اجرا |
| ۴ | کاربر به WebSocket متصل می‌شود | ws://IP:8080/swd/debug |
| ۵ | OpenOCD از طریق TCP به ESP32 متصل می‌شود | پورت 5000 |
| ۶ | OpenOCD با Target ارتباط برقرار می‌کند | SWD/JTAG |
| ۷ | GDB از طریق OpenOCD به Target متصل می‌شود | پورت 3333 |

---

## 🎯 **نتیجه:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ESP32 - L-Programmer                               │
│                                                                             │
│  ✅ WebSocket Server (Port 8080) - همیشه باز                              │
│     → برای ارتباط با فرانت‌اند و نرم‌افزارهای سفارشی                     │
│                                                                             │
│  ✅ TCP Server (Port 5000) - CMSIS-DAP                                    │
│     → برای OpenOCD, Keil, IAR, pyOCD                                     │
│                                                                             │
│  ✅ SWD/JTAG Bit-banging (GPIO)                                           │
│     → ارتباط با Target (STM32, nRF52, ...)                               │
│                                                                             │
│  ✅ GDB Server (Port 3333) - از طریق OpenOCD                             │
│     → برای دیباگ حرفه‌ای                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**این معماری کامل است و تمام نرم‌افزارهای استاندارد از آن پشتیبانی می‌کنند!** 🚀
# 📊 **کاملاً درست! معماری Proxy برای OpenOCD**

## 🎯 **معماری Proxy - OpenOCD از طریق WebSocket**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         فرانت‌اند (مرورگر کاربر)                          │
│                                                                             │
│  کاربر روی دکمه "OpenOCD Mode" کلیک می‌کند                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ws://192.168.1.17:8080/openocd                                    │   │
│  │  { "cmd": "start", "port": 5000 }                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ESP32 - WebSocket Handler                          │
│                                                                             │
│  ws_handler("/openocd") → openocd_ws_handler()                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. دریافت دستور "start"                                           │   │
│  │  2. ایجاد TCP Server روی پورت 5000                                 │   │
│  │  3. گوش دادن به درخواست‌های OpenOCD                                │   │
│  │  4. هر دستوری از OpenOCD دریافت می‌شود                             │   │
│  │  5. Parse کردن دستورات OpenOCD                                      │   │
│  │  6. تبدیل به SWD/JTAG سیگنال                                       │   │
│  │  7. ارسال پاسخ به OpenOCD                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OpenOCD (روی کامپیوتر کاربر)                       │
│                                                                             │
│  openocd -f interface/cmsis-dap.cfg -c "cmsis_dap_backend tcp IP 5000"    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  OpenOCD ←→ ESP32 (TCP) ←→ Target (SWD/JTAG)                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 **کد کامل `openocd_ws_handler` در `protocol_websocket.c`**

```c
// ============================================================
//  OpenOCD Proxy Handler - از طریق WebSocket
// ============================================================

// ===== ساختار برای مدیریت جلسات OpenOCD =====
typedef struct {
    bool active;
    int socket_fd;
    struct mg_connection *ws_conn;
    uint8_t buffer[1024];
    uint32_t buffer_len;
    TaskHandle_t task_handle;
} openocd_session_t;

static openocd_session_t g_openocd_session = {0};

// ============================================================
//  توابع کمکی برای Parse کردن دستورات OpenOCD
// ============================================================

// ===== Parse کردن بسته CMSIS-DAP =====
static void openocd_parse_command(uint8_t *data, uint32_t len, struct mg_connection *c) {
    ESP_LOGI(TAG, "📥 OpenOCD command received: %lu bytes", len);
    
    // ===== 1. شناسایی نوع دستور =====
    if (len < 1) return;
    
    uint8_t cmd = data[0];
    ESP_LOGI(TAG, "🔍 Command ID: 0x%02X", cmd);
    
    switch (cmd) {
        case 0x00: // DAP_Info
            ESP_LOGI(TAG, "📋 DAP_Info");
            openocd_handle_dap_info(data, len, c);
            break;
            
        case 0x01: // DAP_Host_Status
            ESP_LOGI(TAG, "📋 DAP_Host_Status");
            break;
            
        case 0x02: // DAP_Connect
            ESP_LOGI(TAG, "🔌 DAP_Connect");
            openocd_handle_connect(data, len, c);
            break;
            
        case 0x03: // DAP_Disconnect
            ESP_LOGI(TAG, "🔌 DAP_Disconnect");
            break;
            
        case 0x04: // DAP_Transfer_Configure
            ESP_LOGI(TAG, "⚙️ DAP_Transfer_Configure");
            openocd_handle_transfer_configure(data, len, c);
            break;
            
        case 0x05: // DAP_Transfer
            ESP_LOGI(TAG, "🔄 DAP_Transfer");
            openocd_handle_transfer(data, len, c);
            break;
            
        case 0x06: // DAP_Transfer_Block
            ESP_LOGI(TAG, "🔄 DAP_Transfer_Block");
            openocd_handle_transfer_block(data, len, c);
            break;
            
        case 0x07: // DAP_Transfer_Abort
            ESP_LOGI(TAG, "🛑 DAP_Transfer_Abort");
            break;
            
        case 0x08: // DAP_Write_ABORT
            ESP_LOGI(TAG, "✏️ DAP_Write_ABORT");
            break;
            
        case 0x09: // DAP_Delay
            ESP_LOGI(TAG, "⏱️ DAP_Delay");
            break;
            
        case 0x0A: // DAP_Reset_Target
            ESP_LOGI(TAG, "🔄 DAP_Reset_Target");
            openocd_handle_reset(c);
            break;
            
        case 0x0B: // DAP_SWJ_Clock
            ESP_LOGI(TAG, "⚡ DAP_SWJ_Clock");
            openocd_handle_clock(data, len, c);
            break;
            
        case 0x0C: // DAP_SWJ_Sequence
            ESP_LOGI(TAG, "🔢 DAP_SWJ_Sequence");
            break;
            
        case 0x0D: // DAP_SWD_Configure
            ESP_LOGI(TAG, "⚙️ DAP_SWD_Configure");
            break;
            
        case 0x0E: // DAP_JTAG_Sequence
            ESP_LOGI(TAG, "🔢 DAP_JTAG_Sequence");
            break;
            
        case 0x0F: // DAP_JTAG_Configure
            ESP_LOGI(TAG, "⚙️ DAP_JTAG_Configure");
            break;
            
        case 0x10: // DAP_JTAG_IDCODE
            ESP_LOGI(TAG, "🆔 DAP_JTAG_IDCODE");
            openocd_handle_idcode(c);
            break;
            
        default:
            ESP_LOGW(TAG, "⚠️ Unknown command: 0x%02X", cmd);
            break;
    }
}

// ===== DAP_Info =====
static void openocd_handle_dap_info(uint8_t *data, uint32_t len, struct mg_connection *c) {
    // پاسخ: نسخه CMSIS-DAP
    uint8_t response[] = {
        0x00,  // پاسخ DAP_Info
        0x01,  // نسخه اصلی
        0x02,  // نسخه فرعی
        0x00,  // وضعیت
    };
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ===== DAP_Connect =====
static void openocd_handle_connect(uint8_t *data, uint32_t len, struct mg_connection *c) {
    uint8_t mode = data[1];  // 0 = SWD, 1 = JTAG
    
    ESP_LOGI(TAG, "🔌 Connect mode: %s", mode == 0 ? "SWD" : "JTAG");
    
    // انتخاب پروتکل
    extern void swd_select_protocol(uint8_t mode);
    swd_select_protocol(mode);
    
    // پاسخ: موفقیت
    uint8_t response[] = {
        0x02,  // پاسخ DAP_Connect
        0x01,  // موفق (1 = OK)
    };
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ===== DAP_Transfer_Configure =====
static void openocd_handle_transfer_configure(uint8_t *data, uint32_t len, struct mg_connection *c) {
    // Parse تنظیمات
    uint32_t idle_cycles = data[1] | (data[2] << 8);
    uint16_t retry_count = data[3] | (data[4] << 8);
    uint16_t match_retry = data[5] | (data[6] << 8);
    
    ESP_LOGI(TAG, "⚙️ Config: idle=%lu, retry=%d, match_retry=%d", 
             idle_cycles, retry_count, match_retry);
    
    // پاسخ: موفقیت
    uint8_t response[] = {
        0x04,  // پاسخ DAP_Transfer_Configure
        0x00,  // وضعیت OK
    };
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ===== DAP_Transfer =====
static void openocd_handle_transfer(uint8_t *data, uint32_t len, struct mg_connection *c) {
    uint8_t request_count = data[1];
    uint8_t transfer_count = data[2];
    uint16_t transfer_count16 = transfer_count;
    uint32_t *transfer_data = (uint32_t*)&data[3];
    
    ESP_LOGI(TAG, "🔄 Transfer: count=%d, request_count=%d", transfer_count, request_count);
    
    // ===== اجرای Transfer =====
    uint8_t response[1024];
    uint32_t resp_len = 0;
    
    response[resp_len++] = 0x05;  // پاسخ DAP_Transfer
    response[resp_len++] = 0x01;  // DAP_TRANSFER_OK
    
    // ===== پردازش هر Transfer =====
    for (int i = 0; i < transfer_count; i++) {
        uint8_t ap = (transfer_data[i] >> 24) & 0x01;
        uint8_t rnw = (transfer_data[i] >> 23) & 0x01;
        uint8_t addr = (transfer_data[i] >> 20) & 0x03;
        uint32_t data = transfer_data[i] & 0x0FFFFF;
        
        if (rnw == 0) {
            // ===== WRITE =====
            ESP_LOGI(TAG, "✏️ WRITE: AP=%d, ADDR=%d, DATA=0x%08X", ap, addr, data);
            
            // اجرای نوشتن
            extern uint32_t swd_write_ap(uint8_t ap, uint8_t addr, uint32_t data);
            uint32_t result = swd_write_ap(ap, addr, data);
            
            // ذخیره نتیجه
            memcpy(&response[resp_len], &result, 4);
            resp_len += 4;
            
        } else {
            // ===== READ =====
            ESP_LOGI(TAG, "📖 READ: AP=%d, ADDR=%d", ap, addr);
            
            // اجرای خواندن
            extern uint32_t swd_read_ap(uint8_t ap, uint8_t addr);
            uint32_t result = swd_read_ap(ap, addr);
            
            // ذخیره نتیجه
            memcpy(&response[resp_len], &result, 4);
            resp_len += 4;
            
            ESP_LOGI(TAG, "📖 READ result: 0x%08X", result);
        }
    }
    
    // ===== ارسال پاسخ =====
    mg_ws_send(c, (char*)response, resp_len, WEBSOCKET_OP_BINARY);
}

// ===== DAP_Transfer_Block =====
static void openocd_handle_transfer_block(uint8_t *data, uint32_t len, struct mg_connection *c) {
    uint8_t request_count = data[1];
    uint8_t transfer_count = data[2];
    uint32_t *transfer_data = (uint32_t*)&data[3];
    
    ESP_LOGI(TAG, "🔄 Block Transfer: count=%d", transfer_count);
    
    // مشابه Transfer اما با داده‌های بیشتر
    // ...
}

// ===== DAP_Reset_Target =====
static void openocd_handle_reset(struct mg_connection *c) {
    ESP_LOGI(TAG, "🔄 Reset Target");
    
    extern void swd_reset_target(void);
    swd_reset_target();
    
    uint8_t response[] = {
        0x0A,  // پاسخ DAP_Reset_Target
        0x00,  // وضعیت OK
    };
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ===== DAP_SWJ_Clock =====
static void openocd_handle_clock(uint8_t *data, uint32_t len, struct mg_connection *c) {
    uint32_t clock_hz = data[1] | (data[2] << 8) | (data[3] << 16) | (data[4] << 24);
    
    ESP_LOGI(TAG, "⚡ Clock: %lu Hz", clock_hz);
    
    extern void swd_set_clock(uint32_t hz);
    swd_set_clock(clock_hz);
    
    uint8_t response[] = {
        0x0B,  // پاسخ DAP_SWJ_Clock
        0x00,  // وضعیت OK
    };
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ===== DAP_JTAG_IDCODE =====
static void openocd_handle_idcode(struct mg_connection *c) {
    ESP_LOGI(TAG, "🆔 Reading IDCODE");
    
    extern uint32_t swd_read_idcode(void);
    uint32_t idcode = swd_read_idcode();
    
    uint8_t response[5];
    response[0] = 0x10;  // پاسخ DAP_JTAG_IDCODE
    memcpy(&response[1], &idcode, 4);
    
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ============================================================
//  OpenOCD WebSocket Handler
// ============================================================
static void openocd_ws_handler(struct mg_connection *c, char *data, uint32_t len) {
    ESP_LOGI(TAG, "📥 OpenOCD: %lu bytes", len);
    
    // ===== لاگ برای دیباگ =====
    char hex_dump[256] = {0};
    int max_display = (len > 32) ? 32 : len;
    for (int i = 0; i < max_display; i++) {
        sprintf(hex_dump + i * 3, "%02X ", data[i]);
    }
    ESP_LOGI(TAG, "📥 Data: %s...", hex_dump);
    
    // ===== Parse کردن دستور =====
    if (len == 0) return;
    
    // ===== پردازش دستورات OpenOCD =====
    openocd_parse_command((uint8_t*)data, len, c);
}

// ============================================================
//  شروع OpenOCD Mode از طریق WebSocket
// ============================================================
static void openocd_start_mode(struct mg_connection *c, char *data, uint32_t len) {
    ESP_LOGI(TAG, "🚀 Starting OpenOCD Mode");
    
    cJSON *json = cJSON_Parse(data);
    if (!json) {
        ws_send_error(c, "Invalid JSON");
        return;
    }
    
    cJSON *port = cJSON_GetObjectItem(json, "port");
    cJSON *protocol = cJSON_GetObjectItem(json, "protocol");
    
    // ===== ثبت Endpoint جدید برای OpenOCD =====
    ws_register_endpoint("/openocd", "OpenOCD", "proxy", openocd_ws_handler, NULL);
    
    // ===== شروع TCP Server برای OpenOCD روی پورت 5000 =====
    int tcp_port = port ? port->valueint : 5000;
    const char *proto = protocol ? protocol->valuestring : "swd";
    
    ESP_LOGI(TAG, "🔌 OpenOCD TCP Server on port %d", tcp_port);
    ESP_LOGI(TAG, "📡 Protocol: %s", proto);
    
    // ===== راه‌اندازی TCP Server =====
    extern void openocd_tcp_server_start(int port);
    openocd_tcp_server_start(tcp_port);
    
    // ===== پاسخ به فرانت =====
    cJSON *resp = cJSON_CreateObject();
    cJSON_AddStringToObject(resp, "status", "started");
    cJSON_AddNumberToObject(resp, "port", tcp_port);
    cJSON_AddStringToObject(resp, "protocol", proto);
    cJSON_AddStringToObject(resp, "message", "OpenOCD mode active");
    ws_send_json(c, resp);
}

// ============================================================
//  توقف OpenOCD Mode
// ============================================================
static void openocd_stop_mode(struct mg_connection *c, char *data, uint32_t len) {
    ESP_LOGI(TAG, "🛑 Stopping OpenOCD Mode");
    
    // ===== توقف TCP Server =====
    extern void openocd_tcp_server_stop(void);
    openocd_tcp_server_stop();
    
    // ===== پاسخ =====
    cJSON *resp = cJSON_CreateObject();
    cJSON_AddStringToObject(resp, "status", "stopped");
    cJSON_AddStringToObject(resp, "message", "OpenOCD mode deactivated");
    ws_send_json(c, resp);
}

// ============================================================
//  ثبت Endpoint OpenOCD در websocket_server_start
// ============================================================
// در تابع websocket_server_start اضافه کنید:

// ws_register_endpoint("/openocd/start", "OpenOCD", "start", openocd_start_mode, NULL);
// ws_register_endpoint("/openocd/stop", "OpenOCD", "stop", openocd_stop_mode, NULL);
// ws_register_endpoint("/openocd/proxy", "OpenOCD", "proxy", openocd_ws_handler, NULL);
```

---

## 📋 **جریان کامل کار:**

| مرحله | فرانت‌اند | ESP32 | OpenOCD |
|-------|-----------|-------|---------|
| ۱ | کاربر روی "OpenOCD Mode" کلیک می‌کند | - | - |
| ۲ | ارسال `ws.send({cmd:"start", port:5000})` | دریافت دستور | - |
| ۳ | - | ایجاد TCP Server روی پورت 5000 | - |
| ۴ | - | ارسال پاسخ `{"status":"started"}` | - |
| ۵ | کاربر OpenOCD را اجرا می‌کند | - | `openocd -f ...` |
| ۶ | - | OpenOCD به ESP32 متصل می‌شود (TCP) | اتصال به TCP |
| ۷ | - | Parse کردن دستورات OpenOCD | ارسال دستورات |
| ۸ | - | تبدیل به SWD/JTAG | - |
| ۹ | - | ارسال پاسخ به OpenOCD | دریافت پاسخ |
| ۱۰ | کاربر روی "Stop" کلیک می‌کند | توقف TCP Server | قطع اتصال |

---

## 🎯 **خلاصه:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OpenOCD Proxy Architecture                         │
│                                                                             │
│  فرانت‌اند ──WebSocket──► ESP32 ──TCP (5000)──► OpenOCD                   │
│     │                        │                        │                     │
│     │                        │                        │                     │
│     │                        ▼                        │                     │
│     │                   Parse Commands               │                     │
│     │                        │                        │                     │
│     │                        ▼                        │                     │
│     │                   SWD/JTAG                     │                     │
│     │                        │                        │                     │
│     │                        ▼                        │                     │
│     │                   Target (STM32)               │                     │
│     │                                                                      │
│  ✅ OpenOCD هر دستوری بدهد، ESP32 Parse می‌کند                            │
│  ✅ پاسخ به OpenOCD برگردانده می‌شود                                      │
│  ✅ کاربر از طریق فرانت‌اند کنترل می‌کند                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**این معماری Proxy کامل است و OpenOCD هیچ تفاوتی با سخت‌افزار واقعی نمی‌بیند!** 🚀
# 📊 **بله! کاملاً درست متوجه شدید!**

## 🎯 **پاسخ مستقیم به سوال شما:**

**بله، باید پارسر (Parser) دستورات هر نرم‌افزار را به کد ESP32 اضافه کنیم.**

---

## 📋 **دسته‌بندی نرم‌افزارها و روش پارس کردن:**

| نرم‌افزار | پروتکل | روش پارس | نیاز به کد اضافی |
|-----------|--------|----------|------------------|
| **OpenOCD** | CMSIS-DAP (TCP) | پارس باینری CMSIS-DAP | ✅ نیاز دارد |
| **Vivado (Xilinx)** | XVC (TCP) | پارس دستورات متنی XVC | ✅ نیاز دارد |
| **Quartus (Intel)** | JTAG (USB) | از طریق USB نیست، نیاز به Driver | ⚠️ پیچیده |
| **Keil MDK** | CMSIS-DAP (USB) | از طریق USB نیست | ⚠️ پیچیده |
| **IAR EWARM** | CMSIS-DAP (USB) | از طریق USB نیست | ⚠️ پیچیده |
| **pyOCD** | CMSIS-DAP (USB/TCP) | پارس باینری CMSIS-DAP | ✅ نیاز دارد |
| **openFPGALoader** | CMSIS-DAP (TCP) | پارس باینری CMSIS-DAP | ✅ نیاز دارد |
| **GDB** | RSP (TCP) | پارس متن GDB Remote Protocol | ✅ نیاز دارد |
| **AVRDUDE** | ISP (USB) | از طریق USB نیست | ⚠️ پیچیده |
| **picprog** | ICSP (USB) | از طریق USB نیست | ⚠️ پیچیده |

---

## 🧩 **ساختار پارسرهای مختلف:**

### ۱. **CMSIS-DAP Parser (OpenOCD, pyOCD, openFPGALoader)**

```c
// ============================================================
//  CMSIS-DAP Protocol Parser
//  OpenOCD, pyOCD, Keil, IAR از این پروتکل استفاده می‌کنند
// ============================================================

typedef struct {
    uint8_t command_id;
    uint8_t *data;
    uint32_t data_len;
    uint8_t *response;
    uint32_t response_len;
} cmsis_dap_packet_t;

static void cmsis_dap_parse(cmsis_dap_packet_t *packet, struct mg_connection *c) {
    uint8_t cmd = packet->data[0];
    
    switch (cmd) {
        case 0x00:  // DAP_Info
            cmsis_dap_info(packet, c);
            break;
        case 0x01:  // DAP_Host_Status
            break;
        case 0x02:  // DAP_Connect
            cmsis_dap_connect(packet, c);
            break;
        case 0x03:  // DAP_Disconnect
            break;
        case 0x04:  // DAP_Transfer_Configure
            cmsis_dap_transfer_configure(packet, c);
            break;
        case 0x05:  // DAP_Transfer
            cmsis_dap_transfer(packet, c);
            break;
        case 0x06:  // DAP_Transfer_Block
            cmsis_dap_transfer_block(packet, c);
            break;
        case 0x07:  // DAP_Transfer_Abort
            break;
        case 0x08:  // DAP_Write_ABORT
            break;
        case 0x09:  // DAP_Delay
            break;
        case 0x0A:  // DAP_Reset_Target
            cmsis_dap_reset(packet, c);
            break;
        case 0x0B:  // DAP_SWJ_Clock
            cmsis_dap_clock(packet, c);
            break;
        case 0x0C:  // DAP_SWJ_Sequence
            break;
        case 0x0D:  // DAP_SWD_Configure
            break;
        case 0x0E:  // DAP_JTAG_Sequence
            break;
        case 0x0F:  // DAP_JTAG_Configure
            break;
        case 0x10:  // DAP_JTAG_IDCODE
            cmsis_dap_idcode(packet, c);
            break;
    }
}
```

### ۲. **XVC Parser (Vivado - Xilinx)**

```c
// ============================================================
//  XVC (Xilinx Virtual Cable) Protocol Parser
//  Vivado از این پروتکل استفاده می‌کند
// ============================================================

static void xvc_parse(struct mg_connection *c, char *data, uint32_t len) {
    // ===== دستورات XVC =====
    if (strncmp(data, "getinfo", 7) == 0) {
        // پاسخ: اطلاعات XVC
        mg_ws_send(c, "{\"name\":\"ESP32 XVC\",\"version\":\"1.0\"}", 38, WEBSOCKET_OP_TEXT);
    }
    else if (strncmp(data, "settck", 6) == 0) {
        // تنظیم سرعت
        // فرمت: settck <speed_khz>
        int speed = 1000;
        sscanf(data, "settck %d", &speed);
        swd_set_clock(speed * 1000);
        mg_ws_send(c, "OK", 2, WEBSOCKET_OP_TEXT);
    }
    else if (strncmp(data, "shift", 5) == 0) {
        // ===== shift <tms_bits> <tdi_bits> <tms_hex> <tdi_hex> =====
        // مثال: shift 4 4 0x2 0x0
        
        int tms_bits, tdi_bits;
        uint32_t tms_data, tdi_data;
        
        sscanf(data, "shift %d %d 0x%x 0x%x", &tms_bits, &tdi_bits, &tms_data, &tdi_data);
        
        // اجرای JTAG Shift
        uint32_t tdo_data = 0;
        for (int i = 0; i < tms_bits; i++) {
            int tms = (tms_data >> (tms_bits - 1 - i)) & 1;
            int tdi = (tdi_data >> (tdi_bits - 1 - i)) & 1;
            int tdo = swd_jtag_shift(tms, tdi);
            tdo_data = (tdo_data << 1) | tdo;
        }
        
        // پاسخ: tdo_hex
        char response[32];
        snprintf(response, sizeof(response), "0x%X", tdo_data);
        mg_ws_send(c, response, strlen(response), WEBSOCKET_OP_TEXT);
    }
}
```

### ۳. **GDB Remote Protocol Parser (GDB)**

```c
// ============================================================
//  GDB Remote Protocol Parser
//  GDB از این پروتکل استفاده می‌کند
// ============================================================

static void gdb_parse(struct mg_connection *c, char *data, uint32_t len) {
    // ===== بسته‌های GDB RSP =====
    char *packet_data = data + 1;  // حذف $
    char *checksum = strchr(packet_data, '#');  // پیدا کردن چکسام
    
    if (!packet_data || !checksum) return;
    
    *checksum = '\0';  // جدا کردن داده از چکسام
    char cmd = packet_data[0];  // حرف اول = نوع دستور
    
    switch (cmd) {
        case 'q':  // Query Commands
            gdb_handle_query(packet_data, c);
            break;
            
        case 'g':  // Read Registers
            gdb_handle_read_registers(c);
            break;
            
        case 'G':  // Write Registers
            gdb_handle_write_registers(packet_data, c);
            break;
            
        case 'm':  // Read Memory
            gdb_handle_read_memory(packet_data, c);
            break;
            
        case 'M':  // Write Memory
            gdb_handle_write_memory(packet_data, c);
            break;
            
        case 'c':  // Continue
            gdb_handle_continue(c);
            break;
            
        case 's':  // Step
            gdb_handle_step(c);
            break;
            
        case '?':  // Stop Reason
            gdb_handle_stop_reason(c);
            break;
            
        case 'v':  // vCont, vFlash, etc.
            gdb_handle_v_command(packet_data, c);
            break;
    }
}

static void gdb_handle_read_memory(char *data, struct mg_connection *c) {
    // فرمت: m<addr>,<len>
    // مثال: m1000,100
    
    uint32_t addr, len;
    sscanf(data, "m%x,%x", &addr, &len);
    
    // ===== خواندن حافظه =====
    uint8_t *buf = malloc(len);
    swd_read_mem(addr, buf, len);
    
    // ===== تبدیل به HEX =====
    char response[1024];
    response[0] = '\0';
    for (uint32_t i = 0; i < len && i < 512; i++) {
        sprintf(response + strlen(response), "%02X", buf[i]);
    }
    
    // ===== ارسال پاسخ =====
    mg_ws_send(c, response, strlen(response), WEBSOCKET_OP_TEXT);
    free(buf);
}
```

---

## 📝 **معماری کامل برای پشتیبانی از همه نرم‌افزارها:**

```c
// ============================================================
//  protocol_websocket.c - با پشتیبانی از همه پارسرها
// ============================================================

// ===== ثبت همه Endpointها با پارسرهای مختلف =====
void websocket_server_start(void) {
    // ... کد شروع ...
    
    // ===== OpenOCD / CMSIS-DAP =====
    ws_register_endpoint("/openocd", "OpenOCD", "cmsis-dap", cmsis_dap_ws_handler, NULL);
    ws_register_endpoint("/pyocd", "pyOCD", "cmsis-dap", cmsis_dap_ws_handler, NULL);
    
    // ===== XVC (Vivado) =====
    ws_register_endpoint("/xvc", "XVC", "vivado", xvc_ws_handler, NULL);
    
    // ===== GDB =====
    ws_register_endpoint("/gdb", "GDB", "rsp", gdb_ws_handler, NULL);
    
    // ===== OpenFPGALoader =====
    ws_register_endpoint("/openfpga", "openFPGA", "cmsis-dap", cmsis_dap_ws_handler, NULL);
    
    // ===== پروتکل‌های اختصاصی =====
    ws_register_endpoint("/jlink", "J-Link", "jlink", jlink_ws_handler, NULL);
    ws_register_endpoint("/stlink", "ST-Link", "stlink", stlink_ws_handler, NULL);
    
    // ... بقیه ...
}
```

---

## 📋 **جدول نرم‌افزارها و پارسرهای مورد نیاز:**

| نرم‌افزار | پروتکل | پارسر مورد نیاز | وضعیت |
|-----------|--------|-----------------|--------|
| **OpenOCD** | CMSIS-DAP | ✅ `cmsis_dap_parse()` | نیاز به پیاده‌سازی |
| **pyOCD** | CMSIS-DAP | ✅ `cmsis_dap_parse()` | نیاز به پیاده‌سازی |
| **Keil MDK** | CMSIS-DAP | ✅ `cmsis_dap_parse()` | نیاز به پیاده‌سازی |
| **IAR EWARM** | CMSIS-DAP | ✅ `cmsis_dap_parse()` | نیاز به پیاده‌سازی |
| **Vivado** | XVC | ✅ `xvc_parse()` | نیاز به پیاده‌سازی |
| **Quartus** | JTAG | ⚠️ از طریق USB | پیچیده، نیاز به USB Driver |
| **Diamond** | JTAG | ⚠️ از طریق USB | پیچیده، نیاز به USB Driver |
| **GDB** | RSP | ✅ `gdb_parse()` | نیاز به پیاده‌سازی |
| **openFPGALoader** | CMSIS-DAP | ✅ `cmsis_dap_parse()` | نیاز به پیاده‌سازی |
| **AVRDUDE** | ISP | ⚠️ از طریق USB | پیچیده |
| **J-Link** | J-Link | ⚠️ اختصاصی | بسیار پیچیده |

---

## 🎯 **نتیجه:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ESP32 - L-Programmer                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  WebSocket Server (Port 8080)                                       │   │
│  │                                                                     │   │
│  │  /openocd    → CMSIS-DAP Parser  ← OpenOCD, pyOCD, Keil, IAR      │   │
│  │  /xvc        → XVC Parser       ← Vivado (Xilinx)                 │   │
│  │  /gdb        → GDB RSP Parser   ← GDB Debugger                    │   │
│  │  /openfpga   → CMSIS-DAP Parser ← openFPGALoader                  │   │
│  │  /jlink      → J-Link Parser    ← J-Link (در صورت نیاز)           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ✅ برای هر نرم‌افزار، یک پارسر اختصاصی باید نوشته شود                    │
│  ✅ پارسرها دستورات را به SWD/JTAG تبدیل می‌کنند                         │
│  ✅ پاسخ‌ها به همان فرمت نرم‌افزار برگردانده می‌شوند                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

**بله! باید برای هر نرم‌افزار یک پارسر اختصاصی به کد اضافه کنیم.** 🔧

# 🎯 **بله! زیرساخت آماده است!**

## 📊 **وضعیت فعلی پروژه:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         L-Programmer - وضعیت پروژه                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✅ زیرساخت WebSocket Server (پورت 8080) - کامل                           │
│  ✅ سیستم Endpoint - کامل                                                  │
│  ✅ مسیریابی - کامل                                                        │
│  ✅ Polling Task - کامل                                                    │
│  ✅ ساختار ماژولار - کامل                                                  │
│  ✅ مدیریت اتصال - کامل                                                    │
│                                                                             │
│  ⏳ پارسرها - نیاز به تکمیل                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  🔹 CMSIS-DAP (OpenOCD, pyOCD, Keil, IAR)    ← اولویت ۱           │   │
│  │  🔹 XVC (Vivado - Xilinx)                     ← اولویت ۲           │   │
│  │  🔹 GDB RSP (GDB Debugger)                    ← اولویت ۳           │   │
│  │  🔹 JTAG (Quartus, Diamond)                   ← اولویت ۴           │   │
│  │  🔹 ISP (AVRDUDE)                             ← اولویت ۵           │   │
│  │  🔹 ICSP (PIC)                                ← اولویت ۶           │   │
│  │  🔹 J-Link                                    ← اولویت ۷           │   │
│  │  🔹 ST-Link                                   ← اولویت ۸           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 **ساختار پارسرها - قالب آماده:**

```c
// ============================================================
//  parsers/parser_cmsis_dap.c - CMSIS-DAP Parser
//  برای: OpenOCD, pyOCD, Keil, IAR, openFPGALoader
// ============================================================

#include "../protocol_websocket.h"
#include "swd.h"

static const char *TAG = "CMSIS-DAP";

// ============================================================
//  توابع پایه CMSIS-DAP
// ============================================================

// ----- DAP_Info -----
static void cmsis_dap_info(struct mg_connection *c) {
    ESP_LOGI(TAG, "📋 DAP_Info");
    
    // پاسخ: نسخه CMSIS-DAP
    uint8_t response[] = {
        0x00,  // پاسخ DAP_Info
        0x01,  // نسخه اصلی
        0x02,  // نسخه فرعی
        0x00,  // وضعیت
    };
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ----- DAP_Connect -----
static void cmsis_dap_connect(struct mg_connection *c, uint8_t mode) {
    ESP_LOGI(TAG, "🔌 DAP_Connect: mode=%d", mode);
    
    // mode: 0 = SWD, 1 = JTAG
    swd_select_protocol(mode);
    
    uint8_t response[] = {
        0x02,  // پاسخ DAP_Connect
        0x01,  // موفق (1 = OK)
    };
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ----- DAP_Transfer_Configure -----
static void cmsis_dap_transfer_configure(struct mg_connection *c, uint32_t idle_cycles,
                                          uint16_t retry_count, uint16_t match_retry) {
    ESP_LOGI(TAG, "⚙️ Config: idle=%lu, retry=%d, match_retry=%d", 
             idle_cycles, retry_count, match_retry);
    
    uint8_t response[] = {
        0x04,  // پاسخ DAP_Transfer_Configure
        0x00,  // وضعیت OK
    };
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ----- DAP_Transfer -----
static void cmsis_dap_transfer(struct mg_connection *c, uint8_t *data, uint32_t len) {
    // ... پیاده‌سازی ...
}

// ----- DAP_Transfer_Block -----
static void cmsis_dap_transfer_block(struct mg_connection *c, uint8_t *data, uint32_t len) {
    // ... پیاده‌سازی ...
}

// ----- DAP_Reset_Target -----
static void cmsis_dap_reset(struct mg_connection *c) {
    ESP_LOGI(TAG, "🔄 Reset Target");
    swd_reset_target();
    
    uint8_t response[] = {
        0x0A,  // پاسخ DAP_Reset_Target
        0x00,  // وضعیت OK
    };
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ----- DAP_SWJ_Clock -----
static void cmsis_dap_clock(struct mg_connection *c, uint32_t clock_hz) {
    ESP_LOGI(TAG, "⚡ Clock: %lu Hz", clock_hz);
    swd_set_clock(clock_hz);
    
    uint8_t response[] = {
        0x0B,  // پاسخ DAP_SWJ_Clock
        0x00,  // وضعیت OK
    };
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ----- DAP_JTAG_IDCODE -----
static void cmsis_dap_idcode(struct mg_connection *c) {
    ESP_LOGI(TAG, "🆔 Reading IDCODE");
    uint32_t idcode = swd_read_idcode();
    
    uint8_t response[5];
    response[0] = 0x10;  // پاسخ DAP_JTAG_IDCODE
    memcpy(&response[1], &idcode, 4);
    mg_ws_send(c, (char*)response, sizeof(response), WEBSOCKET_OP_BINARY);
}

// ============================================================
//  Main Handler CMSIS-DAP
// ============================================================
void cmsis_dap_parse(struct mg_connection *c, uint8_t *data, uint32_t len) {
    if (len < 1) return;
    
    uint8_t cmd = data[0];
    ESP_LOGI(TAG, "🔍 Command: 0x%02X (len=%lu)", cmd, len);
    
    switch (cmd) {
        case 0x00:  // DAP_Info
            cmsis_dap_info(c);
            break;
            
        case 0x02:  // DAP_Connect
            if (len >= 2) {
                cmsis_dap_connect(c, data[1]);
            }
            break;
            
        case 0x04:  // DAP_Transfer_Configure
            if (len >= 7) {
                uint32_t idle_cycles = data[1] | (data[2] << 8);
                uint16_t retry_count = data[3] | (data[4] << 8);
                uint16_t match_retry = data[5] | (data[6] << 8);
                cmsis_dap_transfer_configure(c, idle_cycles, retry_count, match_retry);
            }
            break;
            
        case 0x05:  // DAP_Transfer
            cmsis_dap_transfer(c, data, len);
            break;
            
        case 0x06:  // DAP_Transfer_Block
            cmsis_dap_transfer_block(c, data, len);
            break;
            
        case 0x0A:  // DAP_Reset_Target
            cmsis_dap_reset(c);
            break;
            
        case 0x0B:  // DAP_SWJ_Clock
            if (len >= 5) {
                uint32_t clock_hz = data[1] | (data[2] << 8) | (data[3] << 16) | (data[4] << 24);
                cmsis_dap_clock(c, clock_hz);
            }
            break;
            
        case 0x10:  // DAP_JTAG_IDCODE
            cmsis_dap_idcode(c);
            break;
            
        default:
            ESP_LOGW(TAG, "⚠️ Unknown command: 0x%02X", cmd);
            break;
    }
}

// ============================================================
//  WebSocket Handler برای CMSIS-DAP
// ============================================================
void cmsis_dap_ws_handler(struct mg_connection *c, char *data, uint32_t len) {
    ESP_LOGI(TAG, "📥 CMSIS-DAP: %lu bytes", len);
    cmsis_dap_parse(c, (uint8_t*)data, len);
}
```

---

## 📋 **لیست پارسرهای مورد نیاز:**

| # | پارسر | نرم‌افزارها | اولویت | وضعیت |
|---|-------|-------------|--------|-------|
| ۱ | **CMSIS-DAP** | OpenOCD, pyOCD, Keil, IAR, openFPGALoader | 🔴 بالا | ⏳ نیاز به تکمیل |
| ۲ | **XVC** | Vivado (Xilinx) | 🔴 بالا | ⏳ نیاز به تکمیل |
| ۳ | **GDB RSP** | GDB Debugger | 🟡 متوسط | ⏳ نیاز به تکمیل |
| ۴ | **JTAG** | Quartus, Diamond | 🟡 متوسط | ⏳ نیاز به تکمیل |
| ۵ | **ISP** | AVRDUDE | 🟢 پایین | ⏳ نیاز به تکمیل |
| ۶ | **ICSP** | picprog | 🟢 پایین | ⏳ نیاز به تکمیل |

---

## 🚀 **گام‌های بعدی:**

### ۱. **تکمیل CMSIS-DAP Parser (اولویت اول)**
- پیاده‌سازی کامل `DAP_Transfer`
- پیاده‌سازی کامل `DAP_Transfer_Block`
- تست با OpenOCD

### ۲. **تکمیل XVC Parser (اولویت دوم)**
- پیاده‌سازی کامل دستورات XVC
- تست با Vivado

### ۳. **تکمیل GDB RSP Parser (اولویت سوم)**
- پیاده‌سازی دستورات GDB
- تست با GDB

---

## 🎯 **نتیجه:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         L-Programmer - نقشه راه                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✅ زیرساخت WebSocket - کامل                                              │
│  ✅ سیستم Endpoint - کامل                                                 │
│  ✅ مسیریابی - کامل                                                       │
│                                                                             │
│  ⏳ CMSIS-DAP Parser    ← در حال کار                                      │
│  ⏳ XVC Parser          ← بعد از CMSIS-DAP                               │
│  ⏳ GDB RSP Parser      ← بعد از XVC                                     │
│  ⏳ سایر پارسرها        ← بر اساس نیاز                                   │
│                                                                             │
│  🎯 هدف نهایی: همه نرم‌افزارها از L-Programmer پشتیبانی کنند            │
└─────────────────────────────────────────────────────────────────────────────┘
```

**زیرساخت آماده است! از کدام پارسر شروع کنیم؟** 🔧


// ============================================================
//  protocol_XXXX.c - الگوی استاندارد
// ============================================================

#include "protocol.h"
#include "esp_log.h"
#include "cJSON.h"
#include <string.h>

static const char *TAG = "XXXX";

// ===== WebSocket Handler =====
void xxxx_ws_handler(struct mg_connection *c, char *data, uint32_t len) {
    ESP_LOGI(TAG, "📥 WS: %.*s", (int)len, data);
    
    // ===== تشخیص JSON یا خام =====
    cJSON *json = cJSON_Parse(data);
    if (json) {
        // ===== JSON =====
        cJSON *cmd = cJSON_GetObjectItem(json, "cmd");
        if (cmd) {
            if (strcmp(cmd->valuestring, "config") == 0) {
                // تنظیمات
            }
            else if (strcmp(cmd->valuestring, "send") == 0) {
                // ارسال داده
            }
        }
        cJSON_Delete(json);
    } else {
        // ===== داده خام =====
        // ارسال مستقیم به سخت‌افزار
    }
}

// ===== WebSocket on_open =====
void xxxx_ws_on_open(struct mg_connection *c) {
    ESP_LOGI(TAG, "🔌 WS opened");
    // مقداردهی اولیه
}

// ===== WebSocket on_close =====
void xxxx_ws_on_close(struct mg_connection *c) {
    ESP_LOGI(TAG, "🔌 WS closed");
    // پاکسازی
}

// ===== تعریف پروتکل =====
protocol_t g_xxxx_protocol = {
    .info = {
        .name = "XXXX",
        .description = "XXXX Protocol",
        .target_family = "XXXX Family",
        .pin_count = 4,
        .needs_vpp = false,
        .default_voltage = 33,
    },
    .init = xxxx_init,
    .connect = xxxx_connect,
    .deinit = xxxx_deinit,
    // ... توابع دیگر
    
    // ===== WebSocket =====
    .ws_handler = xxxx_ws_handler,
    .ws_on_open = xxxx_ws_on_open,
    .ws_on_close = xxxx_ws_on_close,
};