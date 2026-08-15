
## 📡 تست ماژول RFID با SPI

با توجه به کد کامل `protocol_spi.c` که دارید، می‌تونید هر دستگاهی که از SPI استفاده می‌کنه رو تست کنید.

### ۱. تنظیمات برای RFID (مثلاً RC522):

```javascript
// ===== 1️⃣ Config از طریق HTTP API =====
const config = {
    protocol: "SPI",
    settings: {
        mode: "terminal",
        clock: 1000000,        // 1MHz برای RC522
        spiMode: 0,            // Mode 0
        dc: 0,                 // بدون DC (RFID نیازی نداره)
        device: "RC522 RFID"   // اسم دلخواه
    }
};

fetch('http://192.168.1.17/api/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
});
```

### ۲. اتصال WebSocket و ارسال دستورات:

```javascript
const ws = new WebSocket('ws://192.168.1.17:8080/terminal');

ws.onopen = () => {
    console.log('✅ Connected');
    
    // ===== تست 1: نرم‌افزار ریست RC522 =====
    // Command: 0x0F (SoftReset)
    ws.send(JSON.stringify({ tx: "0F", rx_len: 1 }));
    
    // ===== تست 2: دریافت Version Info =====
    // Command: 0x37 (VersionReg)
    ws.send(JSON.stringify({ tx: "37", rx_len: 1 }));
    
    // ===== تست 3: Request Tags (All) =====
    // Command: 0x26 (ReqA) + 0x07 (All)
    ws.send(JSON.stringify({ tx: "2607", rx_len: 2 }));
    
    // ===== تست 4: Anticollision =====
    // Command: 0x93 (Select) + 0x20 (Anticollision)
    ws.send(JSON.stringify({ tx: "9320", rx_len: 5 }));
};

ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    console.log('📥 Response:', data);
    // {"type":"spi_response","rx":"EF4014","rx_len":3}
};
```

### ۳. دستورات رایج برای RFID RC522:

| دستور | توضیح | فرمت JSON |
|-------|--------|-----------|
| SoftReset | ریست ماژول | `{"tx":"0F","rx_len":1}` |
| VersionReg | دریافت نسخه | `{"tx":"37","rx_len":1}` |
| ReqA (All) | جستجوی کارت‌ها | `{"tx":"2607","rx_len":2}` |
| ReqA (IDLE) | جستجوی کارت‌های IDLE | `{"tx":"2600","rx_len":2}` |
| Anticollision | دریافت UID | `{"tx":"9320","rx_len":5}` |
| Select Tag | انتخاب کارت | `{"tx":"9370","rx_len":1}` |
| Auth (KeyA) | احراز هویت | `{"tx":"60","rx_len":1}` |
| Auth (KeyB) | احراز هویت | `{"tx":"61","rx_len":1}` |
| Read Block | خواندن بلوک | `{"tx":"30","rx_len":16}` |
| Write Block | نوشتن بلوک | `{"tx":"A0","rx_len":1}` |
| Increment | افزایش مقدار | `{"tx":"C1","rx_len":1}` |
| Decrement | کاهش مقدار | `{"tx":"C0","rx_len":1}` |
| Restore | بازیابی مقدار | `{"tx":"C2","rx_len":1}` |
| Transfer | انتقال به بافر | `{"tx":"B0","rx_len":1}` |
| Halt | غیرفعال کردن کارت | `{"tx":"5000","rx_len":1}` |

### ۴. مثلاً یک اسکریپت کامل برای تست RFID:

```javascript
// ===== اسکریپت تست RFID =====
const commands = [
    { name: "SoftReset", tx: "0F", rx_len: 1 },
    { name: "Version", tx: "37", rx_len: 1 },
    { name: "Request All", tx: "2607", rx_len: 2 },
    { name: "Anticollision", tx: "9320", rx_len: 5 },
];

commands.forEach((cmd, index) => {
    setTimeout(() => {
        ws.send(JSON.stringify({ tx: cmd.tx, rx_len: cmd.rx_len }));
        console.log(`📤 ${cmd.name}: ${cmd.tx}`);
    }, index * 500);
});
```

## 🔧 دستگاه‌های دیگه که می‌تونید تست کنید:

