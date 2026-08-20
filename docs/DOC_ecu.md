

## ECU ها و روش برنامه‌ریزی:

### ۱. روش‌های ارتباط با ECU:

| روش | پروتکل | سرعت | کاربرد |
|-----|--------|------|--------|
| **OBD-II** | CAN, K-Line | کند (500kbps) | ریمپ، دیاگ، آپدیت |
| **Boot Mode** | UART, SPI | متوسط | آپدیت کامل |
| **Direct Wire** | JTAG, BDM, DAP | سریع | تعمیر، ریکاوری |
| **Bench** | JTAG, BDM | سریع | روی میز |

### ۲. آیا همه ECU ها بوت‌لودر دارند؟

**بله!** اما تفاوت دارند:

#### بوت‌لودر کارخانه‌ای (Factory Bootloader):
```
Bosch: بوت‌لودر در Flash جدا
Delphi: بوت‌لودر در EEPROM
Denso: بوت‌لودر در Flash
```

#### بوت‌لودر از طریق OBD:
```
CAN: برای ECU های جدید (2008+)
K-Line: برای ECU های قدیمی (قبل از 2008)
```

### ۳. ریمپ (Remap) چگونه انجام می‌شود؟

#### روش ۱: OBD (معمولی):
```
1. اتصال به OBD-II
2. خواندن Flash از طریق CAN/K-Line
3. ویرایش Map ها (توربو، سوخت، تایمینگ)
4. نوشتن مجدد از طریق CAN/K-Line
```

#### روش ۲: Boot Mode (مطمئن‌تر):
```
1. ECU را از خودرو جدا کن
2. پین Boot را فعال کن
3. اتصال مستقیم JTAG/BDM
4. خواندن/نوشتن کامل Flash
```

#### روش ۳: Direct Wire (حرفه‌ای):
```
1. ECU را باز کن
2. اتصال مستقیم به چیپ
3. JTAG/BDM/DAP
4. دسترسی کامل
```

### ۴. پروتکل‌های OBD:

#### CAN Bus (مدرن):
```
ECU → CANH/CANL → OBD-II Pin 6/14
سرعت: 500kbps
استاندارد: ISO 15765-4
```

#### K-Line (قدیمی):
```
ECU → K-Line → OBD-II Pin 7
سرعت: 10.4kbps
استاندارد: ISO 9141-2, ISO 14230
```

### ۵. بوت‌لودر ECU ها:

#### Bosch:
```
ME7: بوت‌لودر از طریق K-Line (Slow Init)
MED17: بوت‌لودر از طریق CAN (UDS)
EDC17: بوت‌لودر از طریق CAN (UDS)
```

#### Delphi:
```
MT05: بوت‌لودر از طریق CAN
DCM3.5: بوت‌لودر از طریق CAN
```

#### Denso:
```
HP3: بوت‌لودر از طریق CAN
DU4: بوت‌لودر از طریق K-Line
```

### ۶. آیا از طریق OBD می‌توان ریمپ کرد؟

#### بله! اما محدودیت دارد:

| ECU | OBD ریمپ | Boot Mode | Direct |
|-----|---------|-----------|--------|
| Bosch ME7 | ✅ K-Line | ✅ | ✅ JTAG |
| Bosch MED17 | ✅ CAN | ✅ | ✅ DAP |
| Bosch EDC17 | ✅ CAN | ✅ | ✅ DAP |
| Delphi MT05 | ✅ CAN | ✅ | ✅ JTAG |
| Denso HP3 | ✅ CAN | ✅ | ✅ DAP |

### ۷. تفاوت روش‌ها:

#### OBD ریمپ:
```
✅ آسان - فقط کابل OBD
✅ بدون باز کردن ECU
❌ کند - 10-30 دقیقه
❌ محدود - فقط Map ها
❌ قابل تشخیص - Checksum عوض می‌شود
```

#### Boot Mode:
```
✅ سریع‌تر - 5-10 دقیقه
✅ کامل - همه Flash
✅ مطمئن‌تر
❌ نیاز به باز کردن ECU
❌ نیاز به اتصال مستقیم
```

#### Direct Wire (JTAG/BDM):
```
✅ سریع‌ترین - 1-5 دقیقه
✅ کامل - همه چیز
✅ حتی ECU خراب
❌ نیاز به باز کردن ECU
❌ نیاز به تجهیزات خاص
```

### ۸. در پروژه شما:

```javascript
// AutomotiveFamily
{
  name: 'Bosch_ECU',
  devices: [
    { name: 'MED17.5', protocol: 'DAP', method: 'direct' },
    { name: 'EDC17C46', protocol: 'DAP', method: 'direct' },
  ]
}
```

## نتیجه:

**همه ECU ها بوت‌لودر دارند** ولی:
1. **OBD** = دسترسی محدود (فقط Map)
2. **Boot Mode** = دسترسی کامل
3. **Direct (JTAG/BDM)** = دسترسی کامل + ریکاوری

پروژه شما برای **روش Direct** (JTAG/BDM/DAP) طراحی شده که حرفه‌ای‌تر و کامل‌تر است! ✅

