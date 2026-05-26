import os
import tempfile
import shutil
import zipfile
import io
import threading
import subprocess
import webbrowser
import sys
import time
import socket

from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
from pypdf import PdfReader, PdfWriter
from scanner import load_pdf, extract_text_with_metadata, reconstruct_text
from security_auditor import SecurityAuditor

# ---------------------------------------------------------------------------
# Conversion Helpers
# ---------------------------------------------------------------------------

def get_libreoffice_path():
    paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def convert_with_libreoffice(input_path: str, output_path: str, out_ext: str, infilter: str = None) -> None:
    soffice = get_libreoffice_path()
    if not soffice:
        raise Exception("LibreOffice is not installed on this machine.")
        
    tmp_dir = os.path.dirname(input_path)
    cmd = [soffice, "--headless"]
    if infilter:
        cmd.append(f"--infilter={infilter}")
    cmd.extend(["--convert-to", out_ext, "--outdir", tmp_dir, input_path])

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise Exception(f"LibreOffice error: {res.stderr.decode('utf-8', errors='ignore')}")

    # LibreOffice saves the file with the same base name in tmp_dir
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    lo_output_path = os.path.join(tmp_dir, base_name + "." + out_ext)
    
    if os.path.exists(lo_output_path) and lo_output_path != output_path:
        shutil.move(lo_output_path, output_path)

def convert_pdf_to_docx(input_path: str, output_path: str, engine: str = "fast") -> None:
    """Convert a PDF to DOCX.

    engine:
      - "fast"    -> LibreOffice writer_pdf_import. Very fast, but the
                     output uses many text frames (one per line/word) and
                     keeps the original PDF page size/orientation.
      - "quality" -> pdf2docx. Reconstructs paragraph flow (real editable
                     text, fewer text boxes) but is significantly slower
                     and more memory-hungry on large PDFs.
    Each engine falls back to the other on failure.
    """
    if engine == "quality":
        try:
            from pdf2docx import Converter
            cv = Converter(input_path)
            try:
                cv.convert(output_path)
            finally:
                cv.close()
            return
        except Exception:
            convert_with_libreoffice(input_path, output_path, "docx", "writer_pdf_import")
            return

    # Default: fast / LibreOffice
    try:
        convert_with_libreoffice(input_path, output_path, "docx", "writer_pdf_import")
    except Exception:
        from pdf2docx import Converter
        cv = Converter(input_path)
        try:
            cv.convert(output_path)
        finally:
            cv.close()

def convert_docx_to_pdf(input_path: str, output_path: str) -> None:
    try:
        convert_with_libreoffice(input_path, output_path, "pdf")
    except:
        from docx2pdf import convert
        convert(input_path, output_path)

def convert_xlsx_to_pdf(input_path: str, output_path: str) -> None:
    convert_with_libreoffice(input_path, output_path, "pdf", "calc_pdf_Export")

def convert_pptx_to_pdf(input_path: str, output_path: str) -> None:
    convert_with_libreoffice(input_path, output_path, "pdf", "impress_pdf_Export")

def convert_image_to_pdf(input_path: str, output_path: str) -> None:
    image = Image.open(input_path)
    # Convert RGBA to RGB to save as PDF
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(output_path, "PDF", resolution=100.0)

def compress_pdf(input_path: str, output_path: str) -> None:
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
    # Remove metadata to save space
    writer.add_metadata({})
    with open(output_path, "wb") as f:
        writer.write(f)

def resize_image(input_path: str, output_path: str, mode: str = "percentage",
                 percent: int = 50, width: int = 0, height: int = 0) -> None:
    img = Image.open(input_path)
    if mode == "percentage":
        new_w = int(img.width * percent / 100)
        new_h = int(img.height * percent / 100)
    else:
        new_w = width or img.width
        new_h = height or img.height
    new_w = max(1, new_w)
    new_h = max(1, new_h)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    # Save with appropriate format
    ext = os.path.splitext(output_path)[1].lower()
    if ext in (".jpg", ".jpeg"):
        if resized.mode in ("RGBA", "P"):
            resized = resized.convert("RGB")
        resized.save(output_path, "JPEG", quality=85, optimize=True)
    else:
        resized.save(output_path, optimize=True)

