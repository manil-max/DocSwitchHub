# 🔨 Build Instructions - DocSwitch Hub

Bu dosya geliştirici ve derleyiciler için kurulum ve yapılandırma talimatları içerir.

## 📋 Ön Gereksinimler

- **Windows 10/11** (64-bit)
- **Python 3.10+** (https://www.python.org/downloads/)
- **Inno Setup 6** (https://jrsoftware.org/isdl.php)
- **Git** (isteğe bağlı, ama önerilen)

## 🚀 Kurulum Adımları

### 1️⃣ **Geliştirme Ortamını Kur**

```bash
# Repository'i clone et
git clone https://github.com/manil-max/DocSwitchHub.git
cd "file converter"

# Virtual environment oluştur (önerilen)
python -m venv venv
venv\Scripts\activate

# Dependencies'i kur
pip install -r requirements.txt
```

### 2️⃣ **Uygulamayı Lokal Olarak Test Et**

```bash
# Flask sunucusunu başlat
python app.py

# Tarayıcıda aç: http://localhost:5000
```

### 3️⃣ **LibreOffice Kur** (İçin Dönüştürme Özellikleri)

```bash
# Windows Package Manager ile
winget install TheDocumentFoundation.LibreOffice

# Veya manual olarak
# https://www.libreoffice.org/download/download/
```

### 4️⃣ **Release Derle**

```bash
# Yönetici olarak PowerShell/CMD açın

# Derleme işlemini başlat
build_release.bat

# Bu script:
# 1. PyInstaller'ı kur
# 2. app.exe oluştur
# 3. Inno Setup installer'ını derle
```

**Çıktı:** `installer\Output\DocSwitchHub_Setup_v*.exe`

---

## 📦 Derleme Süreci Nedir?

### **Adım 1: PyInstaller (app.exe)**
```bash
pyinstaller --noconfirm build.spec
```
- `app.py` → `DocSwitch.exe` dönüştürür
- Tüm Python dependencies'i bundle eder
- Statik dosyaları (templates, static) dahil eder
- Sonuç: `dist/DocSwitch/` klasöründe

### **Adım 2: Inno Setup Installer**
```
AppFiles/ (PyInstaller output)
    ↓
setup.iss (Inno Setup script)
    ↓
DocSwitchHub_Setup_v1.0.2.exe
```

**Installer ne yapar?**
- ✅ Program Files'a kurur
- ✅ Start Menu'ye shortcut ekler
- ✅ Windows Search'te görünür hale getirir
- ✅ LibreOffice indir linkini sunar
- ✅ Uninstall seçeneği ekler

---

## 🔧 Manuel Derleme (Eğer build_release.bat çalışmazsa)

### **PyInstaller Kullan:**
```bash
# build.spec'i güncelle (gerekirse)
pyinstaller --noconfirm build.spec

# dist/DocSwitch klasöründen installer/AppFiles'a kopyala
xcopy "dist\DocSwitch" "installer\AppFiles\" /E /I /Y
```

### **Inno Setup ile Derle:**
1. Inno Setup Studio'yu aç
2. `installer/setup.iss` dosyasını yükle
3. **Build** → **Compile** tıkla
4. Çıktı: `installer/Output/DocSwitchHub_Setup_v*.exe`

---

## 📂 Proje Yapısı

```
file converter/
├── app.py                      # Ana Flask uygulaması
├── build.spec                  # PyInstaller konfigürasyonu
├── build_release.bat           # Derleme script'i
├── requirements.txt            # Python dependencies
├── static/
│   ├── script.js
│   └── style.css
├── templates/
│   └── index.html
├── installer/
│   ├── setup.iss               # Inno Setup script
│   ├── output/                 # Derlenmiş installer çıkacak
│   └── AppFiles/               # PyInstaller output (otomatik oluşturulur)
└── README.md
```

---

## ✅ Sorun Giderme

### **"PyInstaller not found" hatası**
```bash
pip install pyinstaller
```

### **"ISCC.exe not found" hatası**
- Inno Setup 6'nın düzgün kurulduğunu kontrol et
- Inno Setup'ı tekrar kur: https://jrsoftware.org/isdl.php

### **"LibreOffice not installed" uyarısı**
- Bu beklenen davranış! Installer, kullanıcıya LibreOffice'i indirme seçeneği sunar

### **app.exe'de icon görmüyor**
- `docswitch_hub.ico` dosyasının proje kökünde olduğundan emin ol
- `build.spec`'de icon path'ı kontrol et

---

## 🚢 Release Sürümü Yayınla

1. **build_release.bat** çalıştır → `setup*.exe` oluşur
2. **GitHub Releases** → **New Release** tıkla
3. **installer/Output/DocSwitchHub_Setup_v*.exe**'i yükle
4. Release notes yaz ve yayınla

---

## 📝 Versiyon Güncelle

**setup.iss içinde:**
```
#define MyAppVersion "1.0.2"
```

**build_release.bat'de versyon otomatik okunur.**

---

## 💡 İpuçları

- **Debug mode:** `app.py`'de Flask debug'ı aç: `app.run(debug=True)`
- **Smaller .exe:** `build.spec`'de `upx=True` ayarı yapılmışsa daha küçük
- **Fast rebuild:** Sadece `pyinstaller build.spec` çalıştır, build_release.bat'a ihtiyaç yok
- **Test installer:** `installer\Output\DocSwitchHub_Setup_v*.exe`'i başka bilgisayarında test et

---

## 📞 Destek

Sorun mu yaşıyorsun?
- GitHub Issues: https://github.com/manil-max/DocSwitchHub/issues
- README.md'yi kontrol et
- Trace'i kontrol et: `build_release.bat` koş ve hata mesajını kopyala

---

**Versiyon:** 1.0.2  
**Güncelleme:** May 2026
