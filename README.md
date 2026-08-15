```markdown
# 📖 README کامل L-Programmer

## 🔧 L-Programmer - پروگرمر و دیباگر جهانی، بی‌سیم و مبتنی بر وب

**نسخه:** 1.0.0  
**تاریخ:** 2026  
**مجوز:** MIT

---

## 🎯 معرفی

L-Programmer یک ابزار **متن‌باز** و **حرفه‌ای** برای برنامه‌ریزی و دیباگ طیف گسترده‌ای از میکروکنترلرها، حافظه‌ها و FPGA ها است. این پروژه با استفاده از **ESP32** و رابط کاربری **وب‌محور**، جایگزین ابزارهای تخصصی متعددی می‌شود:

| ابزار سنتی | جایگزین با L-Programmer |
|-------------|------------------------|
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
| BDM Debugger | ✅ BDM (NXP) |

---

## ✨ ویژگی‌ها

### سخت‌افزار
- ESP32 با WiFi داخلی
- 20+ پین GPIO با Level Shifter
- VPP قابل تنظیم (12V برای PIC)
- کانکتور 10 پین استاندارد
- تغذیه هدف (3.3V/5V)
- ADC برای سنجش ولتاژ/جریان
- DAC برای تولید سیگنال

### نرم‌افزار
- **وب‌سرور** - بدون نیاز به نصب نرم‌افزار
- **WebSocket** - ارتباط Real-time
- **REST API** - 11+ endpoint
- **i18n** - فارسی، انگلیسی، عربی
- **Hex Editor** - ویرایش آنلاین
- **Fuse Config** - فیوزبیت‌ها
- **Terminal** - ترمینال چندمنظوره
- **Debugger** - دیباگ ARM از طریق OpenOCD
- **Script Engine** - اجرای دستورات متوالی

---

## 📦 پروتکل‌های پشتیبانی‌شده

### 💾 برنامه‌ریزی (Programming)

| پروتکل | خانواده | فایل |
|--------|---------|------|
| **ISP** | AVR (ATmega, ATtiny) | `protocol_isp.c` |
| **ICSP** | PIC (10F-33F) | `protocol_icsp.c` |
| **SWD** | ARM Cortex-M | `protocol_swd.c` |
| **JTAG** | ARM, FPGA | `protocol_jtag.c` |
| **SWIM** | STM8 | `protocol_swim.c` |
| **BDM** | NXP S12 | `protocol_bdm.c` |
| **DAP** | CMSIS-DAP | `protocol_dap.c` |
| **CC-DBG** | TI CC25xx | `protocol_cc.c` |
| **Holtek ISP** | HT46/HT66/HT68 | `protocol_holtek.c` |

### 🔌 ارتباطی (Communication)

| پروتکل | کاربرد | فایل |
|--------|--------|------|
| **UART** | Serial Terminal | `protocol_uart.c` |
| **RS485** | Industrial | `protocol_rs485.c` |
| **SPI** | Flash/EEPROM | `protocol_spi.c` |
| **I2C** | EEPROM/Sensors | `protocol_i2c.c` |
| **1-Wire** | Dallas | `protocol_1wire.c` |
| **IR** | Infrared | `protocol_ir.c` |

### 🚗 خودرو (Automotive)

| پروتکل | کاربرد | فایل |
|--------|--------|------|
| **OBD-II** | ELM327/K-Line | `protocol_obd.c` |
| **CAN Bus** | CAN 2.0A/B | `protocol_can.c` |
| **K-Line** | ISO 9141 | `protocol_kline.c` |
| **CANopen** | صنعتی | `protocol_can.c` |
| **J1939** | کامیون | `protocol_can.c` |

### 🏢 اتوماسیون ساختمان

| پروتکل | کاربرد | فایل |
|--------|--------|------|
| **KNX** | TP-UART | `protocol_knx.c` |
| **DALI** | نور | `protocol_dali.c` |
| **BACnet** | MS/TP | `protocol_bacnet.c` |
| **Modbus** | RTU/TCP | `protocol_modbus.c` |

### 🏠 خانه هوشمند

| پروتکل | کاربرد | فایل |
|--------|--------|------|
| **Zigbee** | CC2530 | `protocol_zigbee.c` |
| **Z-Wave** | Plus | `protocol_zwave.c` |
| **MQTT** | Broker/Client | `protocol_mqtt.c` |

### 🏭 صنعتی

| پروتکل | کاربرد | فایل |
|--------|--------|------|
| **Profibus** | DP/PA | `protocol_profibus.c` |
| **DeviceNet** | CAN | `protocol_can.c` |
| **EtherCAT** | Master/Slave | `protocol_ethercat.c` |
| **Profinet** | IO | `protocol_profinet.c` |

### 🔥 اعلام حریق

| پروتکل | کاربرد | فایل |
|--------|--------|------|
| **Notifier** | NFS | `protocol_notifier.c` |
| **Honeywell** | IFP | `protocol_honeywell.c` |
| **Siemens** | Cerberus | `protocol_siemens.c` |
| **Bosch** | 7000 | `protocol_bosch.c` |
| **Securiton** | AlgoRex | `protocol_securiton.c` |

### 📱 سیم‌کارت

| حالت | کاربرد | فایل |
|------|--------|------|
| **Reader** | خواندن SIM | `protocol_sim.c` |
| **Emulator** | شبیه‌سازی SIM | `protocol_sim.c` |

### 📡 بی‌سیم

| پروتکل | کاربرد | فایل |
|--------|--------|------|
| **nRF24** | nRF24L01+ | `protocol_nrf24.c` |
| **CC1101** | Sub-GHz | `protocol_cc1101.c` |
| **RFID** | 125kHz/13.56MHz | `protocol_rfid.c` |

### 🎛️ FPGA

| پروتکل | کاربرد | فایل |
|--------|--------|------|
| **XVC** | Xilinx Vivado | `protocol_xvc.c` |
| **JTAG** | Altera/Lattice | `protocol_jtag.c` |

---

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

```bash
# ESP-IDF v5.1+
pip install esptool
pip install pyserial
```

### فلش کردن

```bash
# کلون پروژه
git clone https://github.com/yourusername/l-programmer.git
cd l-programmer

# بیلد
idf.py build

# فلش
idf.py -p /dev/ttyUSB0 flash monitor
```

### اتصال

```
SSID: L-Programmer
Password: 12345678
IP: 192.168.4.1
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
ws://IP:8080/terminal       → ترمینال عمومی
ws://IP:8080/UART           → داده خام UART
ws://IP:8080/SPI            → داده خام SPI
ws://IP:8080/I2C            → داده خام I2C
ws://IP:8080/CAN            → داده خام CAN
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

## 🔧 ساخت و توسعه

### ساختار پروژه

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

## 📄 مجوز

MIT License - استفاده آزاد با ذکر منبع

---

## 🙏 تقدیر

- **ESP-IDF** - فریم‌ورک اصلی
- **Mongoose** - وب‌سرور
- **CMSIS-DAP** - پروتکل دیباگ ARM
- **STM8 SWIM** - پروتکل STM8

---

**L-Programmer: یک ابزار، همه پروتکل‌ها، همه دستگاه‌ها!** 🚀
```

حالا README کامل و حرفه‌ای داری! این فایل را در پوشه `lprogrammer-firmware/` قرار بده و گیت کن:

```bash
cd ~/project/programer/lprogrammer-firmware
cat > README.md << 'EOF'
# ... محتوای بالا ...
EOF

git add README.md
git commit -m "docs: README کامل با تمام پروتکل‌ها، API و معماری"
```