def parse_page_ranges(ranges_text: str, page_count: int):
    if not ranges_text.strip():
        raise ValueError("Please enter at least one page or page range.")

    pages = []
    for raw_part in ranges_text.split(","):
        part = raw_part.strip()
        if not part:
            continue

        if "-" in part:
            bounds = [p.strip() for p in part.split("-", 1)]
            if len(bounds) != 2 or not bounds[0].isdigit() or not bounds[1].isdigit():
                raise ValueError(f"Invalid range '{part}'. Use examples like 10-24, 55-76, 88.")
            start, end = int(bounds[0]), int(bounds[1])
        else:
            if not part.isdigit():
                raise ValueError(f"Invalid page '{part}'.")
            start = end = int(part)

        if start < 1 or end < 1:
            raise ValueError("Page numbers must start at 1.")
        if start > end:
            raise ValueError(f"Range '{part}' is reversed.")
        if end > page_count:
            raise ValueError(f"Range '{part}' is outside this PDF's {page_count} pages.")

        pages.extend(range(start - 1, end))

    if not pages:
        raise ValueError("Please enter at least one valid page.")
    return pages

def parse_positive_int(value: str, default: int, field_name: str, minimum: int = 0, maximum: int = None) -> int:
    try:
        parsed = int(value or default)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number.")

    if parsed < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}.")
    if maximum is not None and parsed > maximum:
        raise ValueError(f"{field_name} must be at most {maximum}.")
    return parsed

# ---------------------------------------------------------------------------
# Flask App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)

TOOLS = {
    "pdf_to_word": {
        "exts": [".pdf"], "out_ext": ".docx", "fn": convert_pdf_to_docx, "type": "convert"
    },
    "word_to_pdf": {
        "exts": [".docx", ".doc"], "out_ext": ".pdf", "fn": convert_docx_to_pdf, "type": "convert"
    },
    "excel_to_pdf": {
        "exts": [".xlsx", ".xls"], "out_ext": ".pdf", "fn": convert_xlsx_to_pdf, "type": "convert"
    },
    "ppt_to_pdf": {
        "exts": [".pptx", ".ppt"], "out_ext": ".pdf", "fn": convert_pptx_to_pdf, "type": "convert"
    },
    "image_to_pdf": {
        "exts": [".jpg", ".jpeg", ".png"], "out_ext": ".pdf", "fn": convert_image_to_pdf, "type": "convert"
    },
    "merge_pdf": {
        "exts": [".pdf"], "out_ext": ".pdf", "type": "merge"
    },
    "split_pdf": {
        "exts": [".pdf"], "out_ext": ".pdf", "type": "split"
    },
    "protect_pdf": {
        "exts": [".pdf"], "out_ext": ".pdf", "type": "protect"
    },
    "rotate_pdf": {
        "exts": [".pdf"], "out_ext": ".pdf", "type": "rotate"
    },
    "remove_bg": {
        "exts": [".jpg", ".jpeg", ".png", ".webp"], "out_ext": ".png", "type": "remove_bg"
    },
    "compress_pdf": {
        "exts": [".pdf"], "out_ext": ".pdf", "fn": compress_pdf, "type": "compress"
    },
    "image_resize": {
        "exts": [".jpg", ".jpeg", ".png", ".webp"], "type": "image_resize"
    },
    "video_downloader": {
        "type": "download_link"
    },
    "prompt_auditor": {
        "exts": [".pdf"], "type": "audit"
    }
}

def schedule_cleanup(path: str, delay: float = 60.0):
    timer = threading.Timer(delay, lambda: shutil.rmtree(path, ignore_errors=True))
    timer.daemon = True
    timer.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )

