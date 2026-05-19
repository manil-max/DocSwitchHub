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

def convert_pdf_to_docx(input_path: str, output_path: str) -> None:
    try:
        convert_with_libreoffice(input_path, output_path, "docx", "writer_pdf_import")
    except Exception as e:
        # Fallback
        from pdf2docx import Converter
        cv = Converter(input_path)
        cv.convert(output_path)
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
    "video_downloader": {
        "type": "download_link"
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
                tool["fn"](input_path, output_path)
                converted_files.append((out_name, output_path))
            except Exception as e:
                errors.append(f"Failed '{filename}': {str(e)}")

    if not converted_files:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        msg = "No files converted. " + " | ".join(errors)
        return jsonify({"error": msg.strip()}), 400

    schedule_cleanup(tmp_dir)

    # Return single file
    if len(converted_files) == 1:
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
    
    if len(files) == 1 and tool["type"] == "split" and split_mode != "ranges":
        zip_name = f"{os.path.splitext(secure_filename(files[0].filename))[0]}_pages.zip"
    elif len(files) > 1:
        zip_name = f"DocSwitch_{tool_id}_batch.zip"
    else:
        zip_name = "DocSwitch_Converted.zip"

    resp = send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name=zip_name)
    if errors: resp.headers["X-Warnings"] = " | ".join(errors)
    return resp

def is_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def find_available_port(start_port: int = 5000) -> int:
    for port in range(start_port, start_port + 50):
        if is_port_available(port):
            return port
    raise RuntimeError("No available local port found for DocSwitch.")


def open_app_window(url: str) -> None:
    time.sleep(2)

    edge_commands = [
        ["msedge", f"--app={url}"],
        [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            f"--app={url}",
        ],
        [
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            f"--app={url}",
        ],
    ]

    for command in edge_commands:
        try:
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except OSError:
            continue

    webbrowser.open(url)


if __name__ == "__main__":
    # Detect if running as PyInstaller executable
    is_frozen = getattr(sys, 'frozen', False)
    port = find_available_port(5000)
    url = f"http://127.0.0.1:{port}"

    threading.Thread(target=open_app_window, args=(url,), daemon=True).start()

    if is_frozen:
        # Running as compiled executable - open in desktop-app style and suppress debug output
        app.run(debug=False, port=port)
    else:
        # Running from source - development mode
        app.run(debug=True, port=port)