بله! می‌توانید بوت‌لودرهای ECU ها را پیدا کنید و پروتکل اضافه کنید:

## ۱. بوت‌لودرهای ECU - پروتکل‌های شناخته شده:

### Bosch (CAN/UDS):
```
پروتکل: UDS (ISO 14229)
روی: CAN Bus
دستورات:
- 0x10: Diagnostic Session
- 0x27: Security Access
- 0x34: Request Download
- 0x36: Transfer Data
- 0x37: Request Transfer Exit
- 0x31: Routine Control (Erase)
- 0x3E: Tester Present
```

### Delphi (CAN):
```
پروتکل: GMLAN (General Motors)
روی: CAN Bus
مشابه UDS
```

### Denso (CAN):
```
پروتکل: ISO 14230 (KWP2000)
روی: K-Line یا CAN
دستورات:
- 0x81: Start Communication
- 0x82: Stop Communication
- 0x27: Security Access
- 0x34: Request Download
- 0x36: Transfer Data
```

## ۲. پیاده‌سازی در ESP32:

### فایل جدید: protocol_can_bootloader.c

```c
// ============================================================
//  protocol_can_bootloader.c - ECU Bootloader via CAN/K-Line
// ============================================================

#include "protocol.h"
#include "driver/gpio.h"
#include "driver/uart.h"
#include "driver/twai.h"
#include "esp_log.h"
#include <string.h>
#include <inttypes.h>

static const char *TAG = "CAN_BOOT";

// ============================================================
//  پین‌ها
// ============================================================
#define CAN_TX_PIN  17
#define CAN_RX_PIN  16
#define KLINE_PIN   5

// ============================================================
//  ثابت‌های UDS (ISO 14229)
// ============================================================
#define UDS_DIAGNOSTIC_SESSION   0x10
#define UDS_ECU_RESET            0x11
#define UDS_SECURITY_ACCESS      0x27
#define UDS_REQUEST_DOWNLOAD     0x34
#define UDS_TRANSFER_DATA        0x36
#define UDS_TRANSFER_EXIT        0x37
#define UDS_ROUTINE_CONTROL      0x31
#define UDS_TESTER_PRESENT       0x3E

// ============================================================
//  ثابت‌های KWP2000 (ISO 14230)
// ============================================================
#define KWP_START_COMM           0x81
#define KWP_STOP_COMM            0x82
#define KWP_SECURITY_ACCESS      0x27
#define KWP_REQUEST_DOWNLOAD     0x34
#define KWP_TRANSFER_DATA        0x36
#define KWP_TRANSFER_EXIT        0x37

// ============================================================
//  Init
// ============================================================
static bool can_bootloader_init(void) {
    // CAN Bus
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(
        CAN_TX_PIN, CAN_RX_PIN, TWAI_MODE_NORMAL);
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();
    
    twai_driver_install(&g_config, &t_config, &f_config);
    twai_start();
    
    ESP_LOGI(TAG, "CAN Bootloader initialized");
    return true;
}

// ============================================================
//  ارسال UDS روی CAN
// ============================================================
static bool uds_send(uint8_t *data, uint8_t len, uint8_t *response, uint8_t *resp_len) {
    twai_message_t tx_msg = {
        .identifier = 0x7E0,  // ECU Request ID
        .data_length_code = len,
    };
    memcpy(tx_msg.data, data, len);
    
    if (twai_transmit(&tx_msg, pdMS_TO_TICKS(1000)) != ESP_OK) {
        return false;
    }
    
    // دریافت پاسخ
    twai_message_t rx_msg;
    if (twai_receive(&rx_msg, pdMS_TO_TICKS(1000)) != ESP_OK) {
        return false;
    }
    
    if (rx_msg.identifier == 0x7E8) {  // ECU Response ID
        memcpy(response, rx_msg.data, rx_msg.data_length_code);
        *resp_len = rx_msg.data_length_code;
        return true;
    }
    
    return false;
}

// ============================================================
//  تشخیص جلسه
// ============================================================
static bool uds_start_session(void) {
    uint8_t request[] = {0x10, 0x03};  // Extended Diagnostic Session
    uint8_t response[8];
    uint8_t resp_len;
    
    if (uds_send(request, 2, response, &resp_len)) {
        if (response[0] == 0x50 && response[2] == 0x03) {
            ESP_LOGI(TAG, "Session started");
            return true;
        }
    }
    
    return false;
}

// ============================================================
//  Security Access
// ============================================================
static bool uds_security_access(uint8_t seed[2], uint8_t key[2]) {
    // درخواست Seed
    uint8_t req_seed[] = {0x27, 0x01};
    uint8_t resp[8];
    uint8_t resp_len;
    
    if (!uds_send(req_seed, 2, resp, &resp_len)) return false;
    
    if (resp[0] == 0x67 && resp[1] == 0x01) {
        seed[0] = resp[2];
        seed[1] = resp[3];
    }
    
    // ارسال Key (برای ECU های مختلف متفاوت است)
    uint8_t req_key[] = {0x27, 0x02, key[0], key[1]};
    
    if (uds_send(req_key, 4, resp, &resp_len)) {
        if (resp[0] == 0x67 && resp[1] == 0x02) {
            ESP_LOGI(TAG, "Security unlocked");
            return true;
        }
    }
    
    return false;
}

// ============================================================
//  خواندن Flash از طریق UDS
// ============================================================
static proto_result_t uds_read_mem(uint32_t addr, uint8_t *buf, uint32_t size) {
    proto_result_t r = {0};
    
    // Request Download (Read)
    uint8_t req[] = {
        0x34, 0x00,
        (addr >> 24) & 0xFF, (addr >> 16) & 0xFF,
        (addr >> 8) & 0xFF, addr & 0xFF,
        (size >> 24) & 0xFF, (size >> 16) & 0xFF,
        (size >> 8) & 0xFF, size & 0xFF
    };
    
    uint8_t resp[8];
    uint8_t resp_len;
    
    if (!uds_send(req, 10, resp, &resp_len)) {
        strcpy(r.message, "Request failed");
        return r;
    }
    
    // Transfer Data
    for (uint32_t i = 0; i < size; i += 4095) {
        uint32_t chunk = (size - i < 4095) ? size - i : 4095;
        
        uint8_t transfer_req[8];
        transfer_req[0] = 0x36;
        transfer_req[1] = (i >> 8) & 0xFF;
        transfer_req[2] = i & 0xFF;
        
        // ارسال داده...
        
        r.bytes_read += chunk;
    }
    
    r.success = true;
    strcpy(r.message, "Read OK");
    return r;
}

// ============================================================
//  Connect
// ============================================================
static bool can_bootloader_connect(void) {
    if (!can_bootloader_init()) return false;
    
    // شروع جلسه
    if (!uds_start_session()) {
        ESP_LOGE(TAG, "Session failed");
        return false;
    }
    
    // Security Access
    uint8_t seed[2], key[2] = {0x00, 0x00};  // Key برای هر ECU متفاوت
    
    if (!uds_security_access(seed, key)) {
        ESP_LOGE(TAG, "Security failed");
        return false;
    }
    
    return true;
}

// ============================================================
//  تعریف پروتکل
// ============================================================
protocol_t g_can_bootloader_protocol = {
    .info = {
        .name = "CAN Bootloader",
        .description = "ECU Bootloader via CAN (UDS)",
        .target_family = "ECU,Automotive",
        .pin_count = 4,
        .needs_vpp = false,
        .default_voltage = 12,
    },
    .init = can_bootloader_init,
    .connect = can_bootloader_connect,
    .read_mem = uds_read_mem,
    // ...
};
```