@app.route("/api/<tool_id>", methods=["POST"])
def process_tool(tool_id):
    if tool_id not in TOOLS:
        return jsonify({"error": "Unknown tool"}), 400

    tool = TOOLS[tool_id]
    
    tmp_dir = tempfile.mkdtemp()
    errors = []
    converted_files = []

    # ---------------------------------------------------------
    # ACTION: DOWNLOAD LINK (yt-dlp)
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ACTION: AUDIT (Document Prompt Auditor)
    # ---------------------------------------------------------
    if tool["type"] == "audit":
        files = request.files.getlist("files")
        file = files[0] if files else None
        if not file or file.filename == "":
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return jsonify({"error": "No file uploaded."}), 400

        filename = secure_filename(file.filename)
        input_path = os.path.join(tmp_dir, filename)
        file.save(input_path)

        try:
            doc = load_pdf(input_path)
            metadata = {k: str(v) for k, v in doc.metadata.items() if v}
            reconstructed = reconstruct_text(doc)
            spans = extract_text_with_metadata(doc)

            auditor = SecurityAuditor()
            for span in spans:
                auditor.scan_visuals(span, span['page'])
                auditor.scan_unicode(span['text'], span['page'])
                auditor.scan_base64(span['text'], span['page'])

            warnings = auditor.warnings
            severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for w in warnings:
                sev = w.get("severity", "LOW")
                if sev in severity_counts:
                    severity_counts[sev] += 1

            score = 100
            score -= severity_counts["CRITICAL"] * 30
            score -= severity_counts["HIGH"] * 15
            score -= severity_counts["MEDIUM"] * 10
            score -= severity_counts["LOW"] * 5
            score = max(0, score)

            total_pages = len(doc)
            doc.close()
            shutil.rmtree(tmp_dir, ignore_errors=True)

            return jsonify({
                "filename": filename,
                "metadata": metadata,
                "reconstructed_text": reconstructed,
                "warnings": warnings,
                "severity_counts": severity_counts,
                "safety_score": score,
                "total_pages": total_pages
            })
        except Exception as e:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return jsonify({"error": f"Audit failed: {str(e)}"}), 500

    if tool["type"] == "download_link":
        link = request.form.get("link", "").strip()
        if not link:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return jsonify({"error": "No link provided."}), 400
            
        import yt_dlp
        
        ydl_opts = {
            'outtmpl': os.path.join(tmp_dir, '%(title)s.%(ext)s'),
            'format': 'best',
            'quiet': True,
            'no_warnings': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=True)
                downloaded_file = ydl.prepare_filename(info_dict)
                
            # If yt-dlp downloaded a different extension organically
            if not os.path.exists(downloaded_file):
                # fallback search in tmp_dir
                files = os.listdir(tmp_dir)
                if files:
                    downloaded_file = os.path.join(tmp_dir, files[0])
                else:
                    raise Exception("File not created by download process.")
                    
            schedule_cleanup(tmp_dir)
            return send_file(downloaded_file, as_attachment=True, download_name=os.path.basename(downloaded_file))
        except Exception as e:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return jsonify({"error": f"Failed to download from link: {str(e)}"}), 500

    # ---------------------------------------------------------
    # Actions below require files
    # ---------------------------------------------------------
    files = request.files.getlist("files")
    arg = request.form.get("arg", "")
    split_mode = request.form.get("split_mode", "pages")
    page_ranges = request.form.get("page_ranges", "")
    pdf_engine = request.form.get("pdf_engine", "fast")  # "fast" | "quality"
    
    if not files or all(f.filename == "" for f in files):
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return jsonify({"error": "No files uploaded."}), 400

    # ---------------------------------------------------------
    # ACTION: MERGE
    # ---------------------------------------------------------
    if tool["type"] == "merge":
        merger = PdfWriter()
        saved_paths = []
        for file in files:
            if file.filename == "": continue
            filename = secure_filename(file.filename)
            input_path = os.path.join(tmp_dir, filename)
            file.save(input_path)
            saved_paths.append(input_path)
        
        try:
            for path in saved_paths:
                merger.append(path)
            output_path = os.path.join(tmp_dir, "Merged_DocSwitch.pdf")
            merger.write(output_path)
            merger.close()
            
            schedule_cleanup(tmp_dir)
            return send_file(output_path, as_attachment=True, download_name="Merged_DocSwitch.pdf")
        except Exception as e:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return jsonify({"error": f"Merge failed: {str(e)}"}), 500

    # ---------------------------------------------------------
    # ACTION: SPLIT
    # ---------------------------------------------------------
    elif tool["type"] == "split":
        for file in files:
            if file.filename == "": continue
            filename = secure_filename(file.filename)
            input_path = os.path.join(tmp_dir, filename)
            file.save(input_path)
            
            base_name = os.path.splitext(filename)[0]
            try:
                reader = PdfReader(input_path)
                if split_mode == "ranges":
                    writer = PdfWriter()
                    for page_index in parse_page_ranges(page_ranges, len(reader.pages)):
                        writer.add_page(reader.pages[page_index])
                    out_name = f"{base_name}_ranges.pdf"
                    out_path = os.path.join(tmp_dir, out_name)
                    with open(out_path, "wb") as f:
                        writer.write(f)
                    converted_files.append((out_name, out_path))
                else:
                    for i, page in enumerate(reader.pages):
                        writer = PdfWriter()
                        writer.add_page(page)
                        out_name = f"{base_name}_page_{i+1}.pdf"
                        out_path = os.path.join(tmp_dir, out_name)
                        with open(out_path, "wb") as f:
                            writer.write(f)
                        converted_files.append((out_name, out_path))
            except Exception as e:
                errors.append(f"Split failed for '{filename}': {str(e)}")

    # ---------------------------------------------------------
    # ACTION: PROTECT
    # ---------------------------------------------------------
    elif tool["type"] == "protect":
        if not arg:
             shutil.rmtree(tmp_dir, ignore_errors=True)
             return jsonify({"error": "Password required for protection."}), 400
             
        for file in files:
            if file.filename == "": continue
            filename = secure_filename(file.filename)
            input_path = os.path.join(tmp_dir, filename)
            file.save(input_path)
            
            base_name = os.path.splitext(filename)[0]
            out_name = f"{base_name}_protected.pdf"
            out_path = os.path.join(tmp_dir, out_name)
            
            try:
                reader = PdfReader(input_path)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                writer.encrypt(arg)
                with open(out_path, "wb") as f:
                    writer.write(f)
                converted_files.append((out_name, out_path))
            except Exception as e:
                errors.append(f"Protect failed for '{filename}': {str(e)}")

    # ---------------------------------------------------------
    # ACTION: ROTATE
    # ---------------------------------------------------------
    elif tool["type"] == "rotate":
        for file in files:
            if file.filename == "": continue
            filename = secure_filename(file.filename)
            input_path = os.path.join(tmp_dir, filename)
            file.save(input_path)
            
            base_name = os.path.splitext(filename)[0]
            out_name = f"{base_name}_rotated.pdf"
            out_path = os.path.join(tmp_dir, out_name)
            
            try:
                reader = PdfReader(input_path)
                writer = PdfWriter()
                for page in reader.pages:
                    page.rotate(90)
                    writer.add_page(page)
                with open(out_path, "wb") as f:
                    writer.write(f)
                converted_files.append((out_name, out_path))
            except Exception as e:
                errors.append(f"Rotate failed for '{filename}': {str(e)}")

    # ---------------------------------------------------------
    # ACTION: REMOVE BACKGROUND
    # ---------------------------------------------------------
    elif tool["type"] == "remove_bg":
        from rembg import remove
        from PIL import Image
        for file in files:
            if file.filename == "": continue
            filename = secure_filename(file.filename)
            _, ext = os.path.splitext(filename)
            ext = ext.lower()

            if ext not in tool["exts"]:
                errors.append(f"Skipped '{filename}' (unsupported format for rembg).")
                continue

            input_path = os.path.join(tmp_dir, filename)
            file.save(input_path)
            
            base_name = os.path.splitext(filename)[0]
            out_name = f"{base_name}_nobg.png"
            out_path = os.path.join(tmp_dir, out_name)
            
            try:
                input_img = Image.open(input_path)
                output_img = remove(input_img)
                output_img.save(out_path)
                converted_files.append((out_name, out_path))
            except Exception as e:
                errors.append(f"Background removal failed for '{filename}': {str(e)}")

    # ---------------------------------------------------------
    # ACTION: COMPRESS PDF
    # ---------------------------------------------------------
    elif tool["type"] == "compress":
        for file in files:
            if file.filename == "": continue
            filename = secure_filename(file.filename)
            input_path = os.path.join(tmp_dir, filename)
            file.save(input_path)

            base_name = os.path.splitext(filename)[0]
            out_name = f"{base_name}_compressed.pdf"
            out_path = os.path.join(tmp_dir, out_name)

            try:
                compress_pdf(input_path, out_path)
                converted_files.append((out_name, out_path))
            except Exception as e:
                errors.append(f"Compress failed for '{filename}': {str(e)}")

    # ---------------------------------------------------------
    # ACTION: IMAGE RESIZE
    # ---------------------------------------------------------
    elif tool["type"] == "image_resize":
        resize_mode = request.form.get("resize_mode", "percentage")
        try:
            resize_pct = parse_positive_int(request.form.get("resize_percent", "50"), 50, "Resize percentage", 1, 500)
            resize_w = parse_positive_int(request.form.get("resize_width", "0"), 0, "Resize width", 0)
            resize_h = parse_positive_int(request.form.get("resize_height", "0"), 0, "Resize height", 0)
        except ValueError as e:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return jsonify({"error": str(e)}), 400

        if resize_mode == "dimensions" and not (resize_w or resize_h):
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return jsonify({"error": "Enter a width, a height, or both."}), 400

        for file in files:
            if file.filename == "": continue
            filename = secure_filename(file.filename)
            _, ext = os.path.splitext(filename)
            ext_lower = ext.lower()

            if ext_lower not in tool["exts"]:
                errors.append(f"Skipped '{filename}' (unsupported format).")
                continue

            input_path = os.path.join(tmp_dir, filename)
            file.save(input_path)

            base_name = os.path.splitext(filename)[0]
            out_name = f"{base_name}_resized{ext_lower}"
            out_path = os.path.join(tmp_dir, out_name)

            try:
                resize_image(input_path, out_path, mode=resize_mode,
                             percent=resize_pct, width=resize_w, height=resize_h)
                converted_files.append((out_name, out_path))
            except Exception as e:
                errors.append(f"Resize failed for '{filename}': {str(e)}")

    # ---------------------------------------------------------
    # ACTION: CONVERT (Default)
    # ---------------------------------------------------------
    else:
        out_ext = tool["out_ext"]
        for file in files:
            if file.filename == "": continue
            filename = secure_filename(file.filename)
            _, ext = os.path.splitext(filename)
            ext = ext.lower()

            if ext not in tool["exts"]:
                errors.append(f"Skipped '{filename}' (unsupported).")
                continue

            input_path = os.path.join(tmp_dir, filename)
            file.save(input_path)

            out_name = os.path.splitext(filename)[0] + out_ext
            output_path = os.path.join(tmp_dir, out_name)

            try:
                if tool_id == "pdf_to_word":
                    tool["fn"](input_path, output_path, engine=pdf_engine)
                else:
                    tool["fn"](input_path, output_path)
                converted_files.append((out_name, output_path))
            except Exception as e:
                errors.append(f"Failed '{filename}': {str(e)}")

    if not converted_files:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        msg = "No files converted. " + " | ".join(errors)
        return jsonify({"error": msg.strip()}), 400

    schedule_cleanup(tmp_dir)

    split_pages_as_zip = tool["type"] == "split" and split_mode != "ranges"

    # Return single file. Split-every-page always returns a zip, even for a
    # one-page PDF, so the saved file type stays predictable.
    if len(converted_files) == 1 and not split_pages_as_zip:
        name, path = converted_files[0]
        resp = send_file(path, as_attachment=True, download_name=name)
        if errors: resp.headers["X-Warnings"] = " | ".join(errors)
        return resp

    # Return zip of files
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, path in converted_files:
            zf.write(path, arcname=name)
    zip_buffer.seek(0)
    
    if len(files) == 1 and split_pages_as_zip:
        zip_name = f"{os.path.splitext(secure_filename(files[0].filename))[0]}_pages.zip"
    elif len(files) > 1:
        zip_name = f"DocSwitch_{tool_id}_batch.zip"
    else:
        zip_name = "DocSwitch_Converted.zip"

    resp = send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name=zip_name)
    if errors: resp.headers["X-Warnings"] = " | ".join(errors)
    return resp

DEFAULT_PORT = 5000


def is_port_available(port: int) -> bool:
    """Return True if no one is listening on the given local TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def wait_for_server(host: str, port: int, timeout: float = 15.0) -> bool:
    """Block until the local TCP port is accepting connections, or timeout.

    Uses a raw socket connect instead of an HTTP request so the Flask
    access log stays clean (no spurious 'GET /' entries on every launch).
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.3)
            if sock.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.1)
    return False


def find_edge_executable() -> str:
    """Locate msedge.exe; return absolute path or 'msedge' if discoverable via PATH."""
    candidate_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            return path
    # Fall back to PATH lookup (shutil.which avoids shell expansion surprises)
    found = shutil.which("msedge")
    return found or ""


def open_app_window(url: str, host: str, port: int) -> None:
    """Wait for the server, then open exactly one Edge --app window (or fall back)."""
    if not wait_for_server(host, port):
        # Server never came up; opening the browser will only show an error.
        return

    edge_path = find_edge_executable()
    if edge_path:
        # --new-window forces Edge to spawn a fresh standalone window even if
        # an Edge instance is already running, preventing the "two windows"
        # symptom seen when --app reuses an existing process.
        try:
            subprocess.Popen(
                [edge_path, "--new-window", f"--app={url}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except OSError:
            pass

    webbrowser.open(url)


def _print_port_in_use_message() -> None:
    print(
        f"[DocSwitch] Port {DEFAULT_PORT} is already in use. "
        "Another instance is probably still running - close it (or its "
        "Edge window) and try again.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    is_frozen = getattr(sys, "frozen", False)
    host = "127.0.0.1"
    url = f"http://{host}:{DEFAULT_PORT}"

    # Use a single, predictable port so re-launching can't create a second
    # parallel instance. The pre-check gives a friendly message in the common
    # case; the try/except below covers the race where another process binds
    # the port between our check and Flask's bind() call.
    if not is_port_available(DEFAULT_PORT):
        _print_port_in_use_message()
        sys.exit(1)

    threading.Thread(
        target=open_app_window, args=(url, host, DEFAULT_PORT), daemon=True
    ).start()

    # debug=False keeps everything in a single process (no Werkzeug reloader),
    # which matters because the reloader would otherwise spawn a child that
    # also tries to open an Edge window.
    try:
        app.run(debug=False, host=host, port=DEFAULT_PORT, use_reloader=False)
    except OSError as e:
        # WinError 10048 = WSAEADDRINUSE; errno 98 on Linux. Treat any "address
        # already in use" failure as a friendly exit, not a stack trace.
        win_in_use = getattr(e, "winerror", None) == 10048
        posix_in_use = e.errno in (48, 98)  # EADDRINUSE on macOS / Linux
        if win_in_use or posix_in_use or "Address already in use" in str(e):
            _print_port_in_use_message()
            sys.exit(1)
        raise
