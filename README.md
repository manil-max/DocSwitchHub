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

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** installed
- **LibreOffice** installed (required for Office document conversions)
  ```bash
  winget install TheDocumentFoundation.LibreOffice
  ```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/DocSwitchHub.git
   cd DocSwitchHub
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

## 🖥️ Desktop App Mode (Optional)

Want it to feel like a native desktop application? Double-click `RunDocSwitch.vbs` — it silently starts the server and opens the app in Microsoft Edge's App Mode (frameless window).

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
