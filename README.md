```markdown
# 📖 README کامل L-Programmer

## 🔧 L-Programmer - پروگرمر و دیباگر جهانی، بی‌سیم و مبتنی بر وب

**نسخه:** 1.0.0  
**تاریخ:** 2026  
**مجوز:** MIT  
**وضعیت:** 🚧 در حال توسعه

---

## 🎯 معرفی

**L-Programmer** یک ابزار **متن‌باز** و **حرفه‌ای** برای برنامه‌ریزی، دیباگ و ارتباط با طیف گسترده‌ای از میکروکنترلرها، حافظه‌ها، FPGA ها و پروتکل‌های صنعتی است.

این پروژه با استفاده از **ESP32** و رابط کاربری **وب‌محور**، جایگزین ابزارهای تخصصی متعددی می‌شود:

| ابزار سنتی | L-Programmer |
|-------------|--------------|
| ST-Link | ✅ SWD/JTAG |
| J-Link | ✅ SWD/JTAG + CMSIS-DAP |
| USBasp | ✅ ISP (AVR) |
| PICkit | ✅ ICSP (PIC) |
| CH341A | ✅ SPI Flash |
| Bus Pirate | ✅ UART/SPI/I2C/1-Wire |
| ELM327 | ✅ OBD-II |
| ST-Link/V2 (STM8) | ✅ SWIM |
| Xilinx Platform Cable | ✅ XVC (FPGA) |
| TI CC Debugger | ✅ CC-DBG |
| BDM Debugger | ✅ BDM (NXP S12) |
| USB-to-Serial | ✅ UART Terminal |
| Logic Analyzer | ✅ 16CH Logic Analyzer |

---

## ✨ ویژگی‌ها

### 🖥️ سخت‌افزار

| ویژگی | توضیح |
|--------|--------|
| **پردازنده** | ESP32 Dual-Core 240MHz |
| **WiFi** | 802.11 b/g/n |
| **حافظه** | 4MB Flash + 1MB SPIFFS |
| **GPIO** | 20+ پین با Level Shifter |
| **VPP** | 12V Boost Converter (برای PIC) |
| **ADC** | 2CH (ولتاژ/جریان) |
| **DAC** | 2CH |
| **کانکتور** | 10 پین استاندارد + 20 پین توسعه |
| **تغذیه هدف** | 3.3V / 5V / 12V |

### 💻 نرم‌افزار

| ویژگی | توضیح |
|--------|--------|
| **وب‌سرور** | بدون نیاز به نصب نرم‌افزار |
| **WebSocket** | ارتباط Real-time |
| **REST API** | 11+ endpoint |
| **i18n** | فارسی، انگلیسی، عربی |
| **Hex Editor** | ویرایش آنلاین با Diff/Compare |
| **Fuse Config** | فیوزبیت‌ها |
| **Terminal** | ترمینال چندمنظوره 40+ پروتکل |
| **Debugger** | دیباگ ARM از طریق OpenOCD |
| **Script Engine** | اجرای دستورات متوالی |
| **Logic Analyzer** | آنالیز سیگنال 16CH |
| **PWA** | نصب روی موبایل |

---

## 📦 پروتکل‌های پشتیبانی‌شده

### 💾 برنامه‌ریزی (Programming)

| پروتکل | خانواده | فایل | وضعیت |
|--------|---------|------|:---:|
| **ISP** | AVR (ATmega, ATtiny) | `protocol_isp.c` | ✅ |
| **ICSP** | PIC (10F-33F) | `protocol_icsp.c` | ✅ |
| **SWD** | ARM Cortex-M | `protocol_swd.c` | ✅ |
| **JTAG** | ARM, FPGA | `protocol_jtag.c` | ✅ |
| **SWIM** | STM8 | `protocol_swim.c` | ✅ |
| **BDM** | NXP S12 | `protocol_bdm.c` | ✅ |
| **DAP** | CMSIS-DAP | `protocol_dap.c` | ✅ |
| **CC-DBG** | TI CC25xx | `protocol_cc.c` | ✅ |
| **Holtek ISP** | HT46/HT66/HT68 | `protocol_holtek.c` | ✅ |

### 🔌 ارتباطی (Communication)

| پروتکل | کاربرد | فایل | وضعیت |
|--------|--------|------|:---:|
| **UART** | Serial Terminal | `protocol_uart.c` | ✅ |
| **RS485** | Industrial | `protocol_rs485.c` | ✅ |
| **SPI** | Flash/EEPROM | `protocol_spi.c` | ✅ |
| **I2C** | EEPROM/Sensors | `protocol_i2c.c` | ✅ |
| **1-Wire** | Dallas | `protocol_1wire.c` | ✅ |
| **IR** | Infrared | `protocol_ir.c` | ✅ |

### 🚗 خودرو (Automotive)

| پروتکل | کاربرد | فایل | وضعیت |
|--------|--------|------|:---:|
| **OBD-II ELM327** | AT Commands | `protocol_obd.c` | ✅ |
| **OBD-II K-Line** | ISO 9141 | `protocol_obd.c` | ✅ |
| **CAN Bus** | CAN 2.0A/B | `protocol_can.c` | ✅ |
| **K-Line Raw** | ISO 9141 | `protocol_kline.c` | ✅ |
| **CANopen** | صنعتی | `protocol_can.c` | ✅ |
| **J1939** | کامیون | `protocol_can.c` | ✅ |

### 🏢 اتوماسیون ساختمان

| پروتکل | کاربرد | فایل | وضعیت |
|--------|--------|------|:---:|
| **KNX** | TP-UART | `protocol_knx.c` | ✅ |
| **DALI** | نور | `protocol_dali.c` | ✅ |
| **BACnet** | MS/TP | `protocol_bacnet.c` | ✅ |
| **Modbus** | RTU/TCP | `protocol_modbus.c` | ✅ |

### 🏠 خانه هوشمند

| پروتکل | کاربرد | فایل | وضعیت |
|--------|--------|------|:---:|
| **Zigbee** | CC2530 | `protocol_zigbee.c` | ✅ |
| **Z-Wave** | Plus | `protocol_zwave.c` | ✅ |
| **MQTT** | Broker/Client | `protocol_mqtt.c` | ✅ |

### 🏭 صنعتی

| پروتکل | کاربرد | فایل | وضعیت |
|--------|--------|------|:---:|
| **Profibus** | DP/PA | `protocol_profibus.c` | ✅ |
| **DeviceNet** | CAN | `protocol_can.c` | ✅ |
| **EtherCAT** | Master/Slave | `protocol_ethercat.c` | ✅ |
| **Profinet** | IO | `protocol_profinet.c` | ✅ |

### 🔥 اعلام حریق

| پروتکل | کاربرد | فایل | وضعیت |
|--------|--------|------|:---:|
| **Notifier** | NFS | `protocol_notifier.c` | ✅ |
| **Honeywell** | IFP | `protocol_honeywell.c` | ✅ |
| **Siemens** | Cerberus | `protocol_siemens.c` | ✅ |
| **Bosch** | 7000 | `protocol_bosch.c` | ✅ |
| **Securiton** | AlgoRex | `protocol_securiton.c` | ✅ |

### 📱 سیم‌کارت

| حالت | کاربرد | فایل | وضعیت |
|------|--------|------|:---:|
| **Reader** | خواندن SIM | `protocol_sim.c` | ✅ |
| **Emulator** | شبیه‌سازی SIM | `protocol_sim.c` | ✅ |

### 📡 بی‌سیم

| پروتکل | کاربرد | فایل | وضعیت |
|--------|--------|------|:---:|
| **nRF24** | nRF24L01+ | `protocol_nrf24.c` | ✅ |
| **CC1101** | Sub-GHz | `protocol_cc1101.c` | ✅ |
| **RFID** | 125kHz/13.56MHz | `protocol_rfid.c` | ✅ |

### 🎛️ FPGA

| پروتکل | کاربرد | فایل | وضعیت |
|--------|--------|------|:---:|
| **XVC** | Xilinx Vivado | `protocol_xvc.c` | ✅ |
| **JTAG** | Altera/Lattice | `protocol_jtag.c` | ✅ |

---

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

```bash
# ESP-IDF v5.1+
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf && ./install.sh && source export.sh

