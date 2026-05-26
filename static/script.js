/**
 * DocSwitch Hub – Frontend Scripts
 * Features: Dark mode, toast notifications, keyboard shortcuts,
 *           conversion history, file type hints, new tools support
 */

document.addEventListener("DOMContentLoaded", () => {
  const sendAppHeartbeat = () => {
    fetch("/api/heartbeat", {
      method: "POST",
      keepalive: true
    }).catch(() => {});
  };
  sendAppHeartbeat();
  setInterval(sendAppHeartbeat, 5000);
  window.addEventListener("pagehide", () => {
    navigator.sendBeacon("/api/shutdown", new Blob([], { type: "text/plain" }));
  });

  // ─── Elements ──────────────────────────────────────────────
  const dashboardView = document.getElementById("dashboardView");
  const toolView = document.getElementById("toolView");
  const homeLogo = document.getElementById("homeLogo");
  const toolCards = document.querySelectorAll(".tool-card");
  
  const backBtn = document.getElementById("backBtn");
  const activeToolTitle = document.getElementById("activeToolTitle");
  const browseBtn = document.getElementById("browseBtn");
  const fileInput = document.getElementById("fileInput");
  const dropzone = document.getElementById("dropzone");
  
  const linkzone = document.getElementById("linkzone");
  const linkInput = document.getElementById("linkInput");
  const convertLinkBtn = document.getElementById("convertLinkBtn");

  const fileList = document.getElementById("fileList");
  const fileListItems = document.getElementById("fileListItems");
  const fileCount = document.getElementById("fileCount");
  const clearAllBtn = document.getElementById("clearAllBtn");
  
  const fileInputMore = document.getElementById("fileInputMore");
  const addMoreBtn = document.getElementById("addMoreBtn");
  const convertBtn = document.getElementById("convertBtn");
  const actionBtnLabel = document.getElementById("actionBtnLabel");
  const toolArgInput = document.getElementById("toolArgInput");
  const splitOptions = document.getElementById("splitOptions");
  const pageRangesInput = document.getElementById("pageRangesInput");
  const resizeOptions = document.getElementById("resizeOptions");
  const pdfEngineOptions = document.getElementById("pdfEngineOptions");

  const progressSection = document.getElementById("progressSection");
  const progressFill = document.getElementById("progressFill");
  const progressText = document.getElementById("progressText");
  const successSection = document.getElementById("successSection");
  const startOverBtn = document.getElementById("startOverBtn");
  const warningsText = document.getElementById("warningsText");
  const sizeComparison = document.getElementById("sizeComparison");
  const errorSection = document.getElementById("errorSection");
  const errorText = document.getElementById("errorText");
  const retryBtn = document.getElementById("retryBtn");

  const sidebarItems = document.querySelectorAll(".sidebar__item");
  const themeToggle = document.getElementById("themeToggle");
  const hamburgerBtn = document.getElementById("hamburgerBtn");
  const sidebar = document.getElementById("sidebar");
  const sidebarOverlay = document.getElementById("sidebarOverlay");
  const toastContainer = document.getElementById("toastContainer");
  const historySection = document.getElementById("historySection");
  const historyList = document.getElementById("historyList");

  // Audit Results elements
  const auditResults = document.getElementById("auditResults");
  const auditDocName = document.getElementById("auditDocName");
  const auditGaugeCircle = document.getElementById("auditGaugeCircle");
  const auditGaugeValue = document.getElementById("auditGaugeValue");
  const auditGaugeLabel = document.getElementById("auditGaugeLabel");
  const auditCountCritical = document.getElementById("auditCountCritical");
  const auditCountHigh = document.getElementById("auditCountHigh");
  const auditCountMedium = document.getElementById("auditCountMedium");
  const auditCountLow = document.getElementById("auditCountLow");
  const auditMetaPages = document.getElementById("auditMetaPages");
  const auditMetaAuthor = document.getElementById("auditMetaAuthor");
  const auditMetaCreator = document.getElementById("auditMetaCreator");
  const auditMetaProducer = document.getElementById("auditMetaProducer");
  const auditWarningCount = document.getElementById("auditWarningCount");
  const auditAccordion = document.getElementById("auditAccordion");
  const auditCleanMsg = document.getElementById("auditCleanMsg");
  const auditCharCount = document.getElementById("auditCharCount");
  const auditTextPre = document.getElementById("auditTextPre");
  const auditTabThreats = document.getElementById("auditTabThreats");
  const auditTabText = document.getElementById("auditTabText");
  const auditPanelThreats = document.getElementById("auditPanelThreats");
  const auditPanelText = document.getElementById("auditPanelText");
  const auditCopyBtn = document.getElementById("auditCopyBtn");
  const auditDownloadBtn = document.getElementById("auditDownloadBtn");
  const auditStartOver = document.getElementById("auditStartOver");

  // ─── State ─────────────────────────────────────────────────
  let currentToolId = null;
  let acceptedExts = "";
  let currentToolArg = null;
  let currentInputType = "file";
  let selectedFiles = [];
  let auditScannedText = "";
  let auditScannedFilename = "";

  // ─── Theme Toggle ──────────────────────────────────────────
  function getPreferredTheme() {
    const stored = localStorage.getItem("docswitch-theme");
    if (stored) return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("docswitch-theme", theme);
  }

  applyTheme(getPreferredTheme());

  themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    showToast(next === "dark" ? "🌙 Dark mode enabled" : "☀️ Light mode enabled", "info");
  });

  // System theme change listener
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
    if (!localStorage.getItem("docswitch-theme")) {
      applyTheme(e.matches ? "dark" : "light");
    }
  });

  // ─── Hamburger Menu ────────────────────────────────────────
  hamburgerBtn.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    sidebarOverlay.classList.toggle("active");
  });
  sidebarOverlay.addEventListener("click", () => {
    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("active");
  });

  // ─── Toast Notifications ──────────────────────────────────
  function showToast(message, type = "info", duration = 3000) {
    const toast = document.createElement("div");
    toast.className = `toast toast--${type}`;
    
    const icons = {
      success: "✅", error: "❌", warning: "⚠️", info: "ℹ️"
    };
    toast.innerHTML = `<span>${icons[type] || ""}</span><span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.classList.add("fade-out");
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  // ─── Conversion History ───────────────────────────────────
  function getHistory() {
    try {
      return JSON.parse(localStorage.getItem("docswitch-history") || "[]");
    } catch { return []; }
  }

  function addToHistory(toolId, fileCount, fileName) {
    const history = getHistory();
    history.unshift({
      tool: toolId,
      files: fileCount,
      name: fileName,
      time: new Date().toISOString()
    });
    // Keep only last 20
    if (history.length > 20) history.length = 20;
    localStorage.setItem("docswitch-history", JSON.stringify(history));
    renderHistory();
  }

  function renderHistory() {
    const history = getHistory();
    if (history.length === 0) {
      historySection.classList.add("hidden");
      return;
    }
    historySection.classList.remove("hidden");
    historyList.innerHTML = "";

    const toolNames = {
      pdf_to_word: "PDF → Word",
      word_to_pdf: "Word → PDF",
      excel_to_pdf: "Excel → PDF",
      ppt_to_pdf: "PPT → PDF",
      image_to_pdf: "Image → PDF",
      merge_pdf: "Merge PDF",
      split_pdf: "Split PDF",
      compress_pdf: "Compress PDF",
      protect_pdf: "Protect PDF",
      rotate_pdf: "Rotate PDF",
      remove_bg: "Remove BG",
      image_resize: "Image Resize",
      video_downloader: "Video Download",
      prompt_auditor: "Prompt Audit"
    };

    history.slice(0, 8).forEach(item => {
      const el = document.createElement("div");
      el.className = "history-item";
      const date = new Date(item.time);
      const timeStr = date.toLocaleDateString() + " " + date.toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});
      el.innerHTML = `
        <span class="history-item__tool">${toolNames[item.tool] || item.tool}</span>
        <span class="history-item__files">${item.name || item.files + " file(s)"}</span>
        <span class="history-item__time">${timeStr}</span>
      `;
      historyList.appendChild(el);
    });
  }

  renderHistory();

  // ─── Sidebar & Dashboard ──────────────────────────────────
  sidebarItems.forEach(item => {
    item.addEventListener("click", () => {
      sidebarItems.forEach(i => i.classList.remove("active"));
      item.classList.add("active");
      
      const filter = item.dataset.filter;
      toolCards.forEach(card => {
        if (filter === "all" || card.dataset.category === filter) {
          card.style.display = "block";
        } else {
          card.style.display = "none";
        }
      });
      goHome();
      // Close mobile sidebar
      sidebar.classList.remove("open");
      sidebarOverlay.classList.remove("active");
    });
  });

  // ─── Views ────────────────────────────────────────────────
  function goHome() {
    dashboardView.classList.remove("hidden");
    toolView.classList.add("hidden");
    resetState();
  }

  function openTool(toolId, title, exts, arg, inputType) {
    currentToolId = toolId;
    activeToolTitle.textContent = title;
    acceptedExts = exts || "";
    currentToolArg = arg;
    currentInputType = inputType || "file";
    
    fileInput.accept = acceptedExts;
    fileInputMore.accept = acceptedExts;

    // Show argument input if tool needs it
    if (arg === "password") {
      toolArgInput.classList.remove("hidden");
      toolArgInput.value = "";
      toolArgInput.placeholder = "Enter password to protect PDF...";
    } else {
      toolArgInput.classList.add("hidden");
    }

    // Set action button label
    const btnLabels = {
      merge_pdf: "Merge PDF",
      split_pdf: "Split PDF",
      compress_pdf: "Compress PDF",
      protect_pdf: "Protect PDF",
      rotate_pdf: "Rotate PDF",
      remove_bg: "Remove Background",
      image_resize: "Resize Image",
      prompt_auditor: "Scan Document"
    };
    actionBtnLabel.textContent = btnLabels[toolId] || "Convert";

    dashboardView.classList.add("hidden");
    toolView.classList.remove("hidden");
    resetState();
  }

  homeLogo.addEventListener("click", goHome);
  backBtn.addEventListener("click", goHome);

  toolCards.forEach(card => {
    card.addEventListener("click", () => {
      openTool(
        card.dataset.tool, 
        card.querySelector(".tool-card__title").textContent, 
        card.dataset.ext, 
        card.dataset.arg, 
        card.dataset.inputtype
      );
    });
  });

  // ─── File Handling ────────────────────────────────────────
  function showSection(sec) {
    [dropzone, linkzone, fileList, progressSection, successSection, errorSection, auditResults].forEach(s => s.classList.add("hidden"));
    if (sec) sec.classList.remove("hidden");
  }

  function resetState() {
    selectedFiles = [];
    fileInput.value = "";
    fileInputMore.value = "";
    linkInput.value = "";
    if (toolArgInput) toolArgInput.value = "";
    if (splitOptions) splitOptions.classList.add("hidden");
    if (resizeOptions) resizeOptions.classList.add("hidden");
    if (pdfEngineOptions) pdfEngineOptions.classList.add("hidden");
    if (pageRangesInput) {
      pageRangesInput.value = "";
      pageRangesInput.classList.add("hidden");
    }
    document.querySelectorAll('input[name="splitMode"]').forEach(input => {
      input.checked = input.value === "pages";
    });
    if (sizeComparison) {
      sizeComparison.classList.add("hidden");
      sizeComparison.innerHTML = "";
    }
    
    if (currentInputType === "link") {
      showSection(linkzone);
    } else {
      showSection(dropzone);
    }
    
    warningsText.classList.add("hidden");
  }

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  }

  function renderFiles() {
    if (selectedFiles.length === 0) {
      resetState();
      return;
    }
    
    showSection(fileList);
    if (splitOptions) splitOptions.classList.toggle("hidden", currentToolId !== "split_pdf");
    if (resizeOptions) resizeOptions.classList.toggle("hidden", currentToolId !== "image_resize");
    if (pdfEngineOptions) pdfEngineOptions.classList.toggle("hidden", currentToolId !== "pdf_to_word");
    fileCount.textContent = selectedFiles.length;
    fileListItems.innerHTML = "";

    // Show total size
    const totalSize = selectedFiles.reduce((sum, f) => sum + f.size, 0);

    selectedFiles.forEach((file, idx) => {
      const el = document.createElement("div");
      el.className = "file-item";
      el.style.animationDelay = `${idx * 0.05}s`;
      el.innerHTML = `
        <div>
          <div class="file-item__name">${file.name}</div>
          <div class="file-item__size">${formatSize(file.size)}</div>
        </div>
        <button class="file-item__remove" data-index="${idx}" title="Remove file">✕</button>
      `;
      fileListItems.appendChild(el);
    });

    fileListItems.querySelectorAll(".file-item__remove").forEach(btn => {
      btn.addEventListener("click", () => {
        const idx = parseInt(btn.dataset.index);
        const removed = selectedFiles[idx].name;
        selectedFiles.splice(idx, 1);
        showToast(`Removed ${removed}`, "info", 2000);
        renderFiles();
      });
    });
  }

  function handleAddFiles(files) {
    const validRaw = acceptedExts.split(",").map(e => e.trim().toLowerCase());
    let addedCount = 0;
    for (const f of files) {
      const ext = "." + f.name.split(".").pop().toLowerCase();
      if (validRaw.includes(ext) || acceptedExts === "") {
        if (!selectedFiles.some(sel => sel.name === f.name && sel.size === f.size)) {
          selectedFiles.push(f);
          addedCount++;
        }
      }
    }
    if (addedCount > 0) {
      renderFiles();
      showToast(`${addedCount} file(s) added`, "success", 2000);
    } else {
      showToast("Invalid file type. Please select a supported format.", "error");
    }
  }

  // Browse Dropzone
  browseBtn.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", () => handleAddFiles(fileInput.files));
  
  dropzone.addEventListener("dragover", e => { e.preventDefault(); dropzone.classList.add("dragover"); });
  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
  dropzone.addEventListener("drop", e => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if(e.dataTransfer.files.length) handleAddFiles(e.dataTransfer.files);
  });

  // Browse FileList
  addMoreBtn.addEventListener("click", () => fileInputMore.click());
  fileInputMore.addEventListener("change", () => handleAddFiles(fileInputMore.files));
  clearAllBtn.addEventListener("click", () => {
    resetState();
    showToast("All files cleared", "info", 2000);
  });

  // ─── Split Mode ───────────────────────────────────────────
  function getSelectedSplitMode() {
    return document.querySelector('input[name="splitMode"]:checked')?.value || "pages";
  }

  document.querySelectorAll('input[name="splitMode"]').forEach(input => {
    input.addEventListener("change", () => {
      if (!pageRangesInput) return;
      pageRangesInput.classList.toggle("hidden", getSelectedSplitMode() !== "ranges");
    });
  });

  // ─── Resize Mode ──────────────────────────────────────────
  const resizePercent = document.getElementById("resizePercent");
  const resizeDimensions = document.getElementById("resizeDimensions");

  document.querySelectorAll('input[name="resizeMode"]').forEach(input => {
    input.addEventListener("change", () => {
      const mode = document.querySelector('input[name="resizeMode"]:checked')?.value;
      if (mode === "percentage") {
        resizePercent.classList.remove("hidden");
        resizeDimensions.classList.add("hidden");
      } else {
        resizePercent.classList.add("hidden");
        resizeDimensions.classList.remove("hidden");
      }
    });
  });

  // ─── Output Helpers ───────────────────────────────────────
  function getOutputExtension(toolId, inputFiles) {
    if (toolId === "merge_pdf") return ".pdf";
    if (inputFiles && inputFiles.length > 1) return ".zip";
    if (toolId === "split_pdf") return getSelectedSplitMode() === "ranges" ? ".pdf" : ".zip";
    if (toolId === "pdf_to_word") return ".docx";
    if (toolId === "compress_pdf") return ".pdf";
    if (toolId === "image_resize") return ".zip";
    if (toolId.includes("to_pdf") || toolId.includes("_pdf")) return ".pdf";
    if (toolId === "remove_bg") return ".png";
    if (toolId === "video_downloader") return ".mp4";
    return "";
  }
  
  function getSuggestedName(toolId, inputFiles) {
    let base = "DocSwitch_Output";
    if (inputFiles && inputFiles.length > 0) {
      if (inputFiles.length === 1) {
        let name = inputFiles[0].name;
        base = name.substring(0, name.lastIndexOf('.')) || name;
        if (toolId === "protect_pdf") base += "_protected";
        if (toolId === "rotate_pdf") base += "_rotated";
        if (toolId === "remove_bg") base += "_nobg";
        if (toolId === "compress_pdf") base += "_compressed";
        if (toolId === "image_resize") base += "_resized";
        if (toolId === "split_pdf") base += getSelectedSplitMode() === "ranges" ? "_ranges" : "_pages";
      } else {
        base = `DocSwitch_${toolId}_batch`;
        if (toolId === "merge_pdf") base = "Merged_Document";
      }
    } else if (toolId === "video_downloader") {
      base = "Video_Download";
    }
    return base + getOutputExtension(toolId, inputFiles);
  }

  function getSavePickerOptions(suggestedName) {
    const ext = "." + suggestedName.split(".").pop().toLowerCase();
    const typeMap = {
      ".zip": { description: "ZIP archive", accept: { "application/zip": [".zip"] } },
      ".pdf": { description: "PDF document", accept: { "application/pdf": [".pdf"] } },
      ".docx": { description: "Word document", accept: { "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"] } },
      ".png": { description: "PNG image", accept: { "image/png": [".png"] } },
      ".jpg": { description: "JPEG image", accept: { "image/jpeg": [".jpg", ".jpeg"] } },
      ".mp4": { description: "MP4 video", accept: { "video/mp4": [".mp4"] } }
    };
    const type = typeMap[ext];
    return type ? { suggestedName, types: [type] } : { suggestedName };
  }

  // ─── Download Helpers ─────────────────────────────────────
  function triggerFallbackDownload(blob, dName) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = dName;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  // ─── Convert Action ──────────────────────────────────────
  convertBtn.addEventListener("click", async () => {
    if (!currentToolId || selectedFiles.length === 0) return;

    // Audit tool uses a different flow (JSON response, not file download)
    if (currentToolId === "prompt_auditor") {
      runAuditScan();
      return;
    }

    if (currentToolArg === "password" && !toolArgInput.value) {
      showToast("Please enter a password.", "warning");
      return;
    }
    if (currentToolId === "split_pdf" && getSelectedSplitMode() === "ranges" && !pageRangesInput.value.trim()) {
      showToast("Please enter page ranges, e.g. 10-24, 55-76, 88", "warning");
      return;
    }

    // Track input file sizes for comparison
    const inputTotalSize = selectedFiles.reduce((sum, f) => sum + f.size, 0);

    const sName = getSuggestedName(currentToolId, selectedFiles);
    let fileHandle = null;

    // Prompt user for save location IMMEDIATELY while user gesture is active
    if (window.showSaveFilePicker) {
      try {
        fileHandle = await window.showSaveFilePicker(getSavePickerOptions(sName));
      } catch (err) {
        if (err.name === 'AbortError') return;
        console.warn("Save picker failed, will fallback.", err);
      }
    }

    showSection(progressSection);
    progressFill.style.width = "0%";
    progressText.textContent = "Uploading files...";

    let fakeProg = 0;
    const progInt = setInterval(() => {
      fakeProg = Math.min(fakeProg + Math.random()*12, 85);
      progressFill.style.width = `${fakeProg}%`;
      if (fakeProg > 30) progressText.textContent = "Processing... This may take a moment.";
      if (fakeProg > 60) progressText.textContent = "Almost done...";
    }, 500);

    const fd = new FormData();
    selectedFiles.forEach(f => fd.append("files", f));
    if (currentToolArg) {
      fd.append("arg", toolArgInput.value);
    }
    if (currentToolId === "split_pdf") {
      fd.append("split_mode", getSelectedSplitMode());
      fd.append("page_ranges", pageRangesInput.value.trim());
    }
    if (currentToolId === "pdf_to_word") {
      const engine = document.querySelector('input[name="pdfEngine"]:checked')?.value || "fast";
      fd.append("pdf_engine", engine);
    }
    if (currentToolId === "image_resize") {
      const mode = document.querySelector('input[name="resizeMode"]:checked')?.value || "percentage";
      fd.append("resize_mode", mode);
      if (mode === "percentage") {
        fd.append("resize_percent", resizePercent.value || "50");
      } else {
        fd.append("resize_width", document.getElementById("resizeWidth").value || "");
        fd.append("resize_height", document.getElementById("resizeHeight").value || "");
      }
    }

    try {
      const res = await fetch(`/api/${currentToolId}`, { method: "POST", body: fd });
      clearInterval(progInt);
      
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.error || "Action failed.");
      }

      progressFill.style.width = "100%";
      progressText.textContent = "Saving file...";

      const disp = res.headers.get("Content-Disposition");
      let finalName = sName;
      if (disp) {
        const m = disp.match(/filename\*?=(?:UTF-8''|"?)([^";]+)/i);
        if (m) finalName = decodeURIComponent(m[1]);
      }

      const blob = await res.blob();
      
      if (fileHandle) {
        try {
          const writable = await fileHandle.createWritable();
          await writable.write(blob);
          await writable.close();
        } catch (err) {
          triggerFallbackDownload(blob, finalName);
        }
      } else {
        triggerFallbackDownload(blob, finalName);
      }

      // Show size comparison for compress tool
      if (currentToolId === "compress_pdf" || currentToolId === "image_resize") {
        const saved = inputTotalSize - blob.size;
        const pct = ((saved / inputTotalSize) * 100).toFixed(1);
        if (saved > 0) {
          sizeComparison.classList.remove("hidden");
          sizeComparison.innerHTML = `
            <strong>📊 Size Comparison:</strong><br>
            Before: ${formatSize(inputTotalSize)} → After: ${formatSize(blob.size)}<br>
            <span style="color:var(--clr-success); font-weight:700;">Saved ${formatSize(saved)} (${pct}% smaller)</span>
          `;
        }
      }

      const warns = res.headers.get("X-Warnings");
      if (warns) {
        warningsText.textContent = "⚠ " + warns;
        warningsText.classList.remove("hidden");
      }

      // Record history
      const firstFileName = selectedFiles.length === 1 ? selectedFiles[0].name : `${selectedFiles.length} files`;
      addToHistory(currentToolId, selectedFiles.length, firstFileName);

      showToast("File saved successfully!", "success");
      setTimeout(() => showSection(successSection), 500);

    } catch (err) {
      clearInterval(progInt);
      errorText.textContent = err.message;
      showSection(errorSection);
      showToast(err.message, "error", 5000);
    }
  });

  // ─── Audit Convert Flow ──────────────────────────────────
  function runAuditScan() {
    if (!currentToolId || selectedFiles.length === 0) return;

    showSection(progressSection);
    progressFill.style.width = "0%";
    progressText.textContent = "Analyzing document structures...";

    let fakeProg = 0;
    const progInt = setInterval(() => {
      fakeProg = Math.min(fakeProg + Math.random() * 10, 85);
      progressFill.style.width = `${fakeProg}%`;
      if (fakeProg > 30) progressText.textContent = "Running security auditors (Unicode & Base64)...";
      if (fakeProg > 60) progressText.textContent = "Compiling security report...";
    }, 400);

    const fd = new FormData();
    selectedFiles.forEach(f => fd.append("files", f));

    fetch(`/api/${currentToolId}`, { method: "POST", body: fd })
      .then(async res => {
        clearInterval(progInt);
        if (!res.ok) {
          const d = await res.json();
          throw new Error(d.error || "Audit failed.");
        }
        progressFill.style.width = "100%";
        progressText.textContent = "Report ready!";
        return res.json();
      })
      .then(data => {
        setTimeout(() => {
          renderAuditResults(data);
          showSection(auditResults);
          addToHistory(currentToolId, 1, data.filename);
          showToast(data.safety_score >= 100 ? "Document is 100% clean!" : "Security scan complete — review findings.", data.safety_score >= 100 ? "success" : "warning");
        }, 500);
      })
      .catch(err => {
        clearInterval(progInt);
        errorText.textContent = err.message;
        showSection(errorSection);
        showToast(err.message, "error", 5000);
      });
  }

  // ─── Render Audit Results ────────────────────────────────
  function escapeHtml(text) {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function renderAuditResults(data) {
    auditScannedText = data.reconstructed_text;
    auditScannedFilename = data.filename;

    // Header
    auditDocName.textContent = data.filename;

    // Gauge
    const score = data.safety_score;
    auditGaugeValue.textContent = `${score}%`;
    const circumference = 2 * Math.PI * 42; // ~263.89
    const offset = circumference * (1 - score / 100);
    auditGaugeCircle.style.strokeDasharray = `${circumference}`;
    auditGaugeCircle.style.strokeDashoffset = `${offset}`;

    // Color based on score
    let gaugeColor = "#10b981"; // green
    let statusText = "SECURE";
    if (score < 50) {
      gaugeColor = "#ef4444";
      statusText = "DANGEROUS";
    } else if (score < 100) {
      gaugeColor = "#f59e0b";
      statusText = "RISK DETECTED";
    }
    auditGaugeCircle.style.stroke = gaugeColor;
    auditGaugeLabel.textContent = statusText;
    auditGaugeLabel.style.color = gaugeColor;
    auditGaugeValue.style.color = gaugeColor;

    // Severity counts
    auditCountCritical.textContent = data.severity_counts.CRITICAL;
    auditCountHigh.textContent = data.severity_counts.HIGH;
    auditCountMedium.textContent = data.severity_counts.MEDIUM;
    auditCountLow.textContent = data.severity_counts.LOW;

    // Metadata
    auditMetaPages.textContent = data.total_pages;
    auditMetaAuthor.textContent = data.metadata.Author || "\u2014";
    auditMetaCreator.textContent = data.metadata.Creator || "\u2014";
    auditMetaProducer.textContent = data.metadata.Producer || "\u2014";

    // Warnings
    auditWarningCount.textContent = data.warnings.length;
    auditAccordion.innerHTML = "";

    if (data.warnings.length === 0) {
      auditCleanMsg.classList.remove("hidden");
      auditAccordion.classList.add("hidden");
    } else {
      auditCleanMsg.classList.add("hidden");
      auditAccordion.classList.remove("hidden");

      const priority = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
      const sorted = [...data.warnings].sort((a, b) => priority[a.severity] - priority[b.severity]);

      sorted.forEach(w => {
        let ctx = escapeHtml(w.context);
        // Highlight special tokens
        ctx = ctx.replace(/\[ZWSP\]/g, '<span class="audit-token audit-token--zwsp">[ZWSP]</span>');
        ctx = ctx.replace(/\[ZWNJ\]/g, '<span class="audit-token audit-token--zwnj">[ZWNJ]</span>');
        ctx = ctx.replace(/\[ZWJ\]/g, '<span class="audit-token audit-token--zwj">[ZWJ]</span>');
        ctx = ctx.replace(/\[BOM\]/g, '<span class="audit-token audit-token--bom">[BOM]</span>');
        ctx = ctx.replace(/\[LRM\]/g, '<span class="audit-token audit-token--lrm">[LRM]</span>');
        ctx = ctx.replace(/\[RLM\]/g, '<span class="audit-token audit-token--rlm">[RLM]</span>');

        const item = document.createElement("div");
        item.className = `audit-accordion-item audit-accordion--${w.severity.toLowerCase()}`;
        item.innerHTML = `
          <div class="audit-accordion__header">
            <div style="display:flex;align-items:center;gap:0.5rem;flex:1;min-width:0;">
              <span class="audit-badge audit-badge--${w.severity.toLowerCase()}">${w.severity}</span>
              <span class="audit-accordion__rule">${w.rule}</span>
            </div>
            <span class="audit-accordion__page">Page ${w.page}</span>
            <svg class="audit-accordion__arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
          </div>
          <div class="audit-accordion__body">
            <p class="audit-accordion__msg">${w.message}</p>
            <div class="audit-accordion__ctx-label">Detected Context</div>
            <div class="audit-accordion__ctx">${ctx}</div>
          </div>
        `;

        const header = item.querySelector(".audit-accordion__header");
        header.addEventListener("click", () => {
          const isOpen = item.classList.contains("open");
          auditAccordion.querySelectorAll(".audit-accordion-item").forEach(o => o.classList.remove("open"));
          if (!isOpen) item.classList.add("open");
        });

        auditAccordion.appendChild(item);
      });
    }

    // Extracted text
    auditCharCount.textContent = auditScannedText.length;
    auditTextPre.textContent = auditScannedText;

    // Default tab
    switchAuditTab("threats");
  }

  // ─── Audit Tab Switching ─────────────────────────────────
  function switchAuditTab(tab) {
    auditTabThreats.classList.toggle("active", tab === "threats");
    auditTabText.classList.toggle("active", tab === "text");
    auditPanelThreats.classList.toggle("active", tab === "threats");
    auditPanelText.classList.toggle("active", tab === "text");
  }
  auditTabThreats.addEventListener("click", () => switchAuditTab("threats"));
  auditTabText.addEventListener("click", () => switchAuditTab("text"));

  // ─── Audit Utilities ────────────────────────────────────
  auditCopyBtn.addEventListener("click", () => {
    if (!auditScannedText) return;
    navigator.clipboard.writeText(auditScannedText).then(() => {
      showToast("Text copied to clipboard!", "success", 2000);
    }).catch(() => showToast("Copy failed.", "error"));
  });

  auditDownloadBtn.addEventListener("click", () => {
    if (!auditScannedText) return;
    const blob = new Blob([auditScannedText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${auditScannedFilename.replace(/\.pdf$/i, "")}_extracted.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    showToast("Text file download started.", "success", 2000);
  });

  auditStartOver.addEventListener("click", resetState);

  // ─── Link Download ───────────────────────────────────────
  convertLinkBtn.addEventListener("click", async () => {
    if (!currentToolId || !linkInput.value.trim()) return;

    const sName = getSuggestedName(currentToolId, null);
    let fileHandle = null;

    if (window.showSaveFilePicker) {
      try {
        fileHandle = await window.showSaveFilePicker(getSavePickerOptions(sName));
      } catch (err) {
        if (err.name === 'AbortError') return;
        console.warn("Save picker failed, will fallback.", err);
      }
    }

    showSection(progressSection);
    progressFill.style.width = "0%";
    progressText.textContent = "Downloading and processing media...";

    let fakeProg = 0;
    const progInt = setInterval(() => {
      fakeProg = Math.min(fakeProg + Math.random()*10, 85);
      progressFill.style.width = `${fakeProg}%`;
    }, 600);

    const fd = new FormData();
    fd.append("link", linkInput.value.trim());

    try {
      const res = await fetch(`/api/${currentToolId}`, { method: "POST", body: fd });
      clearInterval(progInt);
      
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.error || "Action failed.");
      }

      progressFill.style.width = "100%";
      progressText.textContent = "Saving file...";

      const disp = res.headers.get("Content-Disposition");
      let finalName = sName;
      if (disp) {
        const m = disp.match(/filename\*?=(?:UTF-8''|"?)([^";]+)/i);
        if (m) finalName = decodeURIComponent(m[1]);
      }

      const blob = await res.blob();
      
      if (fileHandle) {
        try {
          const writable = await fileHandle.createWritable();
          await writable.write(blob);
          await writable.close();
        } catch (err) {
          triggerFallbackDownload(blob, finalName);
        }
      } else {
        triggerFallbackDownload(blob, finalName);
      }

      addToHistory(currentToolId, 1, linkInput.value.trim().substring(0, 40));
      showToast("Download complete!", "success");
      setTimeout(() => showSection(successSection), 500);

    } catch (err) {
      clearInterval(progInt);
      errorText.textContent = err.message;
      showSection(errorSection);
      showToast(err.message, "error", 5000);
    }
  });

  // ─── Navigation Buttons ───────────────────────────────────
  startOverBtn.addEventListener("click", resetState);
  retryBtn.addEventListener("click", resetState);

  // ─── Keyboard Shortcuts ───────────────────────────────────
  document.addEventListener("keydown", (e) => {
    // Escape -> go back to home
    if (e.key === "Escape" && !dashboardView.classList.contains("hidden") === false) {
      goHome();
    }
    // Ctrl+O -> open file browser (when in tool view)
    if ((e.ctrlKey || e.metaKey) && e.key === "o") {
      e.preventDefault();
      if (!toolView.classList.contains("hidden")) {
        if (currentInputType === "link") return;
        if (!dropzone.classList.contains("hidden")) {
          fileInput.click();
        } else if (!fileList.classList.contains("hidden")) {
          fileInputMore.click();
        }
      }
    }
  });
});
