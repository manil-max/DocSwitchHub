<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows-blue?style=for-the-badge&logo=windows" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" />
</p>

<h1 align="center">🔄 DocSwitch Hub</h1>
<p align="center"><b>Replace your paid subscriptions. 100% offline tools for documents, media, and downloads.</b></p>
<p align="center">An all-in-one local document & media processing suite that works completely offline — no uploads, no ads, no file limits.</p>

---

## ✨ Features

### 📄 Document Tools
| Tool | Description |
|------|-------------|
| **PDF → Word** | Convert PDF to editable DOCX (ultra-fast via LibreOffice) |
| **Word → PDF** | Convert DOCX/DOC to PDF |
| **Excel → PDF** | Convert XLSX/XLS spreadsheets to PDF |
| **PowerPoint → PDF** | Convert PPTX/PPT presentations to PDF |
| **Image → PDF** | Convert JPG/PNG images to PDF |
| **Merge PDF** | Combine multiple PDFs into one |
| **Split PDF** | Extract every page into individual PDF files |
| **Protect PDF** | Lock PDFs with a password |
| **Rotate PDF** | Rotate all pages 90° clockwise |

### 🎨 Media Tools
| Tool | Description |
|------|-------------|
| **Background Remover** | AI-powered background removal from images (local model, no internet needed) |

### 📥 Download Tools
| Tool | Description |
|------|-------------|
| **Video Downloader** | Download videos from YouTube and other sites — no ads, high quality |

---

## 🚀 Quick Start - Two Options

### **Option 1: One-Click Installer (Recommended for Most Users)** ⭐

**No Python knowledge needed. Just download and run!**

1. **Download** the latest installer from [Releases](https://github.com/manil-max/DocSwitchHub/releases)
2. **Double-click** `DocSwitchHub_Setup_v*.exe`
3. **Click "Install"** → Done! ✅
4. Find **DocSwitch Hub** in:
   - **Start Menu** (search "DocSwitch")
   - **Desktop shortcut** (if you selected it)
   - **Windows Search** (just type "DocSwitch")

**One requirement:** LibreOffice (installer will prompt you to download it)

---

### **Option 2: Manual Installation (For Developers)**

**Want to modify the code or run from source?**

#### Prerequisites
- **Python 3.10+** installed ([Download](https://www.python.org/downloads/))
- **LibreOffice** installed for document conversions
  ```bash
  winget install TheDocumentFoundation.LibreOffice
  ```

#### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/manil-max/DocSwitchHub.git
   cd "file converter"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

5. **Open in browser**
   Navigate to `http://127.0.0.1:5000`

---

## 🏗️ Building the Installer (For Developers)

Want to compile your own installer? See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

```bash
build_release.bat
# Creates: installer\Output\DocSwitchHub_Setup_v*.exe
```

---

## 🖥️ Desktop App Mode

When you run DocSwitch Hub from the installer, it automatically:
- ✅ Opens in Microsoft Edge's App Mode (frameless window)
- ✅ Appears in your Taskbar as a native app
- ✅ Runs silently in the background
- ✅ Shows up in Windows Search

---

## 📂 Project Structure

```
DocSwitchHub/
├── app.py              # Flask backend with all tool logic
├── requirements.txt    # Python dependencies
├── RunDocSwitch.vbs    # Silent launcher for desktop mode
├── static/
│   ├── style.css       # Premium SaaS-style UI
│   └── script.js       # Frontend interactivity & API calls
├── templates/
│   └── index.html      # Dashboard with sidebar navigation
├── LICENSE
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-tool`)
3. Commit your changes (`git commit -m 'Add amazing tool'`)
4. Push to the branch (`git push origin feature/amazing-tool`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>⭐ Star this repo if you found it useful!</b>
</p>