# esptool
pip install esptool pyserial
```

### فلش کردن

```bash
# کلون پروژه
git clone https://github.com/hadipic/l-programmer.git
cd l-programmer

# بیلد
idf.py build

# فلش
idf.py -p /dev/ttyUSB0 flash monitor
```

### اتصال

```
حالت Access Point:
  SSID: L-Programmer
  Password: 12345678
  IP: 192.168.4.1

حالت Station (اتصال به WiFi خانه):
  SSID: Shop-electronic
  IP: 192.168.1.17
```

---

## 📡 API Reference

### HTTP API

| Method | Endpoint | توضیح |
|--------|----------|--------|
| GET | `/api/status` | وضعیت دستگاه |
| GET | `/api/protocols` | لیست پروتکل‌ها |
| GET | `/api/capabilities` | قابلیت‌ها |
| POST | `/api/config` | تنظیم پروتکل |
| POST | `/api/connect` | اتصال |
| POST | `/api/disconnect` | قطع اتصال |
| POST | `/api/detect` | تشخیص خودکار |
| POST | `/api/read` | خواندن حافظه |
| POST | `/api/program` | نوشتن حافظه |
| POST | `/api/erase` | پاک کردن |
| POST | `/api/verify` | تأیید |
| POST | `/api/vpp` | تنظیم VPP |

### WebSocket

```
ws://IP:8080/terminal       → ترمینال عمومی (JSON)
ws://IP:8080/uart/terminal  → داده خام UART
ws://IP:8080/spi/monitor    → داده خام SPI
ws://IP:8080/i2c/monitor    → داده خام I2C
ws://IP:8080/can/monitor    → داده خام CAN
ws://IP:8080/swd/debug      → دیباگ SWD
ws://IP:8080/openocd        → OpenOCD Bridge
ws://IP:8080/xvc            → Xilinx Vivado
```

---

## 📊 پین‌بندی

### کانکتور 10 پین

| پین | سیگنال | GPIO |
|-----|--------|------|
| 1 | RESET | GPIO5 |
| 2 | VCC | 3.3V/5V |
| 3 | GND | GND |
| 4 | SWIM/SWDIO | GPIO18 |
| 5 | SWCLK/PGC | GPIO19 |
| 6 | PGD | GPIO23 |
| 7 | SCK | GPIO14 |
| 8 | MISO | GPIO12 |
| 9 | MOSI | GPIO13 |
| 10 | VPP | GPIO16 |

---

## 🏗️ معماری

```
┌─────────────────────────────────────────┐
│              Web Browser               │
│  ┌─────────────────────────────────┐   │
│  │  SPA (HTML/CSS/JS)             │   │
│  │  • Hex Editor                  │   │
│  │  • Fuse Config                 │   │
│  │  • Terminal                    │   │
│  │  • Debugger                    │   │
│  │  • Pinout Guide                │   │
│  └────────────┬────────────────────┘   │
│               │ HTTP/WebSocket         │
└───────────────┼─────────────────────────┘
                │
