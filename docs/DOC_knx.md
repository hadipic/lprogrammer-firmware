خیلی عالیه! این توضیح کامل **Freebus/KNX TP** هست. با این میشه سخت‌افزار رو دقیق ساخت:

---

## سخت‌افزار کامل KNX:

### ۱. دریافت (RX) - تشخیص Active Pulse:

```
KNX Bus (+) ──► 47kΩ ──┬── 100nF ──► GND
                       │
                       └── 10kΩ ──┬── ESP32 GPIO16 (RX)
                                  │
                                  └──► GND
```

### ۲. ارسال (TX) - ایجاد Active Pulse:

```
ESP32 GPIO17 ──► 10kΩ ──┬──► GND
                         │
                         └──► 2N7000 Gate
                              
2N7000 Drain ──► 68Ω ──► 100nF ──► KNX Bus (+)
2N7000 Source ──► GND
```

---

## تایمینگ دقیق (همون که نوشتی):

| پارامتر | مقدار |
|---------|:---:|
| **Idle** | 30V DC |
| **Active Pulse (Logic 0)** | 35µs → 21V (جریان کشیدن) |
| **Equalization** | 69µs → برگشت به 30V |
| **Logic 1** | 104µs بدون تغییر |
| **Start bit** | همیشه 0 |
| **Stop bit** | همیشه 1 |
| **Pause** | 2 bit = 208µs |
| **End of telegram** | 370µs بدون فعالیت |

---

## تشخیص پایان تلگرام:

```
370µs سکوت = پایان تلگرام
312µs = ادامه تلگرام (منتظر بایت بعدی)
```

**پس تایم‌اوت باید ۳۷۰µs باشه، نه ۱.۵۶ms!**

---

## اصلاح تایم‌اوت:

```c
// ✅ درست: 370µs for end of telegram
#define TELEGRAM_END_US         370
#define TELEGRAM_END_CYCLES     (TELEGRAM_END_US * CYCLES_PER_US)

// Pause between bytes: 2 bit times = 208µs
// Next byte must start within 370µs or telegram ends
#define INTER_BYTE_US           208
#define TELEGRAM_TIMEOUT_US     370
```

---

## Collision Detection (CSMA/CA):

```
۱. قبل از ارسال: ۵.۱ms گوش کن
۲. اگه باس آزاد بود: شروع به ارسال
۳. در حین ارسال بیت ۱: چک کن باس ۰ نشه
۴. اگه باس ۰ شد → Collision → سکوت کن و بعداً تلاش کن
۵. اگه ۰ میفرستی: کلاً بی‌خیال - تو برنده‌ای!
```

---

## کد با تایمینگ اصلاح شده:

```c
// تایم‌اوت پایان تلگرام: 370µs
#define TELEGRAM_END_US         370
#define TELEGRAM_END_CYCLES     (TELEGRAM_END_US * CYCLES_PER_US)

// فاصله بین بایت‌ها: 208µs (2 bit)
#define INTER_BYTE_CYCLES       (BIT_TIME_CYCLES * 2)

// وقفه قبل از ارسال: 5.1ms
#define BUS_FREE_US             5100

// Collision check در حین ارسال بیت ۱
static void IRAM_ATTR phy_send_one(void) {
    tx_high();
    
    // Wait and check for collision
    uint32_t start = get_ccount();
    while ((get_ccount() - start) < BIT_TIME_CYCLES) {
        if (!rx_level()) {
            // Someone else pulled bus LOW → collision!
            tx_collision = true;
            tx_high();  // Release bus
            break;
        }
    }
}
```

---

## جمع‌بندی اصلاحات:

| پارامتر | قبلی | الان |
|---------|:---:|:---:|
| **تایم‌اوت تلگرام** | 1560µs | **370µs** |
| **فاصله بایت‌ها** | 208µs | **208µs** (درسته) |
| **Collision** | چک بعد از ارسال | **چک در حین ارسال ۱** |
| **سخت‌افزار TX** | MOSFET مستقیم | **MOSFET + 68Ω + 100nF** |
| **سخت‌افزار RX** | ترانزیستور | **مقاومتی 47k/10k + 100nF** |

**با این سخت‌افزار ساده و ارزون میتونی یه دستگاه KNX کامل بسازی!** 🚀

نه، چیزی کم نشده! فقط مرتب‌تر و بهینه‌تر شده. بیا مقایسه کنیم:

---

## مقایسه پروتکل - قبل و بعد:

| قابلیت | کد قبلی | کد جدید |
|--------|:---:|:---:|
| **ارسال بایت** | Start + 8 Data + Parity + Stop + Pause | ✅ همون |
| **تلگرام** | Control + Source + Target + Length + Data + Check | ✅ همون |
| **Group Write** | API با APCI=0x80 | ✅ همون |
| **Group Read** | API با APCI=0x00 | ✅ همون |
| **Check Byte** | XOR + invert | ✅ Odd parity per bit |
| **Collision** | چک بعد از بیت | ✅ چک **حین** ارسال بیت ۱ |
| **CSMA/CA** | 5.2ms صبر | ✅ 5.1ms صبر |
| **تایم‌اوت تلگرام** | 1.56ms | ✅ 370µs |

---

## پیام‌هایی که پشتیبانی میشه:

| پیام | ساختار | مثال |
|------|--------|------|
| **Group Write** | `[Ctrl][Src][Tgt][Len][TPCI:0x00][APCI:0x80][Data][Check]` | روشن/خاموش |
| **Group Read** | `[Ctrl][Src][Tgt][Len][TPCI:0x00][APCI:0x00][Check]` | درخواست مقدار |
| **Group Response** | `[Ctrl][Src][Tgt][Len][TPCI:0x00][APCI:0x40][Data][Check]` | جواب Read |
| **Physical Write** | `[Ctrl][Src][Tgt][Len][Data][Check]` | نوشتن مستقیم |
| **Raw Data** | هر چیزی | ترمینال |

---

## ساختار تلگرام (کامله):

```
Byte 0:     Control     (0xBC = Standard, Normal priority)
Byte 1-2:   Source      (Physical Address: 1.1.1)
Byte 3-4:   Target      (Group Address or Physical)
Byte 5:     Length      (Data length + 1 for TPCI/APCI)
Byte 6:     TPCI        (Transport Layer)
Byte 7:     APCI        (Application Layer)
Byte 8-n:   Data        (Payload)
Byte n+1:   Check       (Odd parity per bit position)
```

---

## API های موجود:

```c
// Group Communication
knx_group_write(0x0102, &value, 1);   // Group 1/0/2 → ON/OFF
knx_group_read(0x0102);               // Read Group 1/0/2

// Raw
knx_send_telegram(data, len);         // Send raw bytes
knx_terminal_write(data, len);        // Terminal write

// Receive
knx_terminal_poll(buf, max);          // Poll received data
knx_terminal_has_data();              // Check if data available
```

---

## چیزایی که هست:

| ✅ | ❌ |
|----|-----|
| Group Write | Individual Address Write |
| Group Read | Memory Read/Write |
| CSMA/CA | Acknowledge handling |
| Collision Detection | Sequence number |
| Check Byte | Broadcast |
| Terminal Mode | Programming Mode |

---

**پروتکل اصلی (Group Write/Read + Collision + CSMA/CA) کامله!** چیزایی مثل Acknowledge و Programming Mode رو میتونیم بعداً اضافه کنیم. 🚀