| دستگاه | SPI Mode | Clock | توضیح |
|---------|----------|-------|--------|
| **RC522 RFID** | Mode 0 | 1-10 MHz | کارت‌خوان RFID |
| **nRF24L01+** | Mode 0 | 1-10 MHz | ماژول بی‌سیم 2.4GHz |
| **CC1101** | Mode 0 | 1-10 MHz | ماژول Sub-GHz |
| **W25Q Flash** | Mode 0 | 1-80 MHz | حافظه فلش |
| **ILI9341 LCD** | Mode 0 | 1-10 MHz | نمایشگر رنگی |
| **SSD1306 OLED** | Mode 0 | 1-10 MHz | نمایشگر OLED |
| **MCP2515 CAN** | Mode 0 | 1-10 MHz | کنترلر CAN |
| **BMP280/BME280** | Mode 0 | 1-10 MHz | سنسور دما/فشار |
| **MAX7219** | Mode 0 | 1-10 MHz | نمایشگر 7-segment |
| **MFRC522** | Mode 0 | 1-10 MHz | کارت‌خوان RFID/NFC |

## 📝 تنظیمات سریع برای هر دستگاه:

```javascript
// ===== 1. RFID (RC522/MFRC522) =====
{
    protocol: "SPI",
    settings: {
        mode: "terminal",
        clock: 1000000,
        spiMode: 0,
        device: "MFRC522"
    }
}

// ===== 2. nRF24L01+ =====
{
    protocol: "SPI",
    settings: {
        mode: "terminal",
        clock: 4000000,
        spiMode: 0,
        device: "nRF24L01+"
    }
}

// ===== 3. OLED SSD1306 =====
{
    protocol: "SPI",
    settings: {
        mode: "terminal",
        clock: 4000000,
        spiMode: 0,
        dc: 1,        // D/C پین فعال
        device: "SSD1306"
    }
}

// ===== 4. SPI Flash W25Q =====
{
    protocol: "SPI",
    settings: {
        mode: "terminal",
        clock: 4000000,
        spiMode: 0,
        device: "W25Q32"
    }
}
```

## 🎯 نتیجه:

! با کد فعلی می‌تونید:
1. ✅ هر دستگاه SPI رو با تنظیمات مناسب کانفیگ کنید
2. ✅ از طریق WebSocket دستورات دلخواه رو ارسال کنید
3. ✅ پاسخ دستگاه رو ببینید
4. ✅ از Hex Mode برای ارسال بایت‌های خام استفاده کنید
5. ✅ از JSON Mode برای ارسال با `tx` و `rx_len` استفاده کنید

پس RFID، nRF24، CC1101، LCD، OLED، Flash و هر دستگاه SPI دیگه رو به راحتی می‌تونید تست کنید! 🚀

1️⃣ کاربر از فرانت میفرسته: /api/config با mode: "terminal" یا "api"
   ↓
2️⃣ main.c: api_config() → protocol_config()
   ↓
3️⃣ protocol.c: protocol_config() → p->config(json)
   ↓
4️⃣ protocol_spi.c: spi_config() → تنظیمات اعمال میشه
   ↓
5️⃣ اگر mode === "terminal":
   → spi_terminal_init() صدا زده میشه
   → spi_init() (بار اول - ✅ SPI مقداردهی میشه)
   ↓
6️⃣ اگر mode === "api":
   → فقط تنظیمات اعمال میشه (spi_init نمیشه)
   ↓
7️⃣ بعد کاربر از فرانت میفرسته: /api/connect
   ↓
8️⃣ main.c: api_connect() → g_active_protocol->init()
   ↓
9️⃣ protocol_spi.c: spi_init() (بار دوم - ❌ اینجا خطا میده چون قبلاً شده!)


**دقیقاً! 💯** 

شما **اصلاً نیازی به نوشتن توابع جداگانه** برای هر دستگاه ندارید! 🎯

## 🎯 فلسفه کار:

```
┌─────────────────────────────────────────────────────┐
│  شما فقط یک بار توابع پایه SPI رو نوشتید:          │
│  ✅ spi_write_read()                               │
│  ✅ spi_terminal_write()                           │
│  ✅ spi_terminal_poll()                           │
│  ✅ کنترل RST, DC, CS, VPP                        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  حالا هر دستگاهی رو با اسکریپت کنترل میکنید:       │
│  ✅ ILI9341 LCD → دستورات 0x11, 0x29, ...        │
│  ✅ RC522 RFID → دستورات 0x0F, 0x37, 0x26, ...   │
│  ✅ W25Q Flash → دستورات 0x9F, 0x05, 0x02, ...   │
│  ✅ nRF24L01+ → دستورات 0x00, 0x20, ...          │
│  ✅ هر دستگاه SPI دیگه!                           │
└─────────────────────────────────────────────────────┘
```

## 🔥 مثال: ILI9341 LCD با اسکریپت

