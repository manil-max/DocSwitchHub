import re
import base64

class SecurityAuditor:
    """
    Security Auditor engine that passive-scans extracted PDF elements 
    for hidden prompt injections, invisible characters, base64 payloads, 
    and suspicious visual layouts.
    """
    
    def __init__(self):
        # We will keep a list of found warnings/logs.
        self.warnings = []

    def scan_unicode(self, text, page_num):
        """Scans for zero-width Unicode characters (invisible tokens)."""
        # Match invisible and bidirectional formatting characters
        invisible_chars = re.findall(r'[\u200b\u200c\u200d\ufeff\u200e\u200f\u202a-\u202e]', text)
        if invisible_chars:
            # Create a highlightable representation for previewing
            highlighted = text
            replacements = {
                '\u200b': '[ZWSP]',
                '\u200c': '[ZWNJ]',
                '\u200d': '[ZWJ]',
                '\ufeff': '[BOM]',
                '\u200e': '[LRM]',
                '\u200f': '[RLM]',
            }
            for char, placeholder in replacements.items():
                highlighted = highlighted.replace(char, placeholder)
            
            # Catch remaining bidi characters if any
            for code in range(0x202a, 0x202f):
                char = chr(code)
                highlighted = highlighted.replace(char, f"[BIDI_0x{code:x}]")

            warning = {
                "page": page_num,
                "rule": "Unicode Invisible Characters",
                "severity": "HIGH",
                "message": f"Detected {len(invisible_chars)} invisible zero-width or formatting characters.",
                "context": highlighted.strip()
            }
            self.warnings.append(warning)
            return warning
        return None

    def scan_base64(self, text, page_num):
        """Scans for suspicious Base64 encoded string blocks."""
        # Regex to find candidate Base64 blocks: at least 12 alphanumeric/plus/slash characters
        candidates = re.findall(r'\b[A-Za-z0-9+/]{12,}={0,2}\b', text)
        found_warnings = []
        for candidate in candidates:
            # Skip candidates that look like plain numbers or plain text words
            if candidate.isdigit() or len(set(candidate)) < 4:
                continue
            
            # Check if it decodes to valid UTF-8 printable text
            try:
                # Add required padding if needed
                padded_candidate = candidate
                missing_padding = len(candidate) % 4
                if missing_padding:
                    padded_candidate += '=' * (4 - missing_padding)
                
                decoded_bytes = base64.b64decode(padded_candidate)
                decoded_text = decoded_bytes.decode('utf-8', errors='strict')
                
                # Check ratio of printable characters
                if len(decoded_text) > 4:
                    printable_chars = sum(1 for c in decoded_text if c.isprintable() or c in '\r\n\t')
                    ratio = printable_chars / len(decoded_text)
                    
                    if ratio > 0.85:
                        warning = {
                            "page": page_num,
                            "rule": "Suspicious Base64 Payload",
                            "severity": "MEDIUM",
                            "message": f"Detected Base64 block decoding to: '{decoded_text.strip()}'",
                            "context": f"Encoded: {candidate}"
                        }
                        self.warnings.append(warning)
                        found_warnings.append(warning)
            except Exception:
                pass
        return found_warnings if found_warnings else None

    def scan_visuals(self, span, page_num):
        """Flags text blocks where font size is too small or matches background color."""
        text = span.get("text", "").strip()
        if not text:
            return None

        size = span.get("size", 0.0)
        color_int = span.get("color", 0)
        
        # Deconstruct RGB channels
        r = (color_int >> 16) & 255
        g = (color_int >> 8) & 255
        b = color_int & 255

        warnings_found = []

        # Check A: Tiny Font Size (< 6pt)
        if size < 6.0:
            warning = {
                "page": page_num,
                "rule": "Tiny Font Trap",
                "severity": "HIGH",
                "message": f"Detected tiny text (size: {size:.2f}pt).",
                "context": f"Text: '{text}'"
            }
            self.warnings.append(warning)
            warnings_found.append(warning)

        # Check B: Text color matches typical white background (r, g, b all > 240)
        # Note: If text is white, r=255, g=255, b=255.
        if r > 240 and g > 240 and b > 240:
            warning = {
                "page": page_num,
                "rule": "Invisible Text Trap",
                "severity": "CRITICAL",
                "message": f"Detected text rendered in white/off-white color (RGB: {r},{g},{b}).",
                "context": f"Text: '{text}'"
            }
            self.warnings.append(warning)
            warnings_found.append(warning)

        return warnings_found if warnings_found else None
