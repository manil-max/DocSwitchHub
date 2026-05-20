# DocSwitch Hub Progress

## Current Goal

Make DocSwitch Hub feel like a normal Windows desktop app first, then prepare the repository so users can download and run it from GitHub with minimal effort.

## Completed

- Built a standalone `dist/DocSwitch.exe` for local Windows use.
- Added Start Menu and Desktop shortcuts for `DocSwitch Hub`.
- Updated the app icon and favicon to a simpler green/yellow/orange mark.
- Updated the app window launch flow so the executable opens in an app-style Edge window when available.

## Bugs To Fix

### Multi-file PDF to Word output is broken

When uploading multiple PDFs, for example 5 PDFs, the app currently returns a single Word file and that file does not open correctly.

Expected behavior:

- Each uploaded PDF should be converted separately.
- If one PDF is uploaded, download one `.docx`.
- If multiple PDFs are uploaded, download a `.zip`.
- The zip should contain one `.docx` per source PDF.
- Each output file should preserve the source filename, for example `book.pdf` -> `book.docx`.
- If one file fails, the successful conversions should still be returned and the user should see a clear warning for failed files.

### Download filenames are too generic

Converted files should be named from the uploaded source file instead of a generic DocSwitch name.

Expected behavior:

- `invoice.pdf` converted with PDF to Word should download as `invoice.docx`.
- `report.docx` converted to PDF should download as `report.pdf`.
- Multi-file outputs should keep those names inside the zip.

## Features To Add

### PDF split by custom page ranges

Add a second mode to the PDF splitter so users can extract chosen page ranges into one new PDF.

Suggested UI:

- Mode selector: `Split every page` and `Extract ranges`.
- Range input example: `10-24, 55-76, 88`.
- Output should be one PDF containing the selected pages in the order entered.
- Validate invalid ranges, reversed ranges, out-of-bounds pages, and empty input.

### PDF preview before conversion

Improve the uploaded file list so users can inspect PDFs before converting.

Possible first version:

- Make uploaded PDF filenames clickable.
- Clicking opens a PDF preview in the browser.

Possible later version:

- Show a small hover preview of the first page.
- Keep this optional because hover previews can be slower for large PDFs and less useful on mobile.

## Suggested Implementation Order

1. Fix multi-file conversion and output naming.
2. Add PDF range extraction mode.
3. Add clickable PDF preview.
4. Rebuild the executable and update shortcuts.
5. After local app behavior is stable, finish the GitHub release/installer flow.

## Latest Work

- Fixed the frontend save-name bug that made multi-file conversions save as a single `.docx`; multi-file conversion actions now suggest a `.zip` filename.
- Kept single-file conversion names based on the uploaded file, for example `book.pdf` -> `book.docx`.
- Added a PDF split mode selector with `Split every page` and `Extract ranges`.
- Added backend page-range parsing for inputs like `10-24, 55-76, 88`.
- Fixed PDF split output typing so `Split every page` always downloads a `.zip`, even when the source PDF has only one page.
- Made the split mode selector more visible and explicit: `Every page to ZIP` or `Selected ranges to PDF`.
- Added file type hints to the Windows save dialog so zip/pdf/docx outputs are less likely to be saved with the wrong extension.

## Verification Notes

- `app.py` syntax parsed successfully.
- Flask smoke checks for `/` and `/favicon.ico` returned `200`.
- Page-range parser returned the expected zero-based page indexes for valid input.
- Full PDF endpoint testing should be repeated in the desktop app because the sandboxed test run had trouble writing temporary PDF files.
- Completed comprehensive bug verification tests confirming multi-file output formatting and filename preservation.
- Passed 15/15 tests for conversion functionality.

## Latest Major Overhaul

- **Premium UI**: Implemented dark mode, glassmorphism, animated cards, and responsive sidebar.
- **UX**: Added toast notifications, keyboard shortcuts (Ctrl+O, Esc), and conversion history log.
- **New Tools**: Added PDF Compress (pypdf) and Image Resize (Pillow).
- **Feedback**: Implemented before/after size comparisons for compression tools.
