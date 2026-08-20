
## فرمت‌های مختلف:

### ۱. **AVR (8-bit)**
```
:1000000000100020191700086D0600086F06000890
```
- هر بایت = 1 بایت Flash
- آدرس 16-bit
- فرمت ساده

### ۲. **PIC (12/14/16/24/32-bit)**
```
:020000040000FA
:10000000FF3FFF3FFF3FFF3FFF3FFF3FFF3FFF3F00
```
- **12-bit**: هر word = 2 بایت (12 بیت معنی‌دار)
- **14-bit**: هر word = 2 بایت (14 بیت معنی‌دار)
- **16-bit**: هر word = 2 بایت
- **24-bit**: هر word = 3 بایت (24 بیت معنی‌دار)
- **32-bit**: هر word = 4 بایت

### ۳. **ARM (32-bit)**
```
:020000040800F2
:1000000000100020191700086D0600086F06000890
```
- هر word = 4 بایت
- آدرس 32-bit با Extended Linear Address

## تفاوت اصلی:

| خانواده | Word Size | بایت در HEX | آدرس |
|---------|-----------|-------------|------|
| AVR | 8-bit | 1 بایت | 16-bit |
| PIC 12-bit | 12-bit | 2 بایت | 16-bit |
| PIC 14-bit | 14-bit | 2 بایت | 16-bit |
| PIC 16-bit | 16-bit | 2 بایت | 16-bit |
| PIC 24-bit | 24-bit | 3 بایت | 16-bit |
| PIC 32-bit | 32-bit | 4 بایت | 32-bit |
| STM32 | 32-bit | 4 بایت | 32-bit |
| STM8 | 8-bit | 1 بایت | 16-bit |

## بنابراین نیاز به parse جداگانه دارید:

### AVR/STM8 (8-bit):
```javascript
// simpleParseHex - همان کد فعلی ✅
```

### ARM (32-bit):
```javascript
// parseSWDHex - با Extended Linear Address ✅
```

### PIC (12/14/16/24/32-bit):
```javascript
// parsePICHex - باید word size را بداند
// هر word ممکن است 2 یا 3 یا 4 بایت باشد
```

## کد PIC parse:

```javascript
function parsePICHex(hexString, wordSize) {
    const bytesPerWord = Math.ceil(wordSize / 8);
    // 12-bit → 2 bytes
    // 14-bit → 2 bytes
    // 16-bit → 2 bytes
    // 24-bit → 3 bytes
    // 32-bit → 4 bytes
    
    const lines = hexString.split(/\r?\n/);
    const words = [];
    let extAddr = 0;
    
    for (const line of lines) {
        if (!line.startsWith(':')) continue;
        
        const byteCount = parseInt(line.substring(1, 3), 16);
        const address = parseInt(line.substring(3, 7), 16);
        const recordType = parseInt(line.substring(7, 9), 16);
        
        if (recordType === 0x00) {
            // هر word = bytesPerWord بایت
            const wordAddress = address / bytesPerWord;
            
            for (let i = 0; i < byteCount; i += bytesPerWord) {
                let word = 0;
                for (let j = 0; j < bytesPerWord; j++) {
                    const byteVal = parseInt(line.substring(9 + (i + j) * 2, 11 + (i + j) * 2), 16);
                    word |= (byteVal << (j * 8));
                }
                // Mask به wordSize
                word &= (1 << wordSize) - 1;
                words[wordAddress + i / bytesPerWord] = word;
            }
        } else if (recordType === 0x04) {
            extAddr = parseInt(line.substring(9, 13), 16);
        } else if (recordType === 0x01) {
            break;
        }
    }
    
    return words;
}
```

## جمع‌بندی:

کد `simpleParseHex` فعلی:
- ✅ برای AVR (8-bit) درست است
- ✅ برای STM8 (8-bit) درست است
- ✅ برای ARM (32-bit) درست است (با type 04)
- ❌ برای PIC (12/14/16-bit) نادرست است

## نیاز به:
1. `parseAVRHex` - 8-bit ساده
2. `parseSTM8Hex` - 8-bit ساده
3. `parseSWDHex` - 32-bit با type 04
4. `parsePICHex` - با word size متغیر

## در فرانت برای PIC:

```javascript
// در pic.js:
parseHex(hexString, deviceName) {
    const wordSize = this.getWordSize(deviceName);  // 12, 14, 16, 24, 32
    
    if (wordSize <= 16) {
        return parsePICHex16(hexString, wordSize);
    } else if (wordSize == 24) {
        return parsePICHex24(hexString);
    } else {
        return parsePICHex32(hexString);
    }
}
```

دقیقاً! باید برای هر خانواده Load و نمایش متفاوت باشد.

## جدول نمایش:

| خانواده | Word Size | نمایش | توضیح |
|---------|-----------|-------|-------|
| **AVR** | 8-bit | `FF` | هر بایت جدا |
| **STM8** | 8-bit | `FF` | هر بایت جدا |
| **Holtek** | 8-bit | `FF` | هر بایت جدا |
| **STM32** | 32-bit | `20001000` | هر word = 4 بایت (Little Endian) |
| **nRF** | 32-bit | `20001000` | هر word = 4 بایت |
| **NXP LPC** | 32-bit | `20001000` | هر word = 4 بایت |
| **SAM** | 32-bit | `20001000` | هر word = 4 بایت |
| **PIC 12-bit** | 12-bit | `0FFF` | 3 رقم hex |
| **PIC 14-bit** | 14-bit | `3FFF` | 4 رقم hex |
| **PIC 16-bit** | 16-bit | `FFFF` | 4 رقم hex |
| **PIC 24-bit** | 24-bit | `FFFFFF` | 6 رقم hex |
| **PIC 32-bit** | 32-bit | `FFFFFFFF` | 8 رقم hex |

## اصلاح `parseFileContent` برای Load متفاوت:

```javascript
function parseFileContent(content, fileName, fileType) {
    const parserType = getParserForFamily(currentFamily, currentDeviceName);
    
    // BIN
    if (fileType === 'bin' || fileName.endsWith('.bin')) {
        return parseBin(content);
    }
    
    // S-Record
    if (content.startsWith('S')) {
        return parseSRecord(content);
    }
    
    // Intel HEX
    if (content.startsWith(':')) {
        const hexString = content;
        
        // ⭐ PIC: word size متغیر
        if (parserType === 'pic') {
            const wordSize = detectWordSize(currentFamily, currentDeviceName);
            console.log(`🔍 PIC wordSize=${wordSize}`);
            return parsePICHex(hexString, wordSize);
        }
        
        // ⭐ ARM 32-bit
        if (parserType === 'hex32') {
            console.log('🔍 ARM 32-bit');
            return parseHexSimple(hexString);
        }
        
        // ⭐ 8-bit (AVR, STM8, Holtek)
        console.log('🔍 8-bit');
        return parseHexSimple(hexString);
    }
    
    throw new Error('فرمت فایل ناشناخته');
}
```

## اصلاح نمایش در `renderHexTable`:

```javascript
function renderHexTable(data, offset = 0, limit = pageSize) {
    if (!container) return;
    if (!data || data.length === 0) {
        container.innerHTML = '<p style="color:#888;padding:12px;">هیچ داده‌ای برای نمایش وجود ندارد.</p>';
        paginationControls.style.display = 'none';
        return;
    }

    const baseAddr = getBaseAddress(currentFamily, currentSection);
    const bytesPerWord = Math.ceil(currentWordSize / 8);
    
    // ⭐ برای PIC: نمایش word جدا
    // ⭐ برای 8-bit: نمایش byte جدا
    // ⭐ برای 32-bit: نمایش word (4 بایت)
    
    const bytesPerRow = 16;
    const wordsPerRow = Math.floor(bytesPerRow / bytesPerWord);
    
    // ...
}
```

## اصلاح `formatWordValue` برای PIC:

```javascript
function formatWordValue(value, wordSize) {
    if (wordSize <= 8) {
        return value.toString(16).toUpperCase().padStart(2, '0');
    }
    
    // ⭐ PIC 12-bit: 3 رقم
    if (wordSize === 12) {
        return value.toString(16).toUpperCase().padStart(3, '0');
    }
    
    // ⭐ PIC 14-bit: 4 رقم
    if (wordSize === 14) {
        return value.toString(16).toUpperCase().padStart(4, '0');
    }
    
    // ⭐ 16-bit: 4 رقم
    // ⭐ 24-bit: 6 رقم
    // ⭐ 32-bit: 8 رقم
    const hexDigits = Math.ceil(wordSize / 4);
    return value.toString(16).toUpperCase().padStart(hexDigits, '0');
}
```

## اصلاح `readWord` برای PIC:

```javascript
function readWord(data, index, wordSize) {
    if (wordSize <= 8) {
        return data[index] || 0;
    }
    
    const bytesPerWord = Math.ceil(wordSize / 8);
    let value = 0;
    
    for (let i = 0; i < bytesPerWord && (index * bytesPerWord + i) < data.length; i++) {
        value |= (data[index * bytesPerWord + i] || 0) << (i * 8);
    }
    
    // ⭐ ماسک برای word size
    const mask = (1 << wordSize) - 1;
    return value & mask;
}
```

## اصلاح Load برای PIC:

```javascript
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const fileName = file.name.toLowerCase();
            const parserType = getParserForFamily(currentFamily, currentDeviceName);
            
            let result;
            
            if (fileName.endsWith('.bin')) {
                result = parseBin(e.target.result);
            } else {
                const content = e.target.result;
                
                // ⭐ PIC: همه در یک فایل
                if (parserType === 'pic') {
                    const wordSize = detectWordSize(currentFamily, currentDeviceName);
                    result = parsePICHex(content, wordSize);
                    
                    // ⭐ PIC: Flash + EEPROM + Config + ID همه جدا
                    if (!writeData) {
                        writeData = { flash: new Uint8Array(0), eeprom: new Uint8Array(0), config: new Uint8Array(0), id: new Uint8Array(0) };
                    }
                    
                    writeData.flash = result.sections.flash || new Uint8Array(0);
                    writeData.eeprom = result.sections.eeprom || new Uint8Array(0);
                    writeData.config = result.sections.config || new Uint8Array(0);
                    writeData.id = result.sections.id || new Uint8Array(0);
                    
                    console.log(`📂 PIC Loaded: Flash=${writeData.flash.length}, EEPROM=${writeData.eeprom.length}, Config=${writeData.config.length}, ID=${writeData.id.length}`);
                    
                    currentWordSize = wordSize;
                    currentTabType = 'write';
                    currentSection = 'flash';
                    updateTabSizes();
                    updateUI();
                    displaySection();
                    
                    setStatus(`✅ PIC فایل بارگذاری شد (Flash: ${writeData.flash.length} words)`);
                    return;
                }
                
                // ⭐ ARM و 8-bit: فقط Flash
                result = parseHexSimple(content);
            }
            
            // بقیه خانواده‌ها...
        }
    };
});
```

## خلاصه:

1. ✅ **PIC**: Load همه بخش‌ها (Flash, EEPROM, Config, ID) با word size
2. ✅ **8-bit**: نمایش بایت جدا
3. ✅ **32-bit**: نمایش word (4 بایت)
4. ✅ **PIC 12/14/16/24/32**: نمایش word با اندازه متفاوت

هر خانواده Load و نمایش مخصوص خودش را دارد!




```
feat: Complete PIC/AVR/STM32 HEX editor, Multi-File load, SWD protocol with Flash Registers

Major changes:
- Complete HEX parsers (Intel HEX 8/16/32-bit, S-Record, BIN, PIC word sizes)
- Multi-File load system for ESP32/Automotive (add files with addresses, flash all)
- SWD protocol with device-specific Flash Registers (STM32/nRF/NXP/SAM)
- PIC full support (10F/12F=12-bit, 16F=14-bit, 18F=16-bit, 24F/30F/33F=24-bit)
- Device Info (getFullDeviceInfo) with memoryMap and Flash Registers from registry
- Load/Save with family-specific parsers/generators
- Blank Check button added
- Erase button moved to Operations section

Working:
- AVR: Load/Save/Display ✅
- PIC 12/14/16-bit: Load/Save/Display ✅
- PIC EEPROM/Config/ID: Load from HEX ✅
- STM32: Connect/IDCODE/Read Flash ✅
- nRF: Structure ready ✅
- NXP: Structure ready ✅
- SAM: Structure ready ✅

Known Issues:
- STM32 Erase not working (Flash Registers received but erase incomplete)
- STM32 Load in hex editor not displaying (parseHexSimple extAddr issue)
- PIC 24-bit (24F/30F/33F) display not tested
- PIC 12-bit (12F675) EEPROM not in HEX file (expected)

TODO:
- Fix STM32 erase (verify FLASH_CR write/read)
- Fix STM32 parseHexSimple for extAddr > 0xFFFF
- Test PIC 24-bit display
- Test nRF/NXP/SAM with real hardware
- Add automotive CAN/K-Line bootloaders
- Add SPI Flash page-by-page load for large flashes
- Add OTA update support
```



```
feat: تکمیل هگز ادیتور و پروتکل SWD

تغییرات اصلی:
- پارسرهای کامل HEX (Intel HEX 8/16/32-bit, S-Record, BIN, PIC)
- سیستم Multi-File برای ESP32/خودرویی
- پروتکل SWD با Flash Registers مخصوص هر دستگاه
- پشتیبانی کامل PIC (12/14/16/24-bit)
- Device Info با memoryMap از رجیستری

کار می‌کند:
- AVR: لود/ذخیره/نمایش ✅
- PIC 12/14/16-bit: لود/ذخیره/نمایش ✅
- STM32: اتصال/شناسایی/خواندن ✅

مشکلات:
- Erase برای STM32 کار نمی‌کند
- لود STM32 در هگز ادیتور مشکل دارد
- PIC 24-bit تست نشده

TODO:
- رفع مشکل Erase
- رفع مشکل لود STM32
- تست خانواده‌های دیگر
```