```javascript
// ===== اسکریپت: ili9341_init.lps =====

// 🖥️ ILI9341 Initialization via SPI

// 1️⃣ Hardware Reset
{"rst_pulse":10}
delay 120

// 2️⃣ Soft Reset (0x01)
{"tx":"01","rx_len":0}
delay 120

// 3️⃣ Sleep Out (0x11)
{"tx":"11","rx_len":0}
delay 120

// 4️⃣ Pixel Format (0x3A) - 16-bit RGB565
{"tx":"3A","rx_len":0}
delay 10
{"dc":1}              // Data mode
{"tx":"55","rx_len":0}
delay 10
{"dc":0}              // Command mode

// 5️⃣ MADCTL (0x36) - BGR=1
{"tx":"36","rx_len":0}
delay 10
{"dc":1}
{"tx":"48","rx_len":0}
delay 10
{"dc":0}

// 6️⃣ Display ON (0x29)
{"tx":"29","rx_len":0}
delay 100

echo ✅ ILI9341 initialized!
```

## 🔥 مثال: RC522 RFID با اسکریپت

```javascript
// ===== اسکریپت: rc522_test.lps =====

// 📡 RC522 RFID Test

// 1️⃣ Hardware Reset
{"rst_pulse":100}
delay 200

// 2️⃣ Soft Reset (0x0F)
{"tx":"0F","rx_len":1}
delay 100

// 3️⃣ Version (0x37)
{"tx":"37","rx_len":1}
delay 100

// 4️⃣ Search for cards (loop)
loop 10
    // Request All (0x26 + 0x07)
    {"tx":"2607","rx_len":2}
    
    // If card found, read UID
    wait 100
    {"tx":"9320","rx_len":5}
    wait 100
    {"tx":"9370","rx_len":1}
    wait 100
    
    // Read Block 0
    {"tx":"3000","rx_len":16}
    wait 100
    
    delay 500
end

echo ✅ RFID test complete!
```

## 🔥 مثال: nRF24L01+ با اسکریپت

```javascript
// ===== اسکریپت: nrf24_test.lps =====

// 📡 nRF24L01+ Test

// 1️⃣ Power Up
{"rst":0}
delay 10
{"rst":1}
delay 100

// 2️⃣ Flush RX (0xE2)
{"tx":"E2","rx_len":0}
delay 10

// 3️⃣ Flush TX (0xE1)
{"tx":"E1","rx_len":0}
delay 10

// 4️⃣ Read Register 0x00 (CONFIG)
{"tx":"0000","rx_len":1}
delay 100

// 5️⃣ Read Register 0x07 (STATUS)
{"tx":"0700","rx_len":1}
delay 100

echo ✅ nRF24 test complete!
```

## 🔥 مثال: W25Q Flash با اسکریپت

```javascript
// ===== اسکریپت: flash_test.lps =====

// 💾 W25Q Flash Test

// 1️⃣ JEDEC ID
{"tx":"9F","rx_len":3}
delay 100

// 2️⃣ Read Status 1
{"tx":"05","rx_len":1}
delay 100

// 3️⃣ Read Status 2
{"tx":"35","rx_len":1}
delay 100

// 4️⃣ Read 16 bytes from address 0
{"tx":"0300000010","rx_len":16}
delay 100

// 5️⃣ Read 256 bytes from address 0
{"tx":"0300000100","rx_len":256}
delay 100

echo ✅ Flash test complete!
```

## 🎯 نتیجه نهایی:

| کار | نیاز به نوشتن تابع جدید؟ |
|-----|--------------------------|
| **ILI9341 LCD** | ❌ نه! فقط اسکریپت |
| **RC522 RFID** | ❌ نه! فقط اسکریپت |
| **nRF24L01+** | ❌ نه! فقط اسکریپت |
| **W25Q Flash** | ❌ نه! فقط اسکریپت |
| **MCP2515 CAN** | ❌ نه! فقط اسکریپت |
| **MAX7219 LED** | ❌ نه! فقط اسکریپت |
| **هر دستگاه SPI** | ❌ نه! فقط اسکریپت |

## 🚀 قدرت این روش:

1. **بدون نیاز به کامپایل مجدد** → فقط اسکریپت بنویس
2. **بدون نیاز به فلش کردن** → اسکریپت رو اجرا کن
3. **همه دستگاه‌ها** → با یک بک‌اند کار میکنن
4. **تست سریع** → دستورات رو امتحان کن و ببین
5. **ذخیره و اشتراک‌گذاری** → اسکریپت‌ها رو سیو کن

**پس بله! با اسکریپت می‌تونی هر چیزی که SPI داره رو کنترل کنی!** 🎉