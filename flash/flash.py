#!/usr/bin/env python3
# ============================================================
#  flash.py - اسکریپت فلش کامل LProgrammer
#  رفع مشکل: استفاده از esptool.py مستقیم یا python -m esptool
# ============================================================

import subprocess
import sys
import os
import csv
import io
import shutil

# ============================================================
#  📁 مسیرها
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FIRMWARE_DIR = os.path.join(SCRIPT_DIR, "..", "firmware")

# ============================================================
#  📋 پارتیشن‌بندی از CSV
# ============================================================
PARTITION_CSV = """# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x6000,
phy_init, data, phy,     0xf000,  0x1000,
factory,  app,  factory, 0x10000, 0x2A0000,
www,      data, spiffs,  ,        0x100000,
"""

# ============================================================
#  📦 فایل‌ها و آدرس‌ها
# ============================================================
FILES = [
    (0x1000, "bootloader.bin"),
    (0x8000, "partition-table.bin"),
    (0x10000, "l-programmer.bin"),
]

def get_www_offset():
    """پیدا کردن آدرس www از پارتیشن CSV"""
    # محاسبه:
    # nvs: 0x9000 + 0x6000 = 0xF000
    # phy_init: 0xF000 + 0x1000 = 0x10000
    # factory: 0x10000 + 0x2A0000 = 0x2B0000
    # www: 0x2B0000
    return 0x2B0000

WWW_ADDR = get_www_offset()

# ============================================================
#  🔍 پیدا کردن esptool
# ============================================================
def find_esptool():
    """پیدا کردن esptool"""
    
    # 1. تلاش: esptool.py
    if shutil.which("esptool.py"):
        return "esptool.py"
    
    # 2. تلاش: python -m esptool
    try:
        result = subprocess.run(["python3", "-m", "esptool", "--version"], 
                                capture_output=True, text=True)
        if result.returncode == 0:
            return ["python3", "-m", "esptool"]
    except:
        pass
    
    try:
        result = subprocess.run(["python", "-m", "esptool", "--version"], 
                                capture_output=True, text=True)
        if result.returncode == 0:
            return ["python", "-m", "esptool"]
    except:
        pass
    
    # 3. تلاش: مسیر ESP-IDF
    esp_idf_path = os.path.expanduser("~/.espressif/python_env/idf5.1_py3.8_env/bin/esptool.py")
    if os.path.exists(esp_idf_path):
        return esp_idf_path
    
    # 4. تلاش: pip show
    try:
        result = subprocess.run(["pip", "show", "esptool"], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith("Location:"):
                    location = line.split(":", 1)[1].strip()
                    esptool_path = os.path.join(location, "esptool.py")
                    if os.path.exists(esptool_path):
                        return esptool_path
    except:
        pass
    
    return None

# ============================================================
#  🔍 پیدا کردن پورت
# ============================================================
def find_port():
    """پیدا کردن پورت ESP32"""
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if any(x in port.description for x in ["CP210", "CH340", "USB", "UART", "Serial"]):
                return port.device
    except ImportError:
        pass
    return None

# ============================================================
#  📋 نمایش پارتیشن‌ها
# ============================================================
def show_partitions():
    print("📋 پارتیشن‌بندی:")
    print("-" * 60)
    reader = csv.reader(io.StringIO(PARTITION_CSV))
    for row in reader:
        if row and len(row) >= 5 and not row[0].startswith("#"):
            name = row[0].strip()
            type_ = row[1].strip()
            subtype = row[2].strip()
            offset = row[3].strip() or "auto"
            size = row[4].strip() or "auto"
            print(f"  {name:12s} | {type_:6s} | {subtype:8s} | {offset:10s} | {size}")
    print("-" * 60)

# ============================================================
#  🔧 فلش کردن
# ============================================================
def flash(port=None, baud=460800, erase_first=False):
    """فلش کردن ESP32"""
    
    # نمایش پارتیشن‌ها
    show_partitions()
    
    # پیدا کردن پورت
    if not port:
        port = find_port()
    
    if not port:
        print("❌ پورت پیدا نشد!")
        print("استفاده: python flash.py COM3")
        print("یا: python flash.py /dev/ttyUSB0")
        return False
    
    print(f"\n🔧 فلش کردن روی {port}...")
    
    # ✅ پیدا کردن esptool
    esptool = find_esptool()
    
    if not esptool:
        print("❌ esptool پیدا نشد!")
        print("نصب: pip install esptool")
        print("یا: source ~/.espressif/python_env/idf5.1_py3.8_env/bin/activate")
        return False
    
    print(f"✅ esptool: {esptool}")
    
    # پاک کردن فلش (اختیاری)
    if erase_first:
        print("🗑️ پاک کردن فلش...")
        if isinstance(esptool, list):
            cmd_erase = esptool + ["--port", port, "erase_flash"]
        else:
            cmd_erase = [esptool, "--port", port, "erase_flash"]
        subprocess.run(cmd_erase)
    
    # ساخت دستور فلش
    if isinstance(esptool, list):
        cmd = esptool + ["--port", port, "--baud", str(baud), "write_flash"]
    else:
        cmd = [esptool, "--port", port, "--baud", str(baud), "write_flash"]
    
    # اضافه کردن فایل‌ها
    for addr, fname in FILES:
        fpath = os.path.join(FIRMWARE_DIR, fname)
        if not os.path.exists(fpath):
            print(f"❌ فایل {fname} پیدا نشد!")
            print(f"   مسیر: {fpath}")
            return False
        print(f"  📦 {fname} → 0x{addr:X}")
        cmd.extend([hex(addr), fpath])
    
    # www.bin
    www_path = os.path.join(FIRMWARE_DIR, "www.bin")
    if os.path.exists(www_path):
        print(f"  📦 www.bin → 0x{WWW_ADDR:X}")
        cmd.extend([hex(WWW_ADDR), www_path])
    else:
        print("  ⚠️ www.bin پیدا نشد - رد شدن")
    
    # نمایش دستور
    print(f"\n📝 دستور:")
    print(f"  {' '.join(cmd)}")
    print()
    
    # اجرا
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ فلش موفق!")
        print("🔄 ESP32 را ریست کنید (دکمه EN)")
        return True
    else:
        print("\n❌ فلش ناموفق!")
        print("راه‌حل‌ها:")
        print("  1. پورت را چک کنید")
        print("  2. ESP32 را در حالت فلش بگذارید (دکمه BOOT را نگه دارید + EN)")
        print("  3. کابل USB را چک کنید")
        return False

# ============================================================
#  📖 راهنما
# ============================================================
def show_help():
    print("""
🔧 LProgrammer Flasher

استفاده:
  python flash.py [پورت] [گزینه‌ها]

گزینه‌ها:
  --erase     پاک کردن فلش قبل از فلش
  --help      نمایش راهنما

مثال:
  python flash.py COM3
  python flash.py /dev/ttyUSB0 --erase
""")

# ============================================================
#  🚀 اجرا
# ============================================================
if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        sys.exit(0)
    
    erase = "--erase" in sys.argv
    port = None
    
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            port = arg
    
    flash(port, erase_first=erase)