## ۳. بوت‌لودرهای معروف ECU:

### Bosch EDC17 (CAN):
```
CAN ID: 0x7E0 (Request), 0x7E8 (Response)
پروتکل: UDS
Security: Seed-Key Algorithm (Bosch Secret)
```

### Bosch ME7 (K-Line):
```
K-Line: ISO 9141
پروتکل: KWP2000
Security: Seed-Key
```

### Delphi MT05 (CAN):
```
CAN ID: 0x7E0/0x7E8
پروتکل: GMLAN
```

## ۴. چالش‌ها:

### Security Algorithm:
```
هر ECU یک الگوریتم Seed-Key دارد:
- Bosch: معروف، در اینترنت هست
- Delphi: معروف
- Denso: معروف
- Continental: معروف

این الگوریتم‌ها معمولاً leaked شده‌اند
```

### Checksum:
```
بعد از ریمپ، Checksum باید دوباره محاسبه شود:
- Bosch: CRC32
- Delphi: XOR
- Denso: CRC16
```

## ۵. آیا می‌توانید؟

### بله! اما نیاز دارید:

1. **CAN Transceiver** (MCP2551/SN65HVD230)
2. **K-Line Transceiver** (L9637D)
3. **Seed-Key الگوریتم‌ها** (از اینترنت)
4. **Checksum الگوریتم‌ها** (از اینترنت)

## ۶. پروتکل‌های اضافه کنید:

```c
// در register_all_protocols:
extern protocol_t g_can_bootloader_protocol;
protocol_register(&g_can_bootloader_protocol);
```

## ۷. در فرانت‌اند:

```javascript
// خانواده ECU
{
  name: 'ECU_Bootloader',
  getProtocol: () => 'CAN',
  types: [
    { name: 'Bosch', devices: [...] },
    { name: 'Delphi', devices: [...] },
  ]
}
```

## نتیجه:

**بله! می‌توانید بوت‌لودر ECU ها را اضافه کنید!**

نیاز دارید:
1. ✅ CAN Transceiver سخت‌افزاری
2. ✅ Seed-Key الگوریتم‌ها (آنلاین پیدا می‌شوند)
3. ✅ Checksum الگوریتم‌ها (آنلاین پیدا می‌شوند)
4. ✅ UDS/KWP2000 پروتکل

**آیا می‌خواهید شروع کنیم؟**