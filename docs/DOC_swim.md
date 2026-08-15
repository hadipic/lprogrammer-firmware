```markdown
# 📚 مستندات کامل پروتکل SWIM (STM8)

## 🎯 معرفی

**SWIM** (Single Wire Interface Module) یک پروتکل ارتباطی تک‌سیم است که برای برنامه‌ریزی و دیباگ میکروکنترلرهای **STM8** استفاده می‌شود. این پروتکل توسط STMicroelectronics توسعه یافته و جایگزین پروتکل قدیمی ICC شده است.

---

## 🔌 اتصال سخت‌افزاری

### پین‌های مورد نیاز

| ESP32 | STM8 | توضیح |
|-------|------|--------|
| GPIO18 | SWIM (PD1) | خط داده (Open-Drain با Pull-up 1kΩ) |
| GPIO5 | NRST | ریست سخت‌افزاری |
| GND | GND | زمین مشترک |
| 3.3V | VDD | تغذیه (اختیاری) |

### مدار Pull-up

```
3.3V ──┬── 1kΩ ──┬── SWIM (GPIO18)
        │         │
        │         └── STM8 SWIM Pin
        │
        └── 100nF ── GND
```

---

## ⚡ مشخصات الکتریکی

| پارامتر | مقدار |
|---------|-------|
| **ولتاژ** | 3.3V یا 5V |
| **سرعت Low-Speed** | 8MHz (125ns/bit) |
| **سرعت High-Speed** | 16MHz (62.5ns/bit) |
| **Pull-up** | 1kΩ به VDD |
| **Open-Drain** | بله |

---

## 🔄 فرمت بیت‌ها (Return-to-Zero)

### Low-Speed Mode (8MHz)

| بیت | LOW (Dominant) | HIGH (Recessive) |
|-----|----------------|------------------|
| **1** | 2 سیکل (250ns) | 20 سیکل (2.5µs) |
| **0** | 20 سیکل (2.5µs) | 2 سیکل (250ns) |

### تصویر زمانی

```
Bit 1:  ┌─┐ ┌───────────────────┐
        │ │ │                   │
        └─┘ └───────────────────┘
        ←250ns→ ←────2.5µs────→

Bit 0:  ┌───────────────────┐ ┌─┐
        │                   │ │ │
        └───────────────────┘ └─┘
        ←────2.5µs────→ ←250ns→
```

---

## 🔄 فرمت فریم (Byte)

هر بایت شامل **۱۰ بیت** است:

```
[Header(1)] [D7] [D6] [D5] [D4] [D3] [D2] [D1] [D0] [Parity(1)]
```

| بخش | تعداد بیت | توضیح |
|-----|-----------|--------|
| **Header** | 1 | 0 = میزبان → دستگاه، 1 = دستگاه → میزبان |
| **Data** | 8 | داده (MSB اول) |
| **Parity** | 1 | XOR همه بیت‌های داده |

### مثال: ارسال بایت 0x01 (Command ROTF)

```
Header=0, D7=0, D6=0, D5=0, D4=0, D3=0, D2=0, D1=0, D0=1, Parity=1
```

---

## 📝 فریم‌های Command (دستورات)

### Command Frame (میزبان → دستگاه)

```
[Header=0] [b0] [b1] [b2] [Parity] [ACK از دستگاه]
  5 بیت ارسال + 1 بیت ACK
```

### Command Frame (دستگاه → میزبان)

```
[Header=1] [b0] [b1] [b2] [Parity] [ACK از میزبان]
```

---

## 🔧 دستورات اصلی SWIM

| دستور | کد | توضیح |
|-------|-----|--------|
| **SRST** | 0x00 | ریست نرم‌افزاری |
| **ROTF** | 0x01 | خواندن حافظه (Read On The Fly) |
| **WOTF** | 0x02 | نوشتن حافظه (Write On The Fly) |

---

## ⚡ توالی فعال‌سازی (Entry Sequence)

برای شروع ارتباط، میزبان باید توالی زیر را روی SWIM ارسال کند:

```
1. LOW به مدت 16µs
2. 4 پالس 500µs (LOW/HIGH)
3. 4 پالس 250µs (LOW/HIGH)
4. رها کردن باس (HIGH)
5. انتظار برای SYNC از دستگاه
```

### کد Entry

```c
// 1. LOW
GPIO.out_w1tc = SWIM_BIT;
delay_us(16);

