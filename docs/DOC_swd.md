# پروتکل SWD (Serial Wire Debug) - توضیح کامل با کد

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [سیگنال‌های الکتریکی](#سیگنال‌های-الکتریکی)
3. [ساختار پروتکل](#ساختار-پروتکل)
4. [فازهای تراکنش](#فازهای-تراکنش)
5. [رجیسترها](#رجیسترها)
6. [پیاده‌سازی کامل](#پیاده‌سازی-کامل)
7. [نکات عملی](#نکات-عملی)

---

## مقدمه

SWD یک پروتکل دو سیمه برای دیباگ و برنامه‌ریزی میکروکنترلرهای ARM Cortex-M است. این پروتکل جایگزین JTAG شده و فقط از ۲ پین استفاده می‌کند:

```
SWDIO (Data)  →  داده دوطرفه
SWCLK (Clock) →  کلاک یک‌طرفه از Host به Target
```

---

## سیگنال‌های الکتریکی

### مشخصات SWDIO:
```c
// Open-Drain با Pull-up خارجی (10kΩ)
gpio_config_t swdio_conf = {
    .pin_bit_mask = SWDIO_BIT,
    .mode = GPIO_MODE_INPUT_OUTPUT_OD,  // Open-Drain
    .pull_up_en = GPIO_PULLUP_ENABLE,    // Pull-up داخلی
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type = GPIO_INTR_DISABLE,
};
```

### مشخصات SWCLK:
```c
// Push-Pull خروجی معمولی
gpio_config_t swclk_conf = {
    .pin_bit_mask = SWCLK_BIT,
    .mode = GPIO_MODE_OUTPUT,           // Push-Pull
    .pull_up_en = GPIO_PULLUP_ENABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type = GPIO_INTR_DISABLE,
};
```

---

## ساختار پروتکل

### دیاگرام کلی تراکنش:
```
[Request 8 bits] → [Turnaround 1 bit] → [ACK 3 bits] → [Data 32 bits + Parity]
```

### Request Phase (8 بیت):

```c
// ساخت Request Byte
uint8_t request = 0;
request |= (1 << 0);                    // Bit 0: Start (همیشه 1)
request |= (APnDP << 1);                // Bit 1: APnDP (0=DP, 1=AP)
request |= (RnW << 2);                  // Bit 2: RnW (0=Write, 1=Read)
request |= ((addr >> 2) & 1) << 3;      // Bit 3: A[2]
request |= ((addr >> 3) & 1) << 4;      // Bit 4: A[3]
request |= (parity << 5);               // Bit 5: Parity
request |= (0 << 6);                    // Bit 6: Stop (همیشه 0)
request |= (1 << 7);                    // Bit 7: Park (همیشه 1)
```

### جدول Request:
| Bit | نام | توضیح |
|-----|-----|-------|
| 0 | Start | همیشه 1 |
| 1 | APnDP | 0=DP, 1=AP |
| 2 | RnW | 0=Write, 1=Read |
| 3 | A[2] | Address bit 2 |
| 4 | A[3] | Address bit 3 |
| 5 | Parity | XOR بیت‌های 0-4 |
| 6 | Stop | همیشه 0 |
| 7 | Park | همیشه 1 |

---

## فازهای تراکنش

### ۱. Request Phase (8 بیت)

```c
// ارسال Request با LSB first
for (i = 0; i < 8; i++) {
    // تنظیم داده در لبه پایین‌رونده
    if (request & (1 << i)) {
        GPIO.enable_w1tc = SWDIO_BIT;  // HIGH
    } else {
        GPIO.out_w1tc = SWDIO_BIT;     // LOW
        GPIO.enable_w1ts = SWDIO_BIT;
    }
    
    // پالس کلاک
    GPIO.out_w1tc = SWCLK_BIT;  // Clock LOW
    swd_delay(SWD_CLOCK_CYCLES);
    GPIO.out_w1ts = SWCLK_BIT;  // Clock HIGH
    swd_delay(SWD_CLOCK_CYCLES);
}
```

### ۲. Turnaround Phase (1 بیت)

```c
// تغییر SWDIO به ورودی
GPIO.enable_w1tc = SWDIO_BIT;

// یک پالس کلاک
GPIO.out_w1tc = SWCLK_BIT;
swd_delay(SWD_CLOCK_CYCLES);
GPIO.out_w1ts = SWCLK_BIT;
swd_delay(SWD_CLOCK_CYCLES);
```

### ۳. ACK Phase (3 بیت)

```c
// خواندن ACK (3 بیت)
ack = 0;
for (i = 0; i < 3; i++) {
    GPIO.out_w1tc = SWCLK_BIT;  // Clock LOW
    swd_delay(SWD_HALF_CYCLES);
    
    if (GPIO.in & SWDIO_BIT) {
        ack |= (1 << i);
    }
    
    swd_delay(SWD_HALF_CYCLES);
    GPIO.out_w1ts = SWCLK_BIT;  // Clock HIGH
    swd_delay(SWD_CLOCK_CYCLES);
}
```

### مقادیر ACK:
| مقدار | معنی |
|-------|------|
| 001 (1) | OK |
| 010 (2) | WAIT |
| 100 (4) | FAULT |

### ۴. Data Phase (32 بیت + Parity)

#### Read Operation:
```c
// خواندن 32 بیت داده
value = 0;
for (i = 0; i < 32; i++) {
    GPIO.out_w1tc = SWCLK_BIT;  // Clock LOW
    swd_delay(SWD_HALF_CYCLES);
    
    if (GPIO.in & SWDIO_BIT) {
        value |= (1UL << i);  // LSB first
    }
    
    swd_delay(SWD_HALF_CYCLES);
    GPIO.out_w1ts = SWCLK_BIT;  // Clock HIGH
    swd_delay(SWD_CLOCK_CYCLES);
}
```

#### Write Operation:
```c
// نوشتن 32 بیت داده
value = (data) ? *data : 0;
for (i = 0; i < 32; i++) {
    if (value & (1UL << i)) {
        GPIO.enable_w1tc = SWDIO_BIT;  // HIGH
    } else {
        GPIO.out_w1tc = SWDIO_BIT;     // LOW
        GPIO.enable_w1ts = SWDIO_BIT;
    }
    
    GPIO.out_w1tc = SWCLK_BIT;
    swd_delay(SWD_CLOCK_CYCLES);
    GPIO.out_w1ts = SWCLK_BIT;
    swd_delay(SWD_CLOCK_CYCLES);
}
```

---

## رجیسترها

### Debug Port (DP) Registers:
```c
#define DP_IDCODE     0x00  // شناسایی Target
#define DP_ABORT      0x00  // لغو عملیات
#define DP_CTRL_STAT  0x04  // کنترل و وضعیت
#define DP_SELECT     0x08  // انتخاب AP
#define DP_RDBUFF     0x0C  // بافر خواندن
```

### Access Port (AP) Registers:
```c
#define AP_CSW        0x00  // Control/Status Word
#define AP_TAR        0x04  // Target Address Register
#define AP_DRW        0x0C  // Data Read/Write
#define AP_IDR        0xFC  // Identification Register
```

---

## پیاده‌سازی کامل

### تابع اصلی Transfer:

```c
static uint8_t IRAM_ATTR swd_transfer(uint8_t APnDP, uint8_t RnW, uint8_t addr, uint32_t *data) {
    uint8_t ack = 0;
    uint32_t value = 0;
    uint8_t request, parity;
    int i;
    
    // Critical Section - جلوگیری از وقفه
    taskENTER_CRITICAL(&swd_spinlock);
    
    // ساخت Request
    request = 0;
    request |= (1 << 0);                    // Start
    request |= (APnDP << 1);                // APnDP
    request |= (RnW << 2);                  // RnW
    request |= ((addr >> 2) & 1) << 3;      // A[2]
    request |= ((addr >> 3) & 1) << 4;      // A[3]
    parity = __builtin_parity(request & 0x1F);
    request |= (parity << 5);               // Parity
    request |= (0 << 6);                    // Stop
    request |= (1 << 7);                    // Park
    
    // ارسال Request
    for (i = 0; i < 8; i++) {
        if (request & (1 << i)) {
            GPIO.enable_w1tc = SWDIO_BIT;
        } else {
            GPIO.out_w1tc = SWDIO_BIT;
            GPIO.enable_w1ts = SWDIO_BIT;
        }
        GPIO.out_w1tc = SWCLK_BIT;
        swd_delay(SWD_CLOCK_CYCLES);
        GPIO.out_w1ts = SWCLK_BIT;
        swd_delay(SWD_CLOCK_CYCLES);
    }
    
    // Turnaround
    GPIO.enable_w1tc = SWDIO_BIT;
    GPIO.out_w1tc = SWCLK_BIT;
    swd_delay(SWD_CLOCK_CYCLES);
    GPIO.out_w1ts = SWCLK_BIT;
    swd_delay(SWD_CLOCK_CYCLES);
    
    // خواندن ACK
    for (i = 0; i < 3; i++) {
        GPIO.out_w1tc = SWCLK_BIT;
        swd_delay(SWD_HALF_CYCLES);
        if (GPIO.in & SWDIO_BIT) ack |= (1 << i);
        swd_delay(SWD_HALF_CYCLES);
        GPIO.out_w1ts = SWCLK_BIT;
        swd_delay(SWD_CLOCK_CYCLES);
    }
    
    // Data Phase
    if (ack == SWD_ACK_OK) {
        if (RnW) {  // Read
            value = 0;
            for (i = 0; i < 32; i++) {
                GPIO.out_w1tc = SWCLK_BIT;
                swd_delay(SWD_HALF_CYCLES);
                if (GPIO.in & SWDIO_BIT) value |= (1UL << i);
                swd_delay(SWD_HALF_CYCLES);
                GPIO.out_w1ts = SWCLK_BIT;
                swd_delay(SWD_CLOCK_CYCLES);
            }
            // خواندن Parity
            GPIO.out_w1tc = SWCLK_BIT;
            swd_delay(SWD_HALF_CYCLES);
            swd_delay(SWD_HALF_CYCLES);
            GPIO.out_w1ts = SWCLK_BIT;
            swd_delay(SWD_CLOCK_CYCLES);
            
            if (data) *data = value;
            
        } else {  // Write
            // Turnaround
            GPIO.enable_w1tc = SWDIO_BIT;
            GPIO.out_w1tc = SWCLK_BIT;
            swd_delay(SWD_CLOCK_CYCLES);
            GPIO.out_w1ts = SWCLK_BIT;
            swd_delay(SWD_CLOCK_CYCLES);
            
            value = (data) ? *data : 0;
            for (i = 0; i < 32; i++) {
                if (value & (1UL << i)) {
                    GPIO.enable_w1tc = SWDIO_BIT;
                } else {
                    GPIO.out_w1tc = SWDIO_BIT;
                    GPIO.enable_w1ts = SWDIO_BIT;
                }
                GPIO.out_w1tc = SWCLK_BIT;
                swd_delay(SWD_CLOCK_CYCLES);
                GPIO.out_w1ts = SWCLK_BIT;
                swd_delay(SWD_CLOCK_CYCLES);
            }
            // نوشتن Parity
            parity = __builtin_parity(value);
            if (parity) {
                GPIO.enable_w1tc = SWDIO_BIT;
            } else {
                GPIO.out_w1tc = SWDIO_BIT;
                GPIO.enable_w1ts = SWDIO_BIT;
            }
            GPIO.out_w1tc = SWCLK_BIT;
            swd_delay(SWD_CLOCK_CYCLES);
            GPIO.out_w1ts = SWCLK_BIT;
            swd_delay(SWD_CLOCK_CYCLES);
        }
    }
    
    // Idle
    GPIO.out_w1tc = SWDIO_BIT;
    GPIO.enable_w1ts = SWDIO_BIT;
    GPIO.out_w1tc = SWCLK_BIT;
    swd_delay(SWD_CLOCK_CYCLES);
    GPIO.out_w1ts = SWCLK_BIT;
    swd_delay(SWD_CLOCK_CYCLES);
    
    taskEXIT_CRITICAL(&swd_spinlock);
    
    return ack;
}
```

### توابع سطح بالا:

```c
// خواندن از DP
static uint8_t swd_dp_read(uint8_t addr, uint32_t *data) {
    uint8_t ack = swd_transfer(0, 1, addr, data);
    if (ack == SWD_ACK_OK && addr != DP_RDBUFF) {
        uint32_t dummy;
        swd_transfer(0, 1, DP_RDBUFF, &dummy);
    }
    return ack;
}

// نوشتن به DP
static uint8_t swd_dp_write(uint8_t addr, uint32_t data) {
    return swd_transfer(0, 0, addr, &data);
}

// خواندن از AP
static uint8_t swd_ap_read(uint8_t reg, uint32_t *data) {
    uint32_t select = (reg & 0xF0) | ((reg & 0x0F) << 4);
    swd_dp_write(DP_SELECT, select);
    return swd_transfer(1, 1, AP_DRW, data);
}

// نوشتن به AP
static uint8_t swd_ap_write(uint8_t reg, uint32_t data) {
    uint32_t select = (reg & 0xF0) | ((reg & 0x0F) << 4);
    swd_dp_write(DP_SELECT, select);
    return swd_transfer(1, 0, AP_DRW, &data);
}
```

---

## نکات عملی

### ۱. Critical Section ضروری است
```c
taskENTER_CRITICAL(&swd_spinlock);
// تمام تراکنش اینجا
taskEXIT_CRITICAL(&swd_spinlock);
```

### ۲. Timing صحیح
```
Write: داده قبل از لبه بالارونده تنظیم می‌شود
Read:  داده در لبه پایین‌رونده نمونه‌برداری می‌شود
```

### ۳. Pull-up خارجی
```
حتماً مقاومت 10kΩ روی SWDIO نصب کنید
```

### ۴. Line Reset قبل از ارتباط
```c
swd_line_reset();  // حداقل 50 پالس کلاک با SWDIO=HIGH
```

### ۵. دیباگ بدون لاگ در نقاط بحرانی
```c
// ذخیره نتایج در متغیر
g_last_ack = ack;
g_last_data = value;

// لاگ بعد از تراکنش
ESP_LOGI(TAG, "ACK=%d, Data=0x%08X", g_last_ack, g_last_data);
```

---

## نتیجه‌گیری

پروتکل SWD با وجود سادگی ظاهری، نیازمند دقت بالا در پیاده‌سازی است. موفقیت در این پیاده‌سازی نیازمند:
- کنترل دقیق Timing
- استفاده از Critical Section
- مدیریت صحیح GPIO
- عدم استفاده از لاگ در نقاط بحرانی

کد ارائه شده تمام این موارد را رعایت کرده و باید بتواند ارتباط پایداری با target های ARM برقرار کند.
# شکل پالس‌های پروتکل SWD - توضیح کامل

## ۱. پالس کلاک پایه (SWCLK)

```
     ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐
     │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │
─────┘  └──┘  └──┘  └──┘  └──┘  └──┘  └──┘  └──┘  └─────
     ↑     ↑     ↑     ↑     ↑     ↑     ↑     ↑
   Rising Falling Rising Falling Rising Falling Rising Falling
   Edge   Edge    Edge   Edge    Edge   Edge    Edge   Edge
```

## ۲. نوشتن بیت (Host → Target)

### نوشتن '1':
```
SWCLK:  ─────┐     ┌─────┐     ┌─────
             │     │     │     │
             └─────┘     └─────┘
             ↑     ↑     ↑     ↑
           Falling Rising Falling Rising

SWDIO:  ─────────────┌───────────────
                     │ (HIGH)
                     │
              داده تنظیم می‌شود
              در لبه پایین‌رونده
              ↑
              Host داده را اینجا قرار می‌دهد
              
              Target داده را در لبه بالارونده می‌خواند
              ↑
```

### نوشتن '0':
```
SWCLK:  ─────┐     ┌─────┐     ┌─────
             │     │     │     │
             └─────┘     └─────┘
             ↑     ↑     ↑     ↑
           Falling Rising Falling Rising

 SWDIO:  ─────┐     ┌───────────────
              │(LOW)│
              │     │
              داده تنظیم می‌شود
              در لبه پایین‌رونده
              ↑
              Host داده را اینجا قرار می‌دهد
              
              Target داده را در لبه بالارونده می‌خواند
              ↑
```

## ۳. خواندن بیت (Target → Host)

### خواندن '1':
```
SWCLK:  ─────┐     ┌─────┐     ┌─────
             │     │     │     │
             └─────┘     └─────┘
             ↑     ↑     ↑     ↑
           Falling Rising Falling Rising

SWDIO:  ─────────────┌───────────────
                     │ (HIGH)
                     │
              Target داده را در لبه بالارونده می‌گذارد
              ↑
              
              Host در لبه پایین‌رونده بعدی می‌خواند
              ↑
              (نمونه‌برداری در میانه پالس)
```

## ۴. تراکنش کامل Read (خواندن IDCODE)

```
Phase:   [Request 8 bits]  [Turn] [ACK 3 bits]  [Data 32 bits]  [Parity] [Idle]
        
SWCLK:  ─┐ ┌┐ ┌┐ ┌┐ ┌┐ ┌┐ ┌┐ ┌┐ ┌┐  ┌┐  ┌┐ ┌┐ ┌┐  ┌┐ ┌┐ ┌┐ ┌┐ ... ┌┐  ┌┐
         └─┘└─┘└─┘└─┘└─┘└─┘└─┘└─┘└┘  └┘  └┘ └┘ └┘  └┘ └┘ └┘ └┘     └┘  └┘
         ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑  ↑  ↑  ↑ ↑ ↑  ↑ ↑ ↑ ↑  ↑
         S A R A A P S P  T  A A A  D D D D  P  I
         t P n A A r a a     C C C  0 1 2 3  a  d
         a n W 2 3 i r r     K K K              r  l
         r D   t k   0 1     0 1 2              i  e
         t P   y               t
              t               y

SWDIO:  ─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐
         │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
         └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘
        
        Host Drive ──────┘ Target Drive ──────┘ Host Drive
```

## ۵. جزئیات هر فاز

### Request Phase (8 بیت) - Host Drive:
```
Bit:     Start  APnDP  RnW   A[2]  A[3]  Parity Stop  Park
Value:     1      0     1     0     0     1      0     1

SWCLK:  ─┐  ┌┐  ┌┐  ┌┐  ┌┐  ┌┐  ┌┐  ┌┐  ┌┐
         └──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘└──

SWDIO:  ─┐  ┌─────────────────┐  ┌─────────┐  ┌─
         │  │                 │  │         │  │
         └──┘                 └──┘         └──┘
          ↑  ↑                 ↑  ↑         ↑  ↑
          S  A                 A  P         S  P
          t  P                 a  a         t  a
          a  n                 r  r         o  r
          r  D                 i  i         p  k
          t  P                 t  t            
             (0)               y  y
                               (1)(0)
```

### ACK Phase (3 بیت) - Target Drive:
```
ACK = OK (001):

SWCLK:  ─┐  ┌┐  ┌┐  ┌┐
         └──┘└──┘└──┘└──

SWDIO:  ──────┐  ┌───────
              │  │
              └──┘
               ↑  ↑
               A  A
               C  C
               K  K
               0  1
               (1)(0)
```

## ۶. فرآیند کامل خواندن بیت

```c
// ============================================================
//  خواندن یک بیت - گام به گام
// ============================================================

// گام ۱: SWDIO به ورودی
GPIO.enable_w1tc = SWDIO_BIT;
//     SWDIO: ──────┐ (رها شده، Pull-up آن را HIGH نگه می‌دارد)

// گام ۲: لبه پایین‌رونده کلاک
GPIO.out_w1tc = SWCLK_BIT;
//     SWCLK: ──────┐
//                  │
//                  └────── (LOW)

// گام ۳: تاخیر نصف پریود
swd_delay(SWD_HALF_CYCLES);
//     Target داده را آماده کرده

// گام ۴: خواندن داده
if (GPIO.in & SWDIO_BIT) {
    // داده 1 است
} else {
    // داده 0 است
}
//     ↑ اینجا نمونه‌برداری می‌کنیم

// گام ۵: تاخیر نصف پریود
swd_delay(SWD_HALF_CYCLES);

// گام ۶: لبه بالارونده کلاک
GPIO.out_w1ts = SWCLK_BIT;
//     SWCLK:       ┌────── (HIGH)
//                  │
//     Target داده را عوض می‌کند
```

## ۷. فرآیند کامل نوشتن بیت

```c
// ============================================================
//  نوشتن یک بیت - گام به گام
// ============================================================

// گام ۱: تنظیم داده قبل از لبه بالا
if (bit) {
    GPIO.enable_w1tc = SWDIO_BIT;  // HIGH
    // SWDIO: ──────┐ (رها شده)
} else {
    GPIO.out_w1tc = SWDIO_BIT;     // LOW
    GPIO.enable_w1ts = SWDIO_BIT;  // فعال کردن خروجی
    // SWDIO: ──────┘ (LOW)
}

// گام ۲: لبه پایین‌رونده کلاک
GPIO.out_w1tc = SWCLK_BIT;
//     SWCLK: ──────┐
//                  │
//                  └────── (LOW)

// گام ۳: تاخیر
swd_delay(SWD_CLOCK_CYCLES);

// گام ۴: لبه بالارونده کلاک
GPIO.out_w1ts = SWCLK_BIT;
//     SWCLK:       ┌────── (HIGH)
//                  │
//     ↑ Target اینجا داده را می‌خواند

// گام ۵: تاخیر
swd_delay(SWD_CLOCK_CYCLES);
```

## ۸. دیاگرام کامل تراکنش Read IDCODE

```
Time:   t0   t1   t2   t3   t4   t5   t6   t7   t8   t9   t10  t11  t12
        │    │    │    │    │    │    │    │    │    │    │    │    │
SWCLK:  ─┐   ┌┐   ┌┐   ┌┐   ┌┐   ┌┐   ┌┐   ┌┐   ┌┐   ┌┐   ┌┐   ┌┐
         └───┘└───┘└───┘└───┘└───┘└───┘└───┘└───┘└───┘└───┘└───┘└───
         
SWDIO:  ─┐   ┌─────────────────┐   ┌─────────┐   ┌─────────┐   ┌───
         │   │                 │   │         │   │         │   │
         └───┘                 └───┘         └───┘         └───┘
         
Phase:  [Start][APnDP][RnW][A2][A3][Parity][Stop][Park][Turn][ACK0][ACK1][ACK2]
Value:    1     0      1    0   0    1       0     1     -    1     0     0
Drive:    Host  Host   Host Host Host Host    Host  Host  -    Tgt   Tgt   Tgt
```

## ۹. نکات کلیدی Timing

### برای Write:
```
1. داده را تنظیم کن (قبل از لبه بالا)
2. کلاک LOW
3. تاخیر
4. کلاک HIGH (Target می‌خواند)
5. تاخیر
```

### برای Read:
```
1. کلاک LOW
2. تاخیر نصف
3. نمونه‌برداری (در میانه پالس)
4. تاخیر نصف
5. کلاک HIGH (Target داده جدید می‌گذارد)
6. تاخیر
```

## ۱۰. جدول زمان‌بندی

| عمل | لبه کلاک | SWDIO |
|-----|----------|-------|
| Host داده می‌گذارد | Falling Edge | Stable |
| Target می‌خواند | Rising Edge | Stable |
| Target داده می‌گذارد | Rising Edge | Stable |
| Host می‌خواند | Falling Edge | Sample |

این دیاگرام‌ها نشان می‌دهند که:
- **داده همیشه قبل از لبه فعال کلاک پایدار است**
- **برای Write**: لبه فعال Rising است
- **برای Read**: لبه فعال Falling است
- **نمونه‌برداری در میانه پالس انجام می‌شود**
# مستند کامل SWD (Serial Wire Debug)

## ۱. مقدمه

SWD یک پروتکل دو سیمه برای دیباگ ARM است که جایگزین JTAG شده:

| ویژگی | JTAG | SWD |
|-------|------|-----|
| پین‌ها | 5 (TCK, TMS, TDI, TDO, TRST) | 2 (SWDIO, SWCLK) |
| سرعت | کندتر | سریعتر |
| تشخیص خطا | ندارد | دارد (Parity) |

---

## ۲. سیگنال‌ها

### SWDIO (Serial Wire Data Input/Output)
- دوجهته
- Host → Target (Write)
- Target → Host (Read)

### SWCLK (Serial Wire Clock)
- فقط Host → Target
- همیشه توسط Host کنترل می‌شود

---

## ۳. جهت داده و لبه‌ها

| عملیات | لبه فعال | توضیح |
|--------|----------|-------|
| Host Write | Falling Edge | Host داده را در لبه پایین می‌گذارد |
| Target Read | Rising Edge | Target داده را در لبه بالا می‌خواند |
| Target Write | Rising Edge | Target داده را در لبه بالا می‌گذارد |
| Host Read | Falling Edge | Host داده را در لبه پایین می‌خواند |

---

## ۴. ساختار تراکنش

### ۴.۱ Request Phase (8 بیت)

| بیت | نام | مقدار | توضیح |
|-----|-----|-------|-------|
| 0 | Start | 1 | شروع |
| 1 | APnDP | 0/1 | 0=DP, 1=AP |
| 2 | RnW | 0/1 | 0=Write, 1=Read |
| 3 | A[2] | 0/1 | آدرس بیت 2 |
| 4 | A[3] | 0/1 | آدرس بیت 3 |
| 5 | Parity | 0/1 | فرد = 1 |
| 6 | Stop | 0 | همیشه 0 |
| 7 | Park | 1 | همیشه 1 |

### ۴.۲ ACK Phase (3 بیت LSB-first)

| مقدار | نام | توضیح |
|-------|-----|-------|
| 001 | OK | موفق |
| 010 | WAIT | تلاش مجدد |
| 100 | FAULT | خطا - Sticky bit تنظیم شده |
| 111 | - | Target متصل نیست |

### ۴.۳ Data Phase (33 بیت)

| بیت‌ها | توضیح |
|--------|-------|
| 32 بیت | داده (LSB first) |
| 1 بیت | Parity (فرد = 1) |

---

## ۵. Turnaround Period

### قوانین:
- هر بار SWDIO تغییر جهت می‌دهد → 1 سیکل Turnaround
- در Turnaround، SWDIO باید HIGH باشد (Pull-up)

### جدول Turnaround:

| موقعیت | تغییر جهت | Turnaround |
|--------|----------|------------|
| قبل از ACK | Host → Target | ✅ لازم |
| بعد از ACK (Write) | Target → Host | ✅ لازم |
| بعد از Data (Read) | Target → Host | ✅ لازم |

---

## ۶. رجیسترهای DP (Debug Port)

| آدرس | Read | Write |
|------|------|-------|
| 0x00 | IDCODE | ABORT |
| 0x04 | CTRL/STAT | CTRL/STAT |
| 0x08 | RESEND | SELECT |
| 0x0C | RDBUFF | - |

### ABORT Register:

| بیت | نام | توضیح |
|-----|-----|-------|
| 0 | DAPABORT | لغو AP transaction |
| 1 | STKCMPCLR | پاک کردن STICKYCMP |
| 2 | STKERRCLR | پاک کردن STICKYERR |
| 3 | WDERRCLR | پاک کردن WDATAERR |
| 4 | ORUNERRCLR | پاک کردن STICKYORUN |

### SELECT Register:

| بیت‌ها | نام | توضیح |
|--------|-----|-------|
| [31:24] | APSEL | انتخاب AP |
| [7:4] | APBANKSEL | انتخاب Bank |

---

## ۷. رجیسترهای AP (Access Port)

| آدرس | Bank | نام |
|------|------|-----|
| 0x00 | 0x0 | CSW |
| 0x04 | 0x0 | TAR |
| 0x0C | 0x0 | DRW |
| 0xFC | 0xF | IDR |

### CSW Register:

| بیت‌ها | نام | توضیح |
|--------|-----|-------|
| [2:0] | Size | 010=32-bit |
| [5:4] | AddrInc | 01=Auto-increment |

---

## ۸. توالی راه‌اندازی

| مرحله | عملیات |
|-------|--------|
| 1 | ارسال 0xE79E (JTAG→SWD) |
| 2 | 50+ پالس کلاک با SWDIO=1 |
| 3 | خواندن IDCODE |
| 4 | نوشتن CTRL/STAT (بیت 28 و 30) |
| 5 | نوشتن SELECT = 0xF0 |
| 6 | خواندن AP IDR |

---

## ۹. خواندن حافظه

```c
// 1. SELECT = 0x00
swd_dp_write(DP_SELECT, 0x00);

// 2. CSW = 0x23000012 (32-bit + auto-increment)
swd_ap_write(AP_CSW, 0x23000012);

// 3. TAR = آدرس
swd_ap_write(AP_TAR, address);

// 4. خواندن DRW (اولی dummy است!)
swd_ap_read(AP_DRW, &dummy);  // نتیجه قبلی
swd_ap_read(AP_DRW, &data);   // داده واقعی
```

---

## ۱۰. نوشتن حافظه

```c
// 1. SELECT = 0x00
swd_dp_write(DP_SELECT, 0x00);

// 2. CSW = 0x23000012
swd_ap_write(AP_CSW, 0x23000012);

// 3. TAR = آدرس
swd_ap_write(AP_TAR, address);

// 4. نوشتن DRW
swd_ap_write(AP_DRW, data);
```

---

## ۱۱. خطاهای رایج

| ACK | معنی | راه‌حل |
|-----|------|--------|
| 4 (FAULT) | Sticky bit تنظیم شده | ABORT بنویسید |
| 2 (WAIT) | Target مشغول | تلاش مجدد |
| 7 | Target متصل نیست | بررسی سیم‌کشی |

### پاک کردن خطا:

```c
// ABORT = همه بیت‌ها
swd_dp_write(DP_ABORT, 0x1E);

// یا فقط STICKYERR
swd_dp_write(DP_ABORT, 0x04);
```

---

## ۱۲. نکته مهم: Read Buffer

```c
// AP Read نتیجه قبلی را برمی‌گرداند!
// برای خواندن داده واقعی:
swd_ap_read(AP_DRW, &dummy);  // نتیجه قبلی (دور بریزید)
swd_ap_read(AP_DRW, &data);   // داده واقعی

// یا:
swd_ap_read(AP_DRW, &data);   // شروع تراکنش
swd_dp_read(DP_RDBUFF, &data); // خواندن نتیجه
```

---

## ۱۳. خلاصه کد صحیح

```c
// خواندن حافظه:
swd_dp_write(DP_ABORT, 0x1E);        // پاک کردن خطا
swd_dp_write(DP_SELECT, 0x00);       // SELECT
swd_ap_write(AP_CSW, 0x23000012);   // CSW
swd_ap_write(AP_TAR, addr);          // TAR
swd_ap_read(AP_DRW, &dummy);         // اولین خواندن (dummy)
swd_ap_read(AP_DRW, &data);          // داده واقعی
```

---
بله! این آدرس‌ها برای هر خانواده STM32 فرق می‌کنند:

## جدول آدرس‌های Flash Registers:

| خانواده | FLASH_KEYR | FLASH_CR | FLASH_SR | توضیح |
|---------|-----------|----------|----------|-------|
| **STM32F0** | 0x40022004 | 0x40022010 | 0x4002200C | F030, F031, F051 |
| **STM32F1** | 0x40022004 | 0x40022010 | 0x4002200C | F103, F105 |
| **STM32F2** | 0x40023C04 | 0x40023C10 | 0x40023C0C | F205, F207 |
| **STM32F3** | 0x40022004 | 0x40022010 | 0x4002200C | F303, F334 |
| **STM32F4** | 0x40023C04 | 0x40023C10 | 0x40023C0C | F405, F407, F411 |
| **STM32F7** | 0x40023C04 | 0x40023C10 | 0x40023C0C | F746, F767 |
| **STM32G0** | 0x40022004 | 0x40022010 | 0x4002200C | G030, G071 |
| **STM32G4** | 0x40022004 | 0x40022010 | 0x4002200C | G431, G474 |
| **STM32L0** | 0x40022004 | 0x40022010 | 0x4002200C | L031, L051 |
| **STM32L1** | 0x40023C04 | 0x40023C10 | 0x40023C0C | L151, L152 |
| **STM32L4** | 0x40022004 | 0x40022010 | 0x4002200C | L431, L476 |
| **STM32L5** | 0x40022004 | 0x40022010 | 0x4002200C | L552 |
| **STM32H7** | 0x52002004 | 0x52002010 | 0x5200200C | H723, H743 |
| **STM32WB** | 0x40022004 | 0x40022010 | 0x4002200C | WB55 |
| **STM32WL** | 0x40022004 | 0x40022010 | 0x4002200C | WL55 |

## الگو:

### اکثر خانواده‌ها (F0, F1, F3, G0, G4, L0, L4, L5, WB, WL):
```
FLASH_KEYR = 0x40022004
FLASH_CR   = 0x40022010
FLASH_SR   = 0x4002200C
```

### خانواده‌های F2, F4, F7, L1:
```
FLASH_KEYR = 0x40023C04
FLASH_CR   = 0x40023C10
FLASH_SR   = 0x40023C0C
```

### STM32H7 (متفاوت):
```
FLASH_KEYR = 0x52002004
FLASH_CR   = 0x52002010
FLASH_SR   = 0x5200200C
```

## در فرانت (device-registry):

```javascript
// برای STM32F0:
flashKeyr: 0x40022004,
flashCr: 0x40022010,
flashSr: 0x4002200C

// برای STM32F4:
flashKeyr: 0x40023C04,
flashCr: 0x40023C10,
flashSr: 0x40023C0C

// برای STM32H7:
flashKeyr: 0x52002004,
flashCr: 0x52002010,
flashSr: 0x5200200C
```

## نکته: در فرانت می‌توانید بر اساس خانواده تعیین کنید:

```javascript
getFullDeviceInfo(deviceName) {
    // ...
    
    let flashKeyr = 0x40022004;
    let flashCr = 0x40022010;
    let flashSr = 0x4002200C;
    
    if (deviceName.includes('F2') || deviceName.includes('F4') || 
        deviceName.includes('F7') || deviceName.includes('L1')) {
        flashKeyr = 0x40023C04;
        flashCr = 0x40023C10;
        flashSr = 0x40023C0C;
    } else if (deviceName.includes('H7')) {
        flashKeyr = 0x52002004;
        flashCr = 0x52002010;
        flashSr = 0x5200200C;
    }
    
    return {
        deviceInfo: {
            // ...
            flashKeyr: flashKeyr,
            flashCr: flashCr,
            flashSr: flashSr
        }
    };
}
```

پس بله، این ۳ آدرس برای هر خانواده فرق می‌کند و باید از فرانت ارسال شود.

حتماً. این تابع را به‌عنوان **نمونه موفق نوشتن STM32 Cortex-M0 با SWD و Flash 16-bit** در نظر می‌گیرم.

نکته مهمی که از نسخه موفق تو یاد می‌گیریم این است که در این خانواده، صرفاً `CSW=16-bit` و فرستادن مقدار 16 بیتی کافی نیست؛ داده‌ی `DRW` را به شکل 32 بیتی می‌فرستی و نیمه‌ی غیرهدف را با `0xFFFF` پر می‌کنی:

```c
if ((write_addr & 0x02) == 0) {
    word = 0xFFFF0000 | halfword;
} else {
    word = ((uint32_t)halfword << 16) | 0x0000FFFF;
}
```

یعنی:

```text
address +0 :  [FFFF][DATA16]
address +2 :  [DATA16][FFFF]
```

این جزئیات برای پیاده‌سازی خانواده‌های دیگر **نباید کورکورانه کپی شود**؛ باید بر اساس Flash controller همان خانواده تعیین شود.

همچنین ترتیب موفق این تابع برای M0 فعلاً این است:

```text
ABORT
 ↓
CSW 32-bit
 ↓
خواندن CR
 ↓
Unlock
 ↓
MER = 0
STRT = 0
 ↓
PG = 1
 ↓
CSW 16-bit
 ↓
نوشتن Half-word با DRW 32-bit + 0xFFFF
 ↓
CSW 32-bit
 ↓
PG = 0
```

این را به‌عنوان **الگوی M0 موفق** نگه می‌داریم، نه یک الگوریتم عمومی برای تمام STM32ها.

دقیقاً! این روش ساده و تمیز است! بگذارید کاملش کنیم:

## کد کامل `swd_set_device` با تشخیص word_size:

```c
static bool swd_set_device(const char *device_name) {
    if (!device_name) return false;
    g_device_name = device_name;
    
    // ⭐ تشخیص word_size از نام دستگاه
    if (strstr(device_name, "STM32F0") || 
        strstr(device_name, "STM32G0") || 
        strstr(device_name, "STM32L0") ||
        strstr(device_name, "STM32F1")) {
        g_dev_info.word_size = 16;
        ESP_LOGI(TAG, "📌 Flash Programming: 16-bit (half-word)");
    } else {
        g_dev_info.word_size = 32;
        ESP_LOGI(TAG, "📌 Flash Programming: 32-bit (word)");
    }
    
    return true;
}
```

## و در `swd_write_mem`:

```c
// ===== 7. Write بر اساس word_size =====
    if (word_size == 16) {
        // ⭐ 16-bit mode - CSW از فرانت + 0x01
       uint32_t csw = g_dev_info.csw;  // 0x23000002
       uint32_t csw_16 = csw - 1;      // 0x23000001
        swd_transfer(AP_CSW, 1, 0, &csw_16);
        
        for (uint32_t i = 0; i < size; i += 2) {
            uint32_t write_addr = addr + i;
            uint16_t halfword = data[i] | (data[i+1] << 8);
            uint32_t word;
            
            if ((write_addr & 0x02) == 0) {
                word = 0xFFFF0000 | halfword;
            } else {
                word = ((uint32_t)halfword) << 16 | 0x0000FFFF;
            }
            
            swd_transfer(AP_TAR, 1, 0, &write_addr);
            if (!swd_transfer(AP_DRW, 1, 0, &word)) {
                snprintf(r.message, sizeof(r.message), 
                         "Write failed at 0x%08" PRIX32, addr + i);
                return r;
            }
            
            r.bytes_written += 2;
        }
    } else {
        // ⭐ 32-bit mode - CSW از فرانت
        swd_transfer(AP_CSW, 1, 0, &csw);  // ⭐ از فرانت!
        
        for (uint32_t i = 0; i < size; i += 4) {
            uint32_t word = 0;
            uint32_t remaining = size - i;
            uint32_t bytes = (remaining < 4) ? remaining : 4;
            
             uint32_t word = data[i] | (data[i+1] << 8) | (data[i+2] << 16) | (data[i+3] << 24);
            
            uint32_t write_addr = addr + i;
            swd_transfer(AP_TAR, 1, 0, &write_addr);
            if (!swd_transfer(AP_DRW, 1, 0, &word)) {
                snprintf(r.message, sizeof(r.message), 
                         "Write failed at 0x%08" PRIX32, addr + i);
                return r;
            }
            
            r.bytes_written += bytes;
        }
    }

```

## مزایا:

1. **ساده و تمیز** - فقط یک `if/else`
2. **قابل گسترش** - خانواده‌های جدید را به راحتی اضافه کنید
3. **بدون هاردکد** - از `g_dev_info.word_size`
4. **لاگ واضح** - مشخص می‌کند 16-bit یا 32-bit

## برای اضافه کردن خانواده جدید:

```c
if (strstr(device_name, "STM32F0") || 
    strstr(device_name, "STM32G0") || 
    strstr(device_name, "STM32L0") ||
    strstr(device_name, "STM32F1") ||
    strstr(device_name, "STM32L1") ||  // ⭐ جدید!
    strstr(device_name, "nRF51")) {     // ⭐ جدید!
    g_dev_info.word_size = 16;
} else {
    g_dev_info.word_size = 32;
}
```

**این روش عالی است!** 🎉




## LPC1768/1788 Flash Programming:

آره! برای LPC1768/1788 همه چیز متفاوت است!

### 1. Flash Layout:
```
LPC1768:
- Flash: 0x00000000 - 0x00080000 (512KB)
- RAM: 0x10000000 - 0x10008000 (32KB)
- AHB SRAM: 0x2007C000 - 0x20083FFF

LPC1788:
- Flash: 0x00000000 - 0x00080000 (512KB)
- RAM: 0x10000000 - 0x10010000 (64KB)
```

### 2. IAP Command Interface:

```c
// آدرس IAP: 0x1FFF1FF1
// این یک تابع در ROM است!

// Command Codes:
#define IAP_PREPARE_SECTORS    50
#define IAP_COPY_RAM_TO_FLASH  51
#define IAP_ERASE_SECTORS      52
#define IAP_BLANK_CHECK        53
#define IAP_READ_PART_ID       54
#define IAP_READ_BOOT_VERSION  55
#define IAP_COMPARE            56
#define IAP_REINVOKE_ISP       57
#define IAP_READ_SERIAL        58
```

### 3. Read (مستقیم):
```c
// خواندن Flash مستقیم است:
// فقط TAR = addr و DRW را بخوانید
// مثل STM32!
```

### 4. Erase (با IAP):
```c
// 1. نوشتن کد IAP در RAM
// 2. اجرای IAP Command با کد 52 (Erase)
// 3. منتظر ماندن
```

### 5. Write (با IAP):
```c
// 1. Prepare Sector (کد 50)
// 2. Erase Sector (کد 52)
// 3. نوشتن داده در RAM
// 4. Copy RAM to Flash (کد 51)
// 5. Compare (کد 56)
```

## تفاوت اصلی:

| مورد | STM32 | LPC1768/1788 |
|------|-------|--------------|
| Flash Base | 0x08000000 | 0x00000000 |
| RAM Base | 0x20000000 | 0x10000000 |
| Read | مستقیم | مستقیم ✅ |
| Erase | FLASH_CR | IAP Command |
| Write | FLASH_CR | IAP Command |
| Unlock | KEYR | IAP Unlock |
| Registers | FLASH Registers | بدون Register! |

## برای LPC1768/1788 باید:

```c
// 1. نوشتن کد در RAM
// 2. اجرای IAP Command
// 3. کاملاً متفاوت از STM32

typedef struct {
    uint32_t cmd;      // Command
    uint32_t par[4];   // Parameters
    uint32_t stat;     // Status
    uint32_t res[4];   // Result
} iap_command_t;

// آدرس IAP
#define IAP_ADDRESS 0x1FFF1FF1

// فراخوانی IAP:
typedef void (*iap_func_t)(iap_command_t*, iap_command_t*);
iap_func_t iap = (iap_func_t)IAP_ADDRESS;

iap_command_t cmd, res;
cmd.cmd = 50;  // Prepare
cmd.par[0] = start_sector;
cmd.par[1] = end_sector;
iap(&cmd, &res);
```

## خلاصه:

| عملیات | STM32 | LPC1768/1788 |
|--------|-------|--------------|
| Read | ✅ مشابه | ✅ مشابه |
| Erase | ❌ متفاوت | IAP Command 52 |
| Write | ❌ متفاوت | IAP Command 51 |
| Unlock | ❌ متفاوت | IAP Command |

**پس برای LPC1768/1788  ید کد کاملاً جدید بنویسیم!**

**Read مشابه است ولی Erase و Write کاملاً متفاوت با IAP!**




## ساختار پیشنهادی:
برای اینکه هر خانواده ارم یه معماری داخلی برای نوشت خوندن فلش داره با ۳ تابع نوشتن خواندن پاک کردن کلی نمیتونم 
وروگرمر همه کاره اکی کنم پس مماری اس دبلیو دی به این ترتیب تغیر میدم هرچی جلوتر میرم میفهم که چقدر کارم سخت پیچیده شده
ساختار به صورت زیر تغیر میدم
```c
// ============================================================
//  Flash Operations Interface
// ============================================================

typedef struct {
    const char *name;  // نام خانواده
    proto_result_t (*erase)(uint32_t addr, uint32_t size);
    proto_result_t (*write)(uint32_t addr, const uint8_t *data, uint32_t size);
    proto_result_t (*read)(uint32_t addr, uint8_t *buf, uint32_t size);
} flash_ops_t;

// ============================================================
//  STM32F0/F1 (16-bit)
// ============================================================
static proto_result_t stm32f0_erase(uint32_t addr, uint32_t size) {
    // Unlock + MER + STRT
    // ...
}

static proto_result_t stm32f0_write(uint32_t addr, const uint8_t *data, uint32_t size) {
    // 16-bit half-word با 0xFFFF padding
    // ...
}

// ============================================================
//  STM32F4/F7 (32-bit)
// ============================================================
static proto_result_t stm32f4_erase(uint32_t addr, uint32_t size) {
    // Unlock + Sector Erase
    // ...
}

static proto_result_t stm32f4_write(uint32_t addr, const uint8_t *data, uint32_t size) {
    // 32-bit word write
    // ...
}

// ============================================================
//  LPC1768/1788 (IAP)
// ============================================================
static proto_result_t lpc1768_erase(uint32_t addr, uint32_t size) {
    // IAP Command 52
    // ...
}

static proto_result_t lpc1768_write(uint32_t addr, const uint8_t *data, uint32_t size) {
    // IAP Command 51
    // ...
}

// ============================================================
//  جدول خانواده‌ها
// ============================================================
static const flash_ops_t flash_ops_table[] = {
    {
        .name = "STM32F0",
        .erase = stm32f0_erase,
        .write = stm32f0_write,
        .read = swd_read_mem,  // مشترک
    },
    {
        .name = "STM32F4",
        .erase = stm32f4_erase,
        .write = stm32f4_write,
        .read = swd_read_mem,  // مشترک
    },
    {
        .name = "LPC1768",
        .erase = lpc1768_erase,
        .write = lpc1768_write,
        .read = swd_read_mem,  // مشترک
    },
};

// ============================================================
//  تابع کلی - بر اساس family
// ============================================================
static proto_result_t swd_erase(void) {
    const char *family = g_device_name;
    
    // پیدا کردن خانواده
    for (int i = 0; i < sizeof(flash_ops_table) / sizeof(flash_ops_table[0]); i++) {
        if (strstr(family, flash_ops_table[i].name)) {
            return flash_ops_table[i].erase(0, g_dev_info.flash_size);
        }
    }
    
    // پیش‌فرض STM32F0
    return stm32f0_erase(0, g_dev_info.flash_size);
}

static proto_result_t swd_write_mem(uint32_t addr, const uint8_t *data, uint32_t size) {
    const char *family = g_device_name;
    
    for (int i = 0; i < sizeof(flash_ops_table) / sizeof(flash_ops_table[0]); i++) {
        if (strstr(family, flash_ops_table[i].name)) {
            return flash_ops_table[i].write(addr, data, size);
        }
    }
    
    return stm32f0_write(addr, data, size);
}
```

## مزایا:

1. **هر خانواده جداگانه** - کد تمیز و قابل نگهداری
2. **اضافه کردن آسان** - فقط یک struct جدید
3. **Read مشترک** - چون خواندن SWD یکسان است
4. **قابل تست** - هر خانواده جداگانه تست می‌شود

## برای اضافه کردن خانواده جدید:

```c
// 1. توابع erase و write را بنویسید
static proto_result_t nrf52_erase(uint32_t addr, uint32_t size) { ... }
static proto_result_t nrf52_write(uint32_t addr, const uint8_t *data, uint32_t size) { ... }

// 2. به جدول اضافه کنید
{
    .name = "nRF52",
    .erase = nrf52_erase,
    .write = nrf52_write,
    .read = swd_read_mem,
},
```

**این بهترین معماری برای پروگرمر چند خانواده است!** 🎉

 LPC ها Flash 32-bit می‌نویسند (word write).

## بررسی لینک NAND:

https://github.com/openocd-org/openocd/tree/master/src/flash/nand

OpenOCD NAND Flash Drivers:
```
src/flash/nand/
├── nand.c          ← NAND Flash Controller
├── nand_ecc.c      ← Error Correction Code
├── nand_manufacturer.c ← تشخیص سازنده
├── at91sam9.c      ← AT91SAM9 NAND
├── davinci.c       ← TI DaVinci NAND
├── lpc3180.c       ← LPC3180 NAND
├── mx3.c           ← i.MX3 NAND
├── orion.c         ← Marvell Orion NAND
├── s3c24xx.c       ← Samsung S3C24xx NAND
├── s3c2412.c       ← Samsung S3C2412 NAND
├── s3c2440.c       ← Samsung S3C2440 NAND
└── ...
```

## تفاوت NOR و NAND Flash:

### NOR Flash (LPC, STM32, nRF, SAM):
```c
// دسترسی مستقیم مثل RAM
// خواندن: مستقیم از آدرس
// نوشتن: word (32-bit) یا half-word (16-bit)
// Erase: Sector/Page

// LPC1768:
// Flash Base: 0x00000000
// نوشتن 32-bit word
uint32_t word = data[i] | (data[i+1] << 8) | (data[i+2] << 16) | (data[i+3] << 24);
swd_transfer(AP_DRW, 1, 0, &word);
```

### NAND Flash (کاملاً متفاوت!):
```c
// دسترسی از طریق Controller
// خواندن: Page Read با ECC
// نوشتن: Page Program
// Erase: Block Erase

// ساختار:
// Page Size: 512/2048/4096 بایت
// Block Size: 16/64/128/256 KB
// نیاز به ECC (Error Correction Code)
// نیاز به Bad Block Management
```

## NAND Flash Programming:

```c
// 1. خواندن Page
// 2. نوشتن Page (Page Program)
// 3. Erase Block
// 4. ECC برای تشخیص خطا
// 5. Bad Block Management

// NAND Command:
#define NAND_CMD_READ_1ST   0x00
#define NAND_CMD_READ_2ND   0x30
#define NAND_CMD_WRITE_1ST  0x80
#define NAND_CMD_WRITE_2ND  0x10
#define NAND_CMD_ERASE_1ST  0x60
#define NAND_CMD_ERASE_2ND  0xD0
#define NAND_CMD_STATUS     0x70
#define NAND_CMD_READ_ID    0x90
#define NAND_CMD_RESET      0xFF
```

## جدول تفاوت:

| مورد | NOR Flash | NAND Flash |
|------|-----------|------------|
| دسترسی | مستقیم مثل RAM | از طریق Controller |
| خواندن | مستقیم | Page Read |
| نوشتن | Word/Half-word | Page Program |
| Erase | Sector/Page | Block Erase |
| ECC | معمولاً ندارد | نیاز دارد! |
| Bad Block | ندارد | نیاز دارد! |
| سرعت خواندن | سریع | کندتر |
| سرعت نوشتن | کند | سریعتر |
| قیمت | گرانتر | ارزانتر |
| کاربرد | برنامه (Code) | ذخیره‌سازی (Data) |

## LPC با NAND Flash:

بعضی LPC ها NAND Controller دارند:
```
LPC3180: NAND Flash Controller
LPC313x: NAND Flash Controller
LPC43xx: EMC با NAND
```

اما LPC1768/1788 **فقط NOR Flash** دارند!

## پس:

### LPC1768/1788:
- ✅ NOR Flash داخلی
- ✅ نوشتن 32-bit word
- ✅ استفاده از IAP

### NAND Flash:
- ❌ LPC1768/1788 ندارند
- ❌ نیاز به Controller جداگانه
- ❌ کاملاً متفاوت از NOR

**LPC1768/1788 فقط NOR Flash دارند! NAND Flash چیز دیگری است!** 🎉