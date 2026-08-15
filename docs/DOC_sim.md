آره! دقیقاً دو حالت داریم:

---

## Mode 1: **SIM Reader** (خوندن سیم‌کارت)

ESP32 جایگزین **PIC** میشه و سیم‌کارت رو میخونه:

```
ESP32 (Master)          SIM Card (Slave)
    │                       │
    ├── CLK ────────────────► C3 (Clock)
    ├── RST ────────────────► C2 (Reset)
    ├── VCC ────────────────► C1 (VCC)
    ├── I/O ◄───────────────► C7 (Data)
    └── GND ────────────────► C5 (GND)
```

**ESP32:** CLK رو تولید میکنه، RST رو High/Low میکنه، VCC رو میدن
**SIM:** ATR میده، به دستورات جواب میده

---

## Mode 2: **SIM Emulator** (شبیه‌سازی سیم‌کارت)

ESP32 خودش رو جای سیم‌کارت جا میزنه:

```
گوشی (Master)           ESP32 SIM Emu (Slave)
    │                       │
    ├── CLK ────────────────► C3 (ورودی - گوشی میده)
    ├── RST ────────────────► C2 (ورودی - گوشی میده)
    ├── VCC ◄───────────────► C1 (ورودی - گوشی میده)
    ├── I/O ◄───────────────► C7 (Data)
    └── GND ────────────────► C5 (GND)
```

**گوشی:** CLK میده، RST رو میکشه پایین، VCC میده
**ESP32:** منتظر RST LOW میمونه، ATR میده، به دستورات جواب میده

---

## تفاوت کلیدی:

| ویژگی | Reader Mode | Emulator Mode |
|--------|:---:|:---:|
| **CLK** | ESP32 تولید میکنه (LEDC) | گوشی تولید میکنه (ورودی ESP32) |
| **RST** | ESP32 کنترل میکنه | گوشی کنترل میکنه (ESP32 میخونه) |
| **VCC** | ESP32 میدن | گوشی میدن (ESP32 تغذیه میشه!) |
| **I/O** | Half-Duplex | Half-Duplex |
| **ATR** | ESP32 دریافت میکنه | **ESP32 ارسال میکنه** |

---

## نکته مهم برای Emulator:

**ESP32 باید با ولتاژ گوشی کار کنه!**

- گوشی VCC = 3V یا 5V میده
- ESP32 = 3.3V
- **اگه گوشی 5V بده، ESP32 میسوزه!**
- راه حل: **Level Shifter** یا **ESP32 با تغذیه جدا**

---

## سخت‌افزار Emulator:

```
گوشی                            ESP32
─────                          ──────
SIM_VCC (C1) ──► Level Shift ──► 3.3V (تغذیه ESP32)
SIM_RST (C2) ──► Level Shift ──► GPIO19 (ورودی)
SIM_CLK (C3) ──► GPIO18 (ورودی - interrupt)
SIM_I/O (C7) ◄── Level Shift ──► GPIO23 (UART)
SIM_GND (C5) ───────────────────► GND
```

---

## کد Emulator - تشخیص RST:

```c
// Emulator Mode: منتظر RST LOW از گوشی
static bool sim_emu_wait_reset(void) {
    ESP_LOGI(TAG, "⏳ Waiting for RESET from phone...");
    
    // صبر کن RST بیاد پایین
    while (gpio_get_level(SIM_RST_PIN) == 1) {
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    
    ESP_LOGI(TAG, "🔌 RESET detected! Sending ATR...");
    
    // 40000 کلاک صبر کن (مثل کد PIC)
    esp_rom_delay_us(8000);  // ~40000 / 5MHz
    
    // ATR بفرست
    sim_send_atr();
    
    return true;
}
```

---

## کد Reader - کنترل RST:

```c
// Reader Mode: ESP32 RST رو کنترل میکنه
static bool sim_reader_activate(void) {
    ESP_LOGI(TAG, "🔌 Activating SIM Card...");
    
    // VCC ON
    gpio_set_level(SIM_VCC_PIN, 1);
    vTaskDelay(pdMS_TO_TICKS(10));
    
    // CLK ON (LEDC)
    // ...
    
    // RST LOW → HIGH
    gpio_set_level(SIM_RST_PIN, 0);
    vTaskDelay(pdMS_TO_TICKS(100));
    gpio_set_level(SIM_RST_PIN, 1);
    
    // منتظر ATR
    uint8_t atr[32];
    int len = uart_read_bytes(sim_uart, atr, sizeof(atr), pdMS_TO_TICKS(2000));
    
    if (len > 0 && atr[0] == 0x3B) {
        ESP_LOGI(TAG, "✅ ATR received: %d bytes", len);
        return true;
    }
    
    return false;
}
```

---

## انتخاب Mode از فرانت:

```javascript
// توی getConfig:
if (protocol === 'sim') {
    config.simMode = document.getElementById('simMode')?.value || 'reader';
    // 'reader' یا 'emulator'
}
```

---

## جمع‌بندی:

| Mode | RST | CLK | VCC | ATR |
|------|:---:|:---:|:---:|:---:|
| **Reader** | ESP32 → SIM | ESP32 → SIM | ESP32 → SIM | ESP32 ← SIM |
| **Emulator** | Phone → ESP32 | Phone → ESP32 | Phone → ESP32 | **ESP32 → Phone** |