// 2. 4 پالس 500µs
for (int i = 0; i < 4; i++) {
    GPIO.enable_w1tc = SWIM_BIT;  // HIGH
    delay_us(500);
    GPIO.out_w1tc = SWIM_BIT;     // LOW
    GPIO.enable_w1ts = SWIM_BIT;
    delay_us(500);
}

// 3. 4 پالس 250µs
for (int i = 0; i < 4; i++) {
    GPIO.enable_w1tc = SWIM_BIT;  // HIGH
    delay_us(250);
    GPIO.out_w1tc = SWIM_BIT;     // LOW
    GPIO.enable_w1ts = SWIM_BIT;
    delay_us(250);
}

// 4. رها کردن
GPIO.enable_w1tc = SWIM_BIT;
```

---

## 🔄 SYNC (همگام‌سازی)

بعد از Entry، دستگاه یک پالس SYNC می‌فرستد:

```
SYNC = 128 سیکل SWIM = ~16µs (در 8MHz)
```

### اندازه‌گیری SYNC

```c
uint32_t start = XTHAL_GET_CCOUNT();
while (!((GPIO.in >> SWIM_PIN) & 1)) {
    // منتظر Rising Edge
}
uint32_t sync_duration = XTHAL_GET_CCOUNT() - start;
uint32_t sync_us = sync_duration / 240;  // 240 cycles per µs
```

---

## 📖 خواندن حافظه (ROTF)

### توالی

```
1. ارسال Command ROTF (0x01) + ACK
2. ارسال Len (تعداد بایت‌ها) + ACK
3. ارسال آدرس (3 بایت) + ACK
4. دریافت داده از دستگاه (N بایت)
```

### مثال: خواندن Device ID از 0x4800

```c
swim_send_byte(0x01, 3);  // ROTF
swim_send_byte(0x10, 8);  // Len = 16
swim_send_byte(0x48, 8);  // Addr High
swim_send_byte(0x00, 8);  // Addr Mid
swim_send_byte(0x00, 8);  // Addr Low

for (int i = 0; i < 16; i++) {
    swim_recv_byte(&id_data[i]);
}
```

---

## ✍️ نوشتن حافظه (WOTF)

### توالی

```
1. Unlock Flash/EEPROM
2. Erase Page (در صورت نیاز)
3. ارسال Command WOTF (0x02) + ACK
4. ارسال Len + ACK
5. ارسال آدرس (3 بایت) + ACK
6. ارسال داده (N بایت) + ACK
7. انتظار برای پایان نوشتن
8. Verify
```

### Unlock Flash

```c
swim_wotf(1, 0x5062, &k1);  // 0x56
swim_wotf(1, 0x5062, &k2);  // 0xAE
```

---

## 📊 جدول آدرس‌های مهم STM8

### STM8S003/S103/S903

| آدرس | اندازه | توضیح |
|------|--------|--------|
| `0x4800` | 16 بایت | **Device ID** (فقط خواندنی) |
| `0x4000` | 2KB | **EEPROM** |
| `0x8000` | 8KB | **Flash** |
| `0x505B` | 1 | FLASH_CR2 (کنترل) |
| `0x505C` | 1 | FLASH_NCR2 (مکمل) |
| `0x505F` | 1 | FLASH_IAPSR (وضعیت) |
| `0x5062` | 1 | FLASH_PUKR (Unlock Flash) |
| `0x5064` | 1 | FLASH_DUKR (Unlock EEPROM) |

### FLASH_CR2 (0x505B)

| بیت | نام | توضیح |
|-----|-----|--------|
| 0 | **PRG** | 1 = Program، 0 = Read |
| 1 | **ERASE** | 1 = Erase Mode |
| 2-7 | Reserved | - |

### FLASH_IAPSR (0x505F)

| بیت | نام | توضیح |
|-----|-----|--------|
| 0 | **EOP** | End Of Programming |
| 1 | **PUL** | Flash Unlocked |
| 2 | **DUL** | EEPROM Unlocked |

---

## 🗂️ ساختار فایل protocol_swim.c

```
protocol_swim.c
│
├── بخش ۱: هدرها و تعاریف
│   ├── #include ها
│   ├── SWIM_PIN, SWIM_BIT
│   └── SHORT_CYCLES, LONG_CYCLES
│
├── بخش ۲: پین‌ها و تایمینگ‌ها
│   ├── swim_ccount()
│   └── swim_delay_cycles()
│
├── بخش ۳: رجیسترهای SWIM
│   ├── swim_regs_t (ساختار)
│   ├── g_swim_regs[] (دیتابیس)
│   ├── swim_detect_family()
│   ├── swim_get_regs()
│   └── swim_get_page_size()
│
├── بخش ۴: توابع پایه GPIO
│   ├── swim_drive_low()
│   ├── swim_release()
│   ├── swim_sample()
│   └── swim_entry_gpio()
│
├── بخش ۵: Entry + SYNC
│   └── swim_entry_and_sync()
│
├── بخش ۶: ارسال/دریافت بیت
│   ├── swim_send_bit()
│   ├── swim_recv_bit()
│   ├── swim_send_byte()
│   └── swim_recv_byte()
│
├── بخش ۷: دستورات SWIM
│   ├── swim_srst()
│   ├── swim_rotf()
│   └── swim_wotf()
│
├── بخش ۸: Unlock و Write
│   ├── swim_flash_unlock()
│   ├── swim_eeprom_unlock()
│   └── swim_flash_write()
│
├── بخش ۹: توابع سطح بالا (API)
│   ├── swim_init()
│   ├── swim_connect()
│   ├── swim_deinit()
│   ├── swim_detect()
│   ├── swim_read_mem()
│   ├── swim_write_mem()
│   └── swim_erase()
│
└── بخش ۱۰: تعریف پروتکل
    └── g_swim_protocol
```

---

## 📊 دیتابیس رجیسترهای SWIM

### ساختار

```c
typedef struct {
    uint16_t device_id_addr;   // آدرس Device ID
    uint16_t flash_start;      // شروع Flash
    uint16_t flash_size;       // اندازه Flash
    uint16_t eeprom_start;     // شروع EEPROM
    uint16_t eeprom_size;      // اندازه EEPROM
    uint16_t flash_pukr;       // FLASH_PUKR
    uint16_t flash_dukr;       // FLASH_DUKR
    uint16_t flash_cr2;        // FLASH_CR2
    uint16_t flash_iapsr;      // FLASH_IAPSR
    uint16_t option_bytes;     // Option Bytes
} swim_regs_t;
```

### خانواده‌های STM8

| خانواده | Flash | EEPROM | Device ID |
|---------|-------|--------|-----------|
| STM8S003 | 8KB | 128B | 0x4800 |
| STM8S103 | 8KB | 640B | 0x4800 |
| STM8S105 | 32KB | 1KB | 0x4800 |
| STM8S207 | 128KB | 2KB | 0x4800 |
| STM8L051 | 8KB | 256B | 0x4926 |
| STM8L101 | 8KB | 2KB | 0x4928 |

---

## 🔧 Unlock Sequence

### Flash Unlock

```c
// 1. ارسال 0x56 به FLASH_PUKR
swim_wotf(1, regs->flash_pukr, 0x56);