┌───────────────┼─────────────────────────┐
│               ▼                         │
│           ESP32                         │
│  ┌─────────────────────────────────┐   │
│  │  Web Server (Mongoose)         │   │
│  │  • HTTP API                    │   │
│  │  • WebSocket Server            │   │
│  └────────────┬────────────────────┘   │
│  ┌────────────▼────────────────────┐   │
│  │  Protocol Layer                │   │
│  │  • ISP, ICSP, SWD, JTAG      │   │
│  │  • UART, SPI, I2C, CAN       │   │
│  │  • KNX, DALI, Modbus         │   │
│  │  • SIM, RFID, IR             │   │
│  └────────────┬────────────────────┘   │
│  ┌────────────▼────────────────────┐   │
│  │  GPIO Bit-Banging              │   │
│  │  • Fast GPIO                   │   │
│  │  • Level Shifter               │   │
│  │  • VPP Boost                   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 🔧 ساختار پروژه

```
l-programmer/
├── main/
│   ├── main.c
│   ├── protocol.c
│   ├── protocol_uart.c
│   ├── protocol_spi.c
│   ├── protocol_i2c.c
│   ├── protocol_can.c
│   ├── protocol_swd.c
│   ├── protocol_jtag.c
│   ├── protocol_swim.c
│   ├── protocol_isp.c
│   ├── protocol_icsp.c
│   ├── protocol_knx.c
│   ├── protocol_sim.c
│   ├── protocol_obd.c
│   └── protocol_websocket.c
├── frontend/
│   ├── index.html
│   ├── main.js
│   ├── style.css
│   ├── i18n.js
│   ├── pages/
│   │   ├── home.js
│   │   ├── devices.js
│   │   ├── hexEditor.js
│   │   ├── fuseConfig.js
│   │   ├── terminal.js
│   │   ├── debugger.js
│   │   └── pinout.js
│   ├── device-registry/
│   │   ├── index.js
│   │   ├── families/
│   │   ├── protocols/
│   │   └── fuse-data/
│   └── utils/
└── docs/
    ├── API.md
    ├── PROTOCOLS.md
    ├── SWIM.md
    ├── UART.md
    └── PINOUT.md
```

---

## 🤝 مشارکت

پروژه متن‌باز است و از مشارکت شما استقبال می‌کنیم:

1. Fork کنید
2. Branch بسازید
3. تغییرات را اعمال کنید
4. Pull Request بفرستید

---

## 👥 شبکه‌های اجتماعی و ارتباطی

### 💬 تلگرام

| نوع | نام | لینک |
|-----|-----|------|
| گروه | **ESP32 Community** | [t.me/+oi9QrKR1qdozZTc0](https://t.me/+oi9QrKR1qdozZTc0) |
| گروه | **Embedded & Qt** | [t.me/Embedded_Qt](https://t.me/Embedded_Qt) |
| کانال | **ESP32 EVM** | [t.me/esp32_evm](https://t.me/esp32_evm) |
| ربات | **Shop Electronic** | [@shop_electronic_bot](https://t.me/shop_electronic_bot) |

### 🌐 وب‌سایت‌ها

| نوع | نام | لینک |
|-----|-----|------|
| فروشگاه | **Shop Electronic** | [shop-electronic.ir](https://shop-electronic.ir) |
| گیت‌هاب | **hadipic** | [github.com/hadipic](https://github.com/hadipic) |

---

## 📄 مجوز

MIT License - استفاده آزاد با ذکر منبع

---

## 🙏 تقدیر

- **ESP-IDF** - فریم‌ورک اصلی
- **Mongoose** - وب‌سرور
- **CMSIS-DAP** - پروتکل دیباگ ARM
- **STM8 SWIM** - پروتکل STM8
- **Community** - همه دوستان در گروه‌های تلگرام

---

**L-Programmer: یک ابزار، همه پروتکل‌ها، همه دستگاه‌ها!** 🚀
```
