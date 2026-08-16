# L-Programmer: Universal Wireless Programmer & Debugger

**L-Programmer** is an open-source project to build a **universal, wireless, web-based programmer and debugger** using the **ESP32** module. It aims to replace a wide range of specialized tools like ST-Link, J-Link, USBasp, CH341A, and many more.

---

## 🚀 Key Features

- **✅ One Tool for Everything**: Program, debug, and communicate with a wide range of microcontrollers, memories, modules, and FPGAs.
- **🌐 Fully Wireless**: Connect via **WiFi** and manage your projects without any physical cables.
- **🖥️ Web-Based UI**: A modern, responsive **Single-Page Application (SPA)** that runs in your browser. **No software installation required** on your computer or smartphone.
- **🔌 Supports Multiple Protocols**:
    - **Programming**: ISP (AVR), ICSP (PIC), SWD (ARM), JTAG (ARM/FPGA), SWIM (STM8), Holtek ISP, CC-DBG (TI), BDM (NXP)
    - **Communication**: UART, RS485, I2C, SPI, CAN, 1-Wire, Modbus, DALI, KNX
    - **Automotive**: OBD-II (K-Line, CAN, VPW, PWM)
    - **Memories**: SPI Flash, I2C EEPROM, MicroWire
- **📱 Compatible with Standard Tools**:
    - **OpenOCD**: For professional ARM debugging
    - **GDB**: For command-line debugging
    - **Vivado**: For Xilinx FPGA programming
    - **ELM327 Emulator**: For OBD-II software (e.g., Torque)
- **💰 Very Low Cost**: Using a standard ESP32 board and simple components, you can build this powerful tool for a fraction of the cost of commercial tools.
- **💡 Open Source & Extensible**: All code (Firmware & Frontend) is released under the **Apache 2.0** license, and you can easily add new protocols.

---

## 🧰 Supported Devices (900+)

| Family | Number of Devices | Examples |
|:-------|:------------------|:---------|
| **ARM Cortex-M** (STM32, nRF52, LPC, SAM) | 900+ | STM32F103, nRF52840, LPC1768 |
| **AVR** (Atmel) | 188 | ATmega328P, ATtiny85 |
| **PIC** (Microchip) | 234 | PIC16F877A, PIC18F2550 |
| **STM8** | 144 | STM8S003F3 |
| **ESP32** | 12 | ESP32, ESP32-S3, ESP32-C3 |
| **Holtek** | 136 | HT66F, HT46R |
| **FPGA** | All | Xilinx (Vivado), Altera (Quartus), Lattice (Diamond) |
| **TI Wireless** | 22 | CC2530, CC2540, CC2650 |

---

## 📊 Architecture Overview

The project uses a layered architecture for maximum flexibility and extensibility.