// 2. ارسال 0xAE به FLASH_PUKR
swim_wotf(1, regs->flash_pukr, 0xAE);

// 3. بررسی PUL (بیت 1 از FLASH_IAPSR)
if (regs->flash_iapsr & 0x02) {
    // Unlock موفق
}
```

### EEPROM Unlock

```c
// 1. ارسال 0xAE به FLASH_DUKR
swim_wotf(1, regs->flash_dukr, 0xAE);

// 2. ارسال 0x56 به FLASH_DUKR
swim_wotf(1, regs->flash_dukr, 0x56);

// 3. بررسی DUL (بیت 2 از FLASH_IAPSR)
if (regs->flash_iapsr & 0x04) {
    // Unlock موفق
}
```

---

## ✍️ نوشتن Flash

### توالی کامل

```c
bool swim_flash_write(uint16_t addr, const uint8_t *data, uint16_t len) {
    // 1. Unlock Flash
    swim_flash_unlock();
    
    // 2. Unlock EEPROM (اگر نیاز)
    swim_eeprom_unlock();
    
    // 3. فعال کردن Program Mode
    swim_wotf(1, regs->flash_cr2, 0x01);  // PRG=1
    
    // 4. نوشتن داده
    for (int i = 0; i < len; i++) {
        swim_wotf(1, addr + i, data[i]);
    }
    
    // 5. انتظار برای EOP
    while (!(regs->flash_iapsr & 0x01)) {
        // منتظر
    }
    
    // 6. غیرفعال کردن Program Mode
    swim_wotf(1, regs->flash_cr2, 0x00);
    
    // 7. Verify
    for (int i = 0; i < len; i++) {
        uint8_t read_byte;
        swim_rotf(1, addr + i, &read_byte);
        if (read_byte != data[i]) {
            return false;  // Verify failed
        }
    }
    
    return true;
}
```

---

## 🧹 Erase

### Erase Flash Page

```c
bool swim_erase_page(uint16_t page_addr) {
    // 1. Unlock Flash
    swim_flash_unlock();
    
    // 2. فعال کردن Erase Mode
    swim_wotf(1, regs->flash_cr2, 0x02);  // ERASE=1
    
    // 3. نوشتن به آدرس صفحه
    swim_wotf(1, page_addr, 0x00);
    
    // 4. انتظار برای EOP
    while (!(regs->flash_iapsr & 0x01)) {
        // منتظر
    }
    
    // 5. غیرفعال کردن Erase Mode
    swim_wotf(1, regs->flash_cr2, 0x00);
    
    return true;
}
```

---

## 📡 WebSocket Integration

### Endpoint

```
ws://IP:8080/swim/debug     → دیباگ SWIM
ws://IP:8080/swim/register  → خواندن/نوشتن رجیستر
```

### پیام‌ها

```json
// Config
{"cmd": "config", "baud": 8000000}

// Read
{"cmd": "read", "address": 0x4800, "size": 16}

// Write
{"cmd": "write", "address": 0x8000, "data": [0x01, 0x02, 0x03]}
```

---

## 🐛 عیب‌یابی

| مشکل | علت | راه‌حل |
|------|------|--------|
| **بدون SYNC** | سیم‌کشی اشتباه | چک پین GPIO18 و Pull-up |
| **NACK در ROTF** | تایمینگ اشتباه | کالیبره کردن با SYNC |
| **نوشتن ناموفق** | Unlock نشده | ارسال 0x56 و 0xAE |
| **Verify خطا** | Page Write نشده | Erase قبل از نوشتن |
| **Timeout** | فرکانس CPU | بررسی SHORT_CYCLES |

---

## 📚 منابع

- **AN2658** - SWIM Protocol Specification
- **STM8S Reference Manual (RM0016)**
- **STM8 SWIM Protocol** - STMicroelectronics

---

**پایان مستندات SWIM** ✅
```
