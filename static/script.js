/**
 * DocSwitch Suite – Frontend Scripts
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
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

  const progressSection = document.getElementById("progressSection");
  const progressFill = document.getElementById("progressFill");
  const progressText = document.getElementById("progressText");
  const successSection = document.getElementById("successSection");
  const startOverBtn = document.getElementById("startOverBtn");
  const warningsText = document.getElementById("warningsText");
  const errorSection = document.getElementById("errorSection");
  const errorText = document.getElementById("errorText");
  const retryBtn = document.getElementById("retryBtn");

  const sidebarItems = document.querySelectorAll(".sidebar__item");

  // State
  let currentToolId = null;
  let acceptedExts = "";
  let currentToolArg = null;
  let currentInputType = "file";
  let selectedFiles = [];

  // --- Sidebar & Dashboard ---
  sidebarItems.forEach(item => {
    item.addEventListener("click", () => {
      sidebarItems.forEach(i => i.classList.remove("active"));
      item.classList.add("active");
      
      const filter = item.dataset.filter;
      let visibleCount = 0;
      toolCards.forEach(card => {
        if (filter === "all" || card.dataset.category === filter) {
          card.style.display = "block";
          visibleCount++;
        } else {
          card.style.display = "none";
        }
      });
      goHome();
    });
  });

  // --- Views ---
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
    if(arg === "password") {
      toolArgInput.classList.remove("hidden");
      toolArgInput.value = "";
      toolArgInput.placeholder = "Enter password to protect PDF...";
    } else {
      toolArgInput.classList.add("hidden");
    }

    if(toolId === "merge_pdf") actionBtnLabel.textContent = "Merge PDF";
    else if(toolId === "split_pdf") actionBtnLabel.textContent = "Split PDF";
    else actionBtnLabel.textContent = "Convert";

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

  // --- File Handling ---
  function showSection(sec) {
    [dropzone, linkzone, fileList, progressSection, successSection, errorSection].forEach(s => s.classList.add("hidden"));
    if (sec) sec.classList.remove("hidden");
  }

  function resetState() {
    selectedFiles = [];
    fileInput.value = "";
    fileInputMore.value = "";
    linkInput.value = "";
    if (toolArgInput) toolArgInput.value = "";
    
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
    fileCount.textContent = selectedFiles.length;
    fileListItems.innerHTML = "";

    selectedFiles.forEach((file, idx) => {
      const el = document.createElement("div");
      el.className = "file-item";
      el.innerHTML = `
        <div>
          <div class="file-item__name">${file.name}</div>
          <div class="file-item__size">${formatSize(file.size)}</div>
        </div>
        <button class="file-item__remove" data-index="${idx}">✕</button>
      `;
      fileListItems.appendChild(el);
    });

    fileListItems.querySelectorAll(".file-item__remove").forEach(btn => {
      btn.addEventListener("click", () => {
        selectedFiles.splice(parseInt(btn.dataset.index), 1);
        renderFiles();
      });
    });
  }

  function handleAddFiles(files) {
    const validRaw = acceptedExts.split(",").map(e => e.trim().toLowerCase());
    for (const f of files) {
      const ext = "." + f.name.split(".").pop().toLowerCase();
      if (validRaw.includes(ext) || acceptedExts === "") {
        if (!selectedFiles.some(sel => sel.name === f.name && sel.size === f.size)) {
          selectedFiles.push(f);
        }
      }
    }
    if (selectedFiles.length > 0) renderFiles();
    else alert("Invalid file type dropped.");
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
  clearAllBtn.addEventListener("click", resetState);

  // --- API Action ---
  convertBtn.addEventListener("click", async () => {
    if (!currentToolId || selectedFiles.length === 0) return;
    if (currentToolArg === "password" && !toolArgInput.value) {
      alert("Please enter a password.");
      return;
    }

    showSection(progressSection);
    progressFill.style.width = "0%";
    progressText.textContent = "Uploading assets...";

    let fakeProg = 0;
    const progInt = setInterval(() => {
      fakeProg = Math.min(fakeProg + Math.random()*15, 85);
      progressFill.style.width = `${fakeProg}%`;
      if(fakeProg > 40) progressText.textContent = "Processing documents...";
    }, 500);

    const fd = new FormData();
    selectedFiles.forEach(f => fd.append("files", f));
    if (currentToolArg) {
      fd.append("arg", toolArgInput.value);
    }

    try {
      const res = await fetch(`/api/${currentToolId}`, { method: "POST", body: fd });
      clearInterval(progInt);
      
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.error || "Action failed.");
      }

      progressFill.style.width = "100%";
      progressText.textContent = "Done!";

      const disp = res.headers.get("Content-Disposition");
      let dName = "DocSwitch_File";
      if (disp) {
        const m = disp.match(/filename\*?=(?:UTF-8''|"?)([^";]+)/i);
        if (m) dName = decodeURIComponent(m[1]);
      }

      const blob = await res.blob();
      
      try {
        // Try to use the modern File System Access API to prompt "Save As"
        if (window.showSaveFilePicker) {
          const handle = await window.showSaveFilePicker({
            suggestedName: dName
          });
          const writable = await handle.createWritable();
          await writable.write(blob);
          await writable.close();
        } else {
          throw new Error("showSaveFilePicker not supported");
        }
      } catch (saveErr) {
        // Fallback to traditional download if API is not supported or user cancels
        if (saveErr.name !== 'AbortError') {
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = dName;
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(url);
        } else {
          // User clicked Cancel on the Save As dialog
          progressText.textContent = "Saved canceled.";
          setTimeout(() => resetState(), 1000);
          return;
        }
      }

      const warns = res.headers.get("X-Warnings");
      if (warns) {
        warningsText.textContent = "⚠ " + warns;
        warningsText.classList.remove("hidden");
      }

      setTimeout(() => showSection(successSection), 500);

    } catch (err) {
      clearInterval(progInt);
      errorText.textContent = err.message;
      showSection(errorSection);
    }
  });

  convertLinkBtn.addEventListener("click", async () => {
    if (!currentToolId || !linkInput.value.trim()) return;

    showSection(progressSection);
    progressFill.style.width = "0%";
    progressText.textContent = "Downloading and processing media...";

    let fakeProg = 0;
    const progInt = setInterval(() => {
      fakeProg = Math.min(fakeProg + Math.random()*15, 85);
      progressFill.style.width = `${fakeProg}%`;
    }, 500);

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
      progressText.textContent = "Done!";

      const disp = res.headers.get("Content-Disposition");
      let dName = "DocSwitch_Download";
      if (disp) {
        const m = disp.match(/filename\*?=(?:UTF-8''|"?)([^";]+)/i);
        if (m) dName = decodeURIComponent(m[1]);
      }

      const blob = await res.blob();
      
      try {
        if (window.showSaveFilePicker) {
          const handle = await window.showSaveFilePicker({ suggestedName: dName });
          const writable = await handle.createWritable();
          await writable.write(blob);
          await writable.close();
        } else {
          throw new Error("showSaveFilePicker not supported");
        }
      } catch (saveErr) {
        if (saveErr.name !== 'AbortError') {
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = dName;
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(url);
        } else {
          progressText.textContent = "Saved canceled.";
          setTimeout(() => resetState(), 1000);
          return;
        }
      }

      setTimeout(() => showSection(successSection), 500);

    } catch (err) {
      clearInterval(progInt);
      errorText.textContent = err.message;
      showSection(errorSection);
    }
  });

  startOverBtn.addEventListener("click", resetState);
  retryBtn.addEventListener("click", resetState);
});